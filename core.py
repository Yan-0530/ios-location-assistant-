"""GeoShift backend. Raw device output is transient and never enters logs."""
from __future__ import annotations
import ipaddress
import json
import math
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request

VERSION = '11.63.1'
PRESETS = {
    '日本': {'东京': (35.6812, 139.7671), '大阪': (34.6937, 135.5023)},
    '美国': {'洛杉矶': (34.0528, -118.2516), '纽约': (40.7128, -74.0060)},
    '中国': {'北京': (39.9042, 116.4074), '上海': (31.2304, 121.4737)},
    '英国': {'伦敦': (51.5074, -0.1278)},
    '法国': {'巴黎': (48.8566, 2.3522)},
    '澳大利亚': {'悉尼': (-33.8688, 151.2093)},
    '自定义': {'自定义坐标': (0.0, 0.0)},
}

def redact(text):
    text = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', str(text))
    text = re.sub(r'(?i)([A-Z]:\\Users\\)[^\\\r\n]+', r'\1[USER]', text)
    text = re.sub(r'(?i)\b[0-9a-f]{8}-[0-9a-f]{16}\b|\b[0-9a-f]{40}\b|\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b', '[DEVICE]', text)
    text = re.sub(r'(?i)([\"\x27]?(?:Identifier|UniqueDeviceID|UDID|SerialNumber|DeviceName|ECID|IMEI2?|MEID|ICCID|IMSI|PhoneNumber|UniqueChipID|WiFiAddress|BluetoothAddress|ComputerName|HostName)[\"\x27]?\s*[:=]\s*)[^\r\n,}]+', r'\1[REDACTED]', text)
    text = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP]', text)
    text = re.sub(r'(?i)\b(?:[0-9a-f]{0,4}:){2,}[0-9a-f:]+(?:%\w+)?', '[IP]', text)
    text = re.sub(r'(?i)\b(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}\b', '[MAC]', text)
    return text

def coordinates(lat, lon):
    a, b = float(lat), float(lon)
    if not math.isfinite(a) or not math.isfinite(b) or not -90 <= a <= 90 or not -180 <= b <= 180:
        raise ValueError('纬度须为 -90～90，经度须为 -180～180，且必须为有限数值。')
    return a, b

def runtime_default():
    if not getattr(sys, 'frozen', False):
        p = Path(sys.executable)
        return str(p.with_name('python.exe') if p.name.lower() == 'pythonw.exe' else p)
    for candidate in [shutil.which('python'), *Path(os.environ.get('LOCALAPPDATA', '.')).glob('Python/pythoncore-3.14-*/python.exe')]:
        if candidate and Path(candidate).is_file() and 'WindowsApps' not in str(candidate):
            return str(candidate)
    return ''

def clean_env():
    # Do not inherit target/transport overrides or frozen-app Python search paths.
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith(('PYMOBILEDEVICE3_', 'PYTHON', '_PYI')) and k.upper() != 'USBMUXD_SOCKET_ADDRESS'}
    env.update(PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONUNBUFFERED='1', NO_COLOR='1', TERM='dumb')
    if getattr(sys, 'frozen', False) and os.name == 'nt':
        import ctypes
        ctypes.windll.kernel32.SetDllDirectoryW(None)
    return env

class ProcessJob:
    """Windows closes this handle on app termination, killing owned backend children."""
    def __init__(self):
        self.handle = None
        if os.name != 'nt': return
        import ctypes as c
        from ctypes import wintypes as w
        class Basic(c.Structure):
            _fields_ = [('PerProcessUserTimeLimit',c.c_longlong), ('PerJobUserTimeLimit',c.c_longlong),
                ('LimitFlags',w.DWORD), ('MinimumWorkingSetSize',c.c_size_t), ('MaximumWorkingSetSize',c.c_size_t),
                ('ActiveProcessLimit',w.DWORD), ('Affinity',c.c_size_t), ('PriorityClass',w.DWORD), ('SchedulingClass',w.DWORD)]
        class IO(c.Structure):
            _fields_ = [(name,c.c_ulonglong) for name in ['ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount']]
        class Extended(c.Structure):
            _fields_ = [('BasicLimitInformation',Basic), ('IoInfo',IO), ('ProcessMemoryLimit',c.c_size_t),
                ('JobMemoryLimit',c.c_size_t), ('PeakProcessMemoryUsed',c.c_size_t), ('PeakJobMemoryUsed',c.c_size_t)]
        self.kernel = c.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes = [c.c_void_p,w.LPCWSTR]
        self.kernel.CreateJobObjectW.restype = w.HANDLE
        self.kernel.SetInformationJobObject.argtypes = [w.HANDLE,c.c_int,c.c_void_p,w.DWORD]
        self.kernel.AssignProcessToJobObject.argtypes = [w.HANDLE,w.HANDLE]
        self.kernel.CloseHandle.argtypes = [w.HANDLE]
        info = Extended(); info.BasicLimitInformation.LimitFlags = 0x2000
        handle = self.kernel.CreateJobObjectW(None,None)
        if not handle or not self.kernel.SetInformationJobObject(handle,9,c.byref(info),c.sizeof(info)):
            if handle: self.kernel.CloseHandle(handle)
            raise RuntimeError('无法建立 Windows 后台进程保护。请在普通桌面会话中运行。')
        self.handle = handle

    def assign(self,p):
        if self.handle and not self.kernel.AssignProcessToJobObject(self.handle,int(p._handle)):
            p.kill(); p.wait()
            raise RuntimeError('无法将后台进程加入生命周期保护，操作已停止。')

    def __del__(self):
        if getattr(self,'handle',None):
            self.kernel.CloseHandle(self.handle)
            self.handle = None

def error_summary(output, code):
    # Allowlisted descriptions only; never echo third-party messages/tracebacks.
    choices = [
        (('password', 'passcode'), '手机设有密码，请在设置 → 隐私与安全性 → 开发者模式中手动启用。'),
        (('devicemodelocked', 'passwordprotected', 'device is locked'), '请解锁手机后重试。'),
        (('notpaired', 'pairingdialog', 'userdeniedpairing', 'invalidhostid'), '请解锁手机，确认“信任此电脑”，然后重试。'),
        (('developermode', 'developer mode'), '请确认手机开发者模式已启用，并完成重启后的确认。'),
        (('no device', 'nodevice', 'connectionrefused', 'muxexception'), '未能连接 USB 设备。请检查数据线、Apple Devices 驱动和信任状态。'),
        (('modulenotfound', 'no module named'), '依赖缺失，请安装隔离环境。'),
        (('invalidservice', 'imagemounter', 'developer disk', 'ddi'), '开发者服务或开发者镜像不可用。请检查手机版本、开发者模式及官方镜像挂载指引。'),
        (('tunnel', 'remotexpc', 'rsd'), '开发者隧道失败。请重新连接 USB、解锁手机并运行隧道诊断。'),
        (('ssl', 'certificate', 'connectionerror', 'could not find a version', 'no matching distribution'), '下载或依赖安装失败，请检查网络、证书及 Python 兼容性。'),
    ]
    lower = output.lower()
    for needles, message in choices:
        if any(n in lower for n in needles):
            return f'{message}（退出码 {code}）'
    return f'命令失败（退出码 {code}）。原始输出未保存，以免泄露设备信息；请检查连接、信任和依赖后重试。'

class Runner:
    def __init__(self):
        self.lock = threading.Lock()
        self.active = None
        self.cancelled = threading.Event()
        self.job = ProcessJob()

    def spawn(self, argv):
        p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding='utf-8', errors='replace', env=clean_env(),
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        self.job.assign(p)
        return p

    @staticmethod
    def kill(p):
        if p.poll() is None:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(p.pid), '/T', '/F'], stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                p.kill()
            p.wait(timeout=10)

    def cancel(self):
        self.cancelled.set()
        with self.lock:
            if self.active:
                self.kill(self.active)

    def run(self, argv, timeout=40, check=True):
        if self.cancelled.is_set():
            raise RuntimeError('操作已取消。')
        with self.lock:
            if self.cancelled.is_set():
                raise RuntimeError('操作已取消。')
            p = self.spawn(argv)
            self.active = p
        try:
            out, _ = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.kill(p)
            p.communicate()
            raise RuntimeError('命令超时，已终止后台进程。请检查手机解锁、信任和连接状态。') from None
        finally:
            with self.lock:
                self.active = None
        if self.cancelled.is_set():
            raise RuntimeError('操作已取消。')
        if check and p.returncode:
            raise RuntimeError(error_summary(out, p.returncode))
        return p.returncode, out

class Backend:
    def __init__(self, data_dir, emit, python=None):
        self.data = Path(data_dir)
        self.data.mkdir(parents=True, exist_ok=True)
        self.emit = emit
        self.base_python = python or runtime_default()
        self.runner = Runner()
        self.sim = None
        self.sim_target = None
        self.sim_output = ''
        self.sim_guard = threading.Lock()
        self.recovery = self.data / 'recovery.json'

    @property
    def python(self):
        p = self.data / 'venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        return str(p) if p.exists() else self.base_python

    def run_python(self, args, **kwargs):
        if not self.python or not Path(self.python).is_file():
            raise RuntimeError('请先选择有效的 Python 解释器（建议 3.14.7）。')
        return self.runner.run([self.python, *args], **kwargs)

    def cli(self, *args, **kwargs):
        return self.run_python(['-m', 'pymobiledevice3', *args], **kwargs)[1]

    def diagnose(self):
        self.emit('log', 'Windows: ' + ('是' if os.name == 'nt' else '否，本版面向 Windows'))
        if os.name == 'nt':
            # Only counts/status leave PowerShell; PnP identifiers are never returned.
            script = "$ErrorActionPreference='Stop'; $n=@(Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -like 'USB\\VID_05AC*' }).Count; Write-Output $n"
            code, out = self.runner.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',script], timeout=30, check=False)
            count = out.strip()
            self.emit('log', 'Windows Apple USB 硬件枚举：' + (count+' 个接口（不等于手机数量）' if code == 0 and count.isdigit() else '无法读取；将继续检测 USB 通信服务'))
        _, out = self.run_python(['-c', 'import sys; print(sys.version.split()[0])'])
        self.emit('check', ('Python', out.strip()))
        self.emit('log', 'Python: ' + out.strip())
        code, _ = self.run_python(['-m', 'pip', '--version'], check=False)
        self.emit('log', 'pip: ' + ('可用' if code == 0 else '不可用'))
        code, out = self.run_python(['-c', 'import importlib.metadata; print(importlib.metadata.version("pymobiledevice3"))'], check=False)
        if code:
            raise RuntimeError('pymobiledevice3 未安装，请点击“安装隔离环境”。')
        version = out.strip()
        self.emit('check', ('pymobiledevice3',version))
        self.emit('log', 'pymobiledevice3: ' + version)
        if version != VERSION:
            raise RuntimeError('当前版本与验证基线不同，请安装固定为 11.63.1 的隔离环境。')
        self.verify_help()
        self.profile(self.device())
        self.emit('log', '环境诊断完成。检测到设备不代表定位已生效。')

    def verify_help(self):
        for args, expected in [
            (['developer','dvt','simulate-location','set','--help'], ['--userspace','--udid','latitude','longitude']),
            (['developer','dvt','simulate-location','clear','--help'], ['--userspace']),
            (['amfi','reveal-developer-mode','--help'], ['--udid']),
        ]:
            out = self.cli(*args)
            if not all(x in out for x in expected):
                raise RuntimeError('命令帮助与预期不一致，已停止操作。请检查依赖版本。')
        self.emit('log', '定位、清除和开发者模式命令帮助：校验通过。')

    def device(self, expected=None):
        out = self.cli('usbmux', 'list', '--usb', '--simple')
        try:
            devices = json.loads(out)
        except ValueError:
            raise RuntimeError('USB 返回格式异常，请检查 Apple Devices 服务。') from None
        if not isinstance(devices, list) or len(devices) != 1 or not isinstance(devices[0], str):
            raise RuntimeError('请仅连接一台 USB iPhone。当前未检测到唯一设备；请检查数据线与 Apple Devices 驱动。')
        target = devices[0]
        if expected and target != expected:
            raise RuntimeError('当前连接的手机与本次定位手机不同。请重新接回原手机后恢复定位。')
        self.emit('check', ('Apple USB','已连接'))
        self.emit('log', 'Apple USB 通信：检测到一台设备（不显示设备标识）。')
        return target

    def profile(self, target):
        rows = json.loads(self.cli('usbmux', 'list', '--usb'))
        for row in rows:
            if target not in (row.get('Identifier'), row.get('UniqueDeviceID')):
                continue
            version = str(row.get('ProductVersion', ''))
            if not re.fullmatch(r'[0-9]{1,2}(?:\.[0-9]{1,3}){0,3}', version):
                break
            model = str(row.get('ProductType', ''))
            if not re.fullmatch(r'iPhone[0-9]+,[0-9]+', model):
                raise RuntimeError('请选择受支持的 iPhone。')
            display = 'iPhone 14 Pro' if model == 'iPhone15,2' else model
            self.emit('device', (display, version))
            parts = tuple(map(int, version.split('.')))
            return (parts + (0,))[:2]
        raise RuntimeError('无法读取当前手机的 iOS 版本。请解锁、确认信任并重新检测。')

    @staticmethod
    def location_command(version, target, action):
        if version < (17, 0):
            return ['developer', 'simulate-location', action, '--udid', target]
        transport = ['--tunnel', target] if version < (17, 4) else ['--userspace','--udid',target]
        return ['developer','dvt','simulate-location',action,*transport]

    def install(self):
        if self.sim and self.sim.poll() is None:
            raise RuntimeError('请先停止并恢复真实定位，再安装或修复环境。')
        if not self.base_python or not Path(self.base_python).is_file():
            raise RuntimeError('请先选择基础 Python 解释器。')
        dest = self.data / 'venv'
        self.emit('log', '正在创建或修复应用独立 venv，请等待……')
        self.runner.run([self.base_python, '-m', 'venv', str(dest)], timeout=180)
        self.emit('log', '正在从 PyPI 下载固定版本及依赖，最长等待 15 分钟……')
        self.run_python(['-m', 'pip', 'install', '--disable-pip-version-check', '--no-input', 'pymobiledevice3=='+VERSION], timeout=900)
        self.emit('log', '依赖安装完成。')
        self.diagnose()

    def developer(self, action):
        target = self.device()
        if self.profile(target) < (16, 0):
            self.emit('log', '此版本早于 iOS 16，无需开发者模式开关。')
            return
        out = self.cli('amfi', action, '--udid', target, timeout=60)
        if action == 'developer-mode-status':
            val = out.strip().lower()
            self.emit('log', '开发者模式：' + ('已开启' if val == 'true' else '未开启' if val == 'false' else '状态无法确认'))
        else:
            self.emit('log', '已请求显示开发者模式开关。请在手机设置 → 隐私与安全性中手动开启，完成重启并确认，再检测状态。')

    def tunnel(self):
        target = self.device()
        version = self.profile(target)
        if version < (17, 0):
            self.emit('transport', '传统 USB · 无需隧道')
            self.emit('log', '旧版 iOS 走传统 USB 服务，定位需要匹配的开发者镜像。')
            return
        options = self.location_command(version, target, 'set')[4:]
        self.cli('developer', 'dvt', 'ls', *options, '/', timeout=60)
        self.emit('transport', '已验证 · ' + ('tunneld' if version < (17,4) else '用户空间'))
        self.emit('log', '本次开发者隧道诊断成功。')

    def set_location(self, lat, lon):
        lat, lon = coordinates(lat, lon)
        if self.sim and self.sim.poll() is None:
            raise RuntimeError('已有定位会话，请先恢复真实定位。')
        if self.recovery.exists():
            raise RuntimeError('上次定位尚未确认恢复，请先点击“恢复真实定位”。')
        self.verify_help()
        target = self.device()
        version = self.profile(target)
        args = self.location_command(version, target, 'set') + ['--',str(lat),str(lon)]
        self.sim_target = target
        self.recovery.write_text('{"needs_clear": true}', encoding='utf-8')
        self.sim_output = ''
        if self.runner.cancelled.is_set():
            raise RuntimeError('操作已取消；恢复标记已保留，请执行恢复真实定位。')
        if version < (17,0):
            self.cli(*args,timeout=60)
            self.emit('status', '已发送传统 USB 定位指令，请在手机上确认；结束时点击恢复。')
            return
        p = self.runner.spawn([self.python, '-m','pymobiledevice3',*args])
        self.sim = p
        self.emit('status', '正在连接定位服务；尚未验证手机位置')
        threading.Thread(target=self._watch_sim, args=(p,), daemon=True).start()
        threading.Thread(target=self._startup_timeout, args=(p,), daemon=True).start()

    def _startup_timeout(self, p):
        deadline = time.monotonic()+75
        while p.poll() is None and time.monotonic() < deadline:
            with self.sim_guard:
                if 'Press ENTER' in self.sim_output or 'Press Ctrl+C' in self.sim_output: return
            time.sleep(.25)
        if p.poll() is None and self.sim is p:
            self.runner.kill(p)
            self.emit('log', '定位服务启动超时，已停止进程并保留恢复标记。请检查连接后恢复真实定位。')

    def _watch_sim(self, p):
        ready = False
        while True:
            try: ch = p.stdout.read(1)
            except (OSError,ValueError): break
            if not ch:
                break
            with self.sim_guard:
                self.sim_output = (self.sim_output + ch)[-16000:]
                output = self.sim_output
            if not ready and ('Press ENTER' in output or 'Press Ctrl+C' in output):
                ready = True
                self.emit('status', '定位命令已进入等待状态；请在手机地图验证')
        code = p.wait()
        if self.sim is p:
            self.emit('status', '定位进程已结束；请执行恢复真实定位')
            if code:
                self.emit('log', error_summary(self.sim_output, code))

    def stop_sim(self):
        p = self.sim
        self.sim = None
        if p and p.poll() is None:
            try:
                p.stdin.write('\n')
                p.stdin.flush()
                p.wait(timeout=6)
            except (OSError, ValueError, subprocess.TimeoutExpired):
                self.runner.kill(p)
        if p:
            for stream in (p.stdin, p.stdout):
                if stream:
                    try:
                        stream.close()
                    except OSError:
                        pass

    def clear_location(self):
        self.stop_sim()
        target = self.device(self.sim_target)
        self.cli(*self.location_command(self.profile(target),target,'clear'),timeout=60)
        self.recovery.unlink(missing_ok=True)
        self.sim_target = None
        self.emit('status', '清除命令成功；请在手机地图确认真实定位')
        self.emit('log', '已发送清除模拟定位命令。如地图缓存未刷新，请重新打开地图并等待真实定位。')

    def public_ip(self):
        # Called exclusively after a fresh explicit UI opt-in. No location/device data sent.
        req = urllib.request.Request('https://ipapi.co/json/', headers={'User-Agent':'GeoShift/0.1'})
        with urllib.request.urlopen(req, timeout=12) as response:
            info = json.loads(response.read(65536))
        addr = str(ipaddress.ip_address(info['ip']))
        country = str(info.get('country_name') or info.get('country') or '未知')[:80]
        self.emit('ip', f'{addr} · {country}')
        self.emit('log', '已按本次授权查询电脑公网出口，IP 仅显示在界面，不写入日志。此结果不代表 iPhone 网络出口。')

    def launch_vpn(self, path):
        p = Path(path)
        if p.suffix.lower() != '.exe' or not p.is_file():
            raise RuntimeError('请选择已经安装的 VPN/代理客户端 EXE。')
        # User-owned external application; intentionally not killed on GeoShift exit.
        subprocess.Popen([str(p)], env=clean_env(), cwd=str(p.parent))
        self.emit('log', '已启动所选现有客户端。请在客户端内连接已有配置；本程序不确认或保证出口变化。')
