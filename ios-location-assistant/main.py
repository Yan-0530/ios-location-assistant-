"""Chinese Tk GUI; all backend work runs off the Tk thread."""
import argparse
import json
import os
from pathlib import Path
import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from dpi import enable_native_dpi
from locales import translate
from dashboard import Dashboard
from core import Backend, PRESETS, coordinates, redact

class App(tk.Tk):
    def __init__(self, data_dir=None):
        enable_native_dpi()
        super().__init__()
        self.scale=self.winfo_fpixels('1i')/96.0
        self.title('虚拟定位助手')
        self.geometry('960x780')
        self.minsize(840, 700)
        self.events = queue.Queue()
        folder = data_dir or Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'GeoShift'
        self.backend = Backend(folder, lambda kind, value: self.events.put((kind, value)))
        self.pref_path=Path(folder)/'language.txt'
        try:
            self.language='en' if self.pref_path.read_text('ascii').strip()=='en' else 'zh'
        except (OSError,UnicodeError):
            self.language='zh'
        self.title(self.tr('虚拟定位助手'))
        self.busy = False
        self.closing = False
        self.buttons = []
        self.logs = []
        self.status = tk.StringVar(value='就绪 · 请先检测环境与 USB 连接')
        self.ip = tk.StringVar(value='未查询（需单次授权）')
        self.country = tk.StringVar(value='美国')
        self.city = tk.StringVar(value='洛杉矶')
        self.lat = tk.StringVar(value='34.0528')
        self.lon = tk.StringVar(value='-118.2516')
        self.dashboard = Dashboard(self)
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.poll_timer = self.after(100, self.poll)
        self.log('界面已就绪。环境安装和公网查询均需确认，不会在启动时联网。')
        if self.backend.recovery.exists():
            self.status.set('上次会话未确认恢复：请连接原手机并点击“停止并恢复真实定位”')
            self.log('发现恢复标记。标记不含设备 ID；请自行确认连接的是上次测试手机。')

    def tr(self,text):
        return translate(text,self.language)

    def toggle_language(self):
        self.language='en' if self.language=='zh' else 'zh'
        try:self.pref_path.write_text(self.language,encoding='ascii')
        except OSError:pass
        self.title(self.tr('虚拟定位助手'))
        self.dashboard.refresh_language()
        self.render_logs()

    def set_custom(self,lat,lon):
        if self.country.get()!='自定义':
            self.country.set('自定义')
            self.city.set('自定义坐标')
            self.dashboard.refresh_presets()
        self.lat.set(f'{lat:.5f}')
        self.lon.set(f'{lon:.5f}')

    def log(self, msg):
        line = datetime.now().strftime('%H:%M:%S') + '  ' + redact(msg)
        self.logs.append(line); self.logs = self.logs[-2000:]
        self.render_logs()

    def render_logs(self):
        self.logbox.configure(state='normal')
        self.logbox.delete('1.0','end'); self.logbox.insert('end','\n'.join(self.tr(line) for line in self.logs))
        self.logbox.see('end'); self.logbox.configure(state='disabled')

    def work(self, action, completion=None):
        if self.busy: return
        self.busy = True
        self.backend.runner.cancelled.clear()
        for b in self.buttons: b.configure(state='disabled')
        self.cancel_button.configure(state='normal')
        self.status.set('正在处理，请等待……')
        def run():
            ok = False
            try:
                action(); ok = True
            except (RuntimeError, ValueError) as e:
                self.events.put(('error', str(e)))
            except Exception:
                # Unknown errors may contain paths, device names or provider responses.
                self.events.put(('error', '操作未完成：发生系统、网络或输出格式错误。请检查配置和连接后重试；原始异常未写入日志。'))
            finally:
                self.events.put(('done', (ok, completion)))
        threading.Thread(target=run, daemon=True).start()

    def poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == 'log': self.log(value)
                elif kind == 'device':
                    model, version = value
                    self.dashboard.model.set(model)
                    self.dashboard.os.set('iOS ' + version + '   ·   USB 已连接')
                elif kind == 'check':
                    key, result = value
                    self.dashboard.checks[key].set(result)
                elif kind == 'transport':
                    self.dashboard.checks['开发者隧道'].set(value)
                elif kind == 'ip': self.ip.set(value)
                elif kind == 'status': self.status.set(value); self.log(value)
                elif kind == 'error':
                    self.status.set(value); self.log(value)
                    messagebox.showerror(self.tr('操作未完成'), self.tr(value), parent=self)
                elif kind == 'done':
                    self.busy = False
                    for b in self.buttons: b.configure(state='normal')
                    self.cancel_button.configure(state='disabled')
                    ok, callback = value
                    if ok and self.status.get() == '正在处理，请等待……': self.status.set('操作完成，请查看日志')
                    if callback: callback(ok)
        except queue.Empty: pass
        if self.winfo_exists(): self.poll_timer = self.after(100, self.poll)

    def destroy(self):
        if getattr(self, 'poll_timer', None):
            self.after_cancel(self.poll_timer)
            self.poll_timer = None
        super().destroy()

    def install(self):
        if messagebox.askyesno(self.tr('确认安装'), self.tr('将使用所选基础 Python 在 %LOCALAPPDATA%\\GeoShift\\venv 创建独立环境，并从 PyPI 下载 pymobiledevice3==11.63.1 及依赖。需要网络和磁盘空间，不修改系统 Python。继续？'), parent=self):
            self.work(self.backend.install)

    def choose_python(self):
        if self.backend.sim and self.backend.sim.poll() is None:
            messagebox.showinfo(self.tr('请先恢复定位'), self.tr('请先停止并恢复真实定位，再更换基础 Python。'), parent=self); return
        path = filedialog.askopenfilename(title=self.tr('选择基础 python.exe'), filetypes=[(self.tr('Python'), 'python.exe'),(self.tr('所有文件'),'*.*')])
        if path:
            self.backend.base_python = path
            self.log('已选择基础 Python。已存在的隔离环境仍优先使用；需要时可重新安装修复。')

    def developer(self):
        messagebox.showinfo(self.tr('开发者模式引导'), self.tr('此按钮仅请求显示手机中的开发者模式开关。\n请解锁手机并信任电脑。随后在设置 → 隐私与安全性中手动开启，按手机提示重启并确认。\n有密码的手机请保留密码，按手动流程操作。'), parent=self)
        self.work(lambda: self.backend.developer('reveal-developer-mode'))

    def change_country(self, _=None):
        names = list(PRESETS[self.country.get()]); self.cities.configure(values=names)
        self.city.set(names[0]); self.change_city(); self.dashboard.refresh_presets()

    def change_city(self, _=None):
        a,b = PRESETS[self.country.get()][self.city.get()]
        self.lat.set(str(a)); self.lon.set(str(b))

    def start(self):
        try: a,b = coordinates(self.lat.get(), self.lon.get())
        except ValueError:
            messagebox.showerror(self.tr('坐标无效'), self.tr('请输入有效经纬度：纬度 -90～90，经度 -180～180。'), parent=self); return
        self.work(lambda: self.backend.set_location(a,b))

    def clear(self):
        if self.backend.recovery.exists() and not self.backend.sim_target:
            if not messagebox.askyesno(self.tr('确认恢复设备'), self.tr('恢复标记不保存设备身份。请确认当前仅连接上次测试的 iPhone；继续向这台手机发送清除模拟定位命令？'), parent=self): return
        self.work(self.backend.clear_location)

    def query_ip(self):
        if messagebox.askyesno(self.tr('本次公网查询授权'), self.tr('将向第三方 https://ipapi.co/json/ 发起一次 HTTPS 请求。对方会收到电脑当前出口 IP；不发送设备标识或 GPS 坐标。结果仅显示在本次界面，国家信息可能不准确。继续？'), parent=self):
            self.work(self.backend.public_ip)

    def vpn(self):
        path = filedialog.askopenfilename(title=self.tr('选择已安装的 VPN / 代理客户端'), filetypes=[(self.tr('应用程序'),'*.exe')])
        if path and messagebox.askyesno(self.tr('启动现有客户端'), self.tr('将运行你选择的 EXE。请确认来源可信，并在客户端内选择已有配置。继续？'), parent=self):
            self.work(lambda: self.backend.launch_vpn(path))

    def export(self):
        path = filedialog.asksaveasfilename(title=self.tr('导出脱敏日志'), defaultextension='.txt', initialfile=self.tr('虚拟定位助手_脱敏日志.txt'), filetypes=[(self.tr('文本日志'),'*.txt')])
        if path:
            try:
                Path(path).write_text((self.tr('脱敏事件记录')+' · 0.3\n') + redact('\n'.join(self.tr(line) for line in self.logs)), encoding='utf-8')
            except OSError: messagebox.showerror(self.tr('导出失败'), self.tr('无法写入该位置，请选择其他文件夹。'), parent=self)

    def cancel(self):
        self.log('正在取消当前操作。取消不会自动清除已有模拟定位，请点击恢复真实定位。')
        threading.Thread(target=self.backend.runner.cancel, daemon=True).start()

    def close(self):
        if self.busy:
            messagebox.showinfo(self.tr('请先取消操作'), self.tr('请先取消当前操作，等待结束后关闭。'), parent=self); return
        if self.backend.recovery.exists() or self.backend.sim:
            if messagebox.askyesno(self.tr('退出并恢复'), self.tr('退出前将尝试停止会话并清除模拟定位。请保持原手机连接、解锁。继续？'), parent=self):
                def completed(ok):
                    if ok: self.destroy()
                    elif messagebox.askyesno(self.tr('恢复未成功'), self.tr('恢复失败，已保留恢复标记。仍要退出？下次启动后请重试恢复；必要时重启手机并在地图验证。'), parent=self):
                        self.destroy()
                self.work(self.backend.clear_location, completed)
        else: self.destroy()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke-test', help='Create GUI offline, then write JSON report and exit')
    args = parser.parse_args()
    if args.smoke_test:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            app = App(tmp); app.update()
            _, result = app.backend.run_python(['-c', "print('runtime-ok')"])
            report={'gui_created':True,'tk':tk.TkVersion,'frozen':bool(getattr(sys,'frozen',False)),
                    'external_runtime_started':result.strip()=='runtime-ok','network_requested':False}
            if sys.platform=='win32':
                import ctypes
                user32=ctypes.windll.user32
                user32.GetThreadDpiAwarenessContext.restype=ctypes.c_void_p
                actual=ctypes.c_void_p(user32.GetThreadDpiAwarenessContext())
                report['per_monitor_v2']=bool(user32.AreDpiAwarenessContextsEqual(actual,ctypes.c_void_p(-4)))
                report['window_dpi']=user32.GetDpiForWindow(app.winfo_id())
            app.dashboard.show('虚拟定位')
            app.toggle_language()
            report['english_location_page']=app.dashboard.heading.cget('text')=='Location'
            Path(args.smoke_test).write_text(json.dumps(report),encoding='utf-8')
            app.destroy()
    else:
        app = App(); app.mainloop()

if __name__ == '__main__': main()
