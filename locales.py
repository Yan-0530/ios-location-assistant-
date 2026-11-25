"""English UI strings, keyed by their Chinese source text."""
import re

EN = {'发布声明': 'Distribution notice',
 '虚拟定位助手目前仅通过 GitHub 官方仓库发布。禁止二次转载或转售本软件。': 'The official GitHub repository is currently the only release channel for Location Assistant. Republishing or reselling this software is prohibited.',
 '控制面板': 'Dashboard',
 '设备管理': 'Devices',
 '环境检测': 'Environment',
 '网络配置': 'Network',
 '虚拟定位': 'Location',
 '运行日志': 'Activity log',
 '设置': 'Settings',
 '等待检测': 'Not checked',
 '连接并解锁 iPhone': 'Connect and unlock your iPhone',
 '待检测': 'Not checked',
 '开发者隧道': 'Developer tunnel',
 '  虚拟定位助手': '  Location Assistant',
 '取消当前操作': 'Cancel task',
 '开发者': 'Developer',
 'Yan以及他忠实的AI大人': 'Yan and his faithful AI overlord',
 '设备控制中心': 'Device dashboard',
 'USB 设备': 'USB device',
 '网络出口': 'Network egress',
 '电脑公网 IP 与国家': 'Computer public IP and country',
 '运行环境': 'Runtime',
 '检测环境 / USB': 'Check environment / USB',
 '安装隔离环境…': 'Install environment…',
 '检测开发者隧道': 'Check tunnel',
 '目标地区': 'Destination',
 '纬度   Latitude': 'Latitude',
 '经度   Longitude': 'Longitude',
 '开始静态定位': 'Start simulation',
 '停止并恢复真实定位': 'Stop and restore location',
 '开发者模式': 'Developer Mode',
 '在 iOS 16 及以后版本，进入「设置 → 隐私与安全性 → 开发者模式」，开启后按手机提示重启并确认。': 'On iOS 16 or later, open Settings → Privacy & Security → '
                                                          'Developer Mode. Turn it on, restart, and confirm on the phone.',
 '显示手机开关…': 'Reveal switch…',
 '读取模式状态': 'Check mode',
 '设备兼容性': 'Device compatibility',
 'iOS 16 及以前': 'iOS 16 and earlier',
 '传统 USB 定位服务，需要匹配的开发者镜像。': 'Legacy USB services require a matching Developer Disk Image.',
 'Windows 需要事先启动管理员 tunneld 服务。': 'Start tunneld as an administrator on Windows first.',
 'iOS 17.4 及以后': 'iOS 17.4 and later',
 '在受支持设备上自动建立用户空间隧道。': 'Supported USB devices can open a userspace tunnel automatically.',
 'Android 真机': 'Android phones',
 '需在手机开发者选项选择模拟位置应用。本版提供 iPhone 控制。': 'Android requires a mock location app selected in Developer options. This app '
                                      'controls iPhones.',
 '公网出口': 'Public IP',
 '查询会向 ipapi.co 发送电脑的出口 IP。手机网络出口由手机自身的网络配置决定。': "A lookup sends your computer's egress IP to ipapi.co. Your iPhone uses "
                                                 'its own network connection.',
 '授权查询公网 IP…': 'Look up public IP…',
 '启动已有 VPN / 代理…': 'Launch VPN / proxy…',
 'Python 解释器': 'Python interpreter',
 '手机后台优先使用已安装的独立环境。可在这里选择创建环境使用的 python.exe。': 'The phone backend prefers the installed virtual environment. Choose the '
                                               'base python.exe used to create it.',
 '选择基础 Python…': 'Choose Python…',
 '脱敏事件记录': 'Redacted activity log',
 '导出脱敏日志…': 'Export redacted log…',
 '检测中…': 'Checking…',
 '正在读取 USB 信息': 'Reading USB information',
 '未确认设备': 'Device not confirmed',
 '请检查 USB 与信任状态': 'Check USB and trust settings',
 '检测失败': 'Check failed',
 '目标坐标  /  全球概览': 'Target / World overview',
 '虚拟定位助手': 'Location Assistant',
 '就绪 · 请先检测环境与 USB 连接': 'Ready · Check your environment and USB connection',
 '未查询（需单次授权）': 'Not queried',
 '美国': 'United States',
 '洛杉矶': 'Los Angeles',
 '界面已就绪。环境安装和公网查询均需确认，不会在启动时联网。': 'Ready. Installing dependencies and looking up the public IP each require confirmation.',
 '上次会话未确认恢复：请连接原手机并点击“停止并恢复真实定位”': 'Recovery pending. Reconnect the original phone and choose Stop and restore location.',
 '发现恢复标记。标记不含设备 ID；请自行确认连接的是上次测试手机。': 'A recovery marker exists. It contains no device ID. Check that the original phone is '
                                      'connected.',
 '正在处理，请等待……': 'Working…',
 '操作未完成：发生系统、网络或输出格式错误。请检查配置和连接后重试；原始异常未写入日志。': 'A system, network or data error occurred. Check your settings and '
                                                'connection, then retry. The raw exception was discarded.',
 '   ·   USB 已连接': '   ·   USB connected',
 '操作未完成': 'Operation incomplete',
 '操作完成，请查看日志': 'Done. See the activity log.',
 '确认安装': 'Confirm installation',
 '将使用所选基础 Python 在 %LOCALAPPDATA%\\GeoShift\\venv 创建独立环境，并从 PyPI 下载 pymobiledevice3==11.63.1 及依赖。需要网络和磁盘空间，不修改系统 Python。继续？': 'Create '
                                                                                                                              'an '
                                                                                                                              'isolated '
                                                                                                                              'environment '
                                                                                                                              'under '
                                                                                                                              '%LOCALAPPDATA%\\GeoShift\\venv '
                                                                                                                              'and '
                                                                                                                              'download '
                                                                                                                              'pymobiledevice3 '
                                                                                                                              '11.63.1 '
                                                                                                                              'and '
                                                                                                                              'its '
                                                                                                                              'dependencies '
                                                                                                                              'from '
                                                                                                                              'PyPI? '
                                                                                                                              'This '
                                                                                                                              'requires '
                                                                                                                              'network '
                                                                                                                              'access '
                                                                                                                              'and '
                                                                                                                              'disk '
                                                                                                                              'space.',
 '请先恢复定位': 'Restore location first',
 '请先停止并恢复真实定位，再更换基础 Python。': 'Stop the simulation and restore the real location before changing Python.',
 '选择基础 python.exe': 'Select base python.exe',
 '所有文件': 'All files',
 '已选择基础 Python。已存在的隔离环境仍优先使用；需要时可重新安装修复。': 'Base Python selected. The installed virtual environment takes priority. Run '
                                           'installation again to repair it.',
 '开发者模式引导': 'Developer Mode guide',
 '此按钮仅请求显示手机中的开发者模式开关。\n请解锁手机并信任电脑。随后在设置 → 隐私与安全性中手动开启，按手机提示重启并确认。\n有密码的手机请保留密码，按手动流程操作。': 'This requests the Developer '
                                                                                           'Mode switch. Unlock the phone '
                                                                                           'and trust this computer. On the '
                                                                                           'phone, open Settings → Privacy '
                                                                                           '& Security → Developer Mode, '
                                                                                           'enable it, restart and confirm. '
                                                                                           'Keep your passcode enabled.',
 '坐标无效': 'Invalid coordinates',
 '请输入有效经纬度：纬度 -90～90，经度 -180～180。': 'Enter a latitude from −90 to 90 and a longitude from −180 to 180.',
 '确认恢复设备': 'Confirm recovery device',
 '恢复标记不保存设备身份。请确认当前仅连接上次测试的 iPhone；继续向这台手机发送清除模拟定位命令？': 'The marker contains no device ID. Is the original test iPhone the '
                                                        'only phone connected? Send the clear command to it?',
 '本次公网查询授权': 'Allow public IP lookup',
 '将向第三方 https://ipapi.co/json/ 发起一次 HTTPS 请求。对方会收到电脑当前出口 IP；不发送设备标识或 GPS 坐标。结果仅显示在本次界面，国家信息可能不准确。继续？': 'Send one HTTPS '
                                                                                                       'request to '
                                                                                                       'https://ipapi.co/json/? '
                                                                                                       'The service '
                                                                                                       'receives this '
                                                                                                       "computer's public "
                                                                                                       'IP. The request '
                                                                                                       'excludes device IDs '
                                                                                                       'and GPS '
                                                                                                       'coordinates. The '
                                                                                                       'result is shown '
                                                                                                       'only here. The '
                                                                                                       'country estimate '
                                                                                                       'may be inaccurate.',
 '选择已安装的 VPN / 代理客户端': 'Select an installed VPN or proxy client',
 '应用程序': 'Applications',
 '启动现有客户端': 'Launch existing client',
 '将运行你选择的 EXE。请确认来源可信，并在客户端内选择已有配置。继续？': 'Run the selected executable? Confirm that you trust its source and select an '
                                         'existing configuration in the client.',
 '导出脱敏日志': 'Export redacted log',
 '虚拟定位助手_脱敏日志.txt': 'Location_Assistant_log.txt',
 '文本日志': 'Text log',
 '导出失败': 'Export failed',
 '无法写入该位置，请选择其他文件夹。': 'Unable to write here. Choose another folder.',
 '正在取消当前操作。取消不会自动清除已有模拟定位，请点击恢复真实定位。': 'Cancelling. To clear an existing location simulation, choose Stop and restore '
                                       'location.',
 '请先取消操作': 'Cancel the current task first',
 '请先取消当前操作，等待结束后关闭。': 'Cancel the current task and wait for it to finish before closing.',
 '退出并恢复': 'Restore and exit',
 '退出前将尝试停止会话并清除模拟定位。请保持原手机连接、解锁。继续？': 'Stop the session and clear the simulated location before exiting? Keep the original '
                                      'phone connected and unlocked.',
 '恢复未成功': 'Recovery incomplete',
 '恢复失败，已保留恢复标记。仍要退出？下次启动后请重试恢复；必要时重启手机并在地图验证。': 'Recovery failed. The marker has been retained. Exit anyway? Reconnect the '
                                                'phone and retry recovery on the next launch. Restart the phone if '
                                                'necessary and check Maps.',
 '日本': 'Japan',
 '东京': 'Tokyo',
 '大阪': 'Osaka',
 '纽约': 'New York',
 '中国': 'China',
 '北京': 'Beijing',
 '上海': 'Shanghai',
 '英国': 'United Kingdom',
 '伦敦': 'London',
 '法国': 'France',
 '巴黎': 'Paris',
 '澳大利亚': 'Australia',
 '悉尼': 'Sydney',
 '自定义': 'Custom',
 '自定义坐标': 'Custom coordinates',
 '纬度须为 -90～90，经度须为 -180～180，且必须为有限数值。': 'Latitude must be within ±90°, longitude within ±180°, and both must be finite.',
 '无法建立 Windows 后台进程保护。请在普通桌面会话中运行。': 'Windows could not create a background process job. Run in a normal desktop session.',
 '无法将后台进程加入生命周期保护，操作已停止。': 'Windows could not attach the backend to its process job. The operation stopped.',
 '手机设有密码，请在设置 → 隐私与安全性 → 开发者模式中手动启用。': 'Manually enable Developer Mode in Settings → Privacy & Security on the phone.',
 '请解锁手机后重试。': 'Unlock your phone and retry.',
 '请解锁手机，确认“信任此电脑”，然后重试。': 'Unlock the phone, confirm Trust This Computer, and retry.',
 '请确认手机开发者模式已启用，并完成重启后的确认。': 'Enable Developer Mode and confirm on the phone after restarting.',
 '未能连接 USB 设备。请检查数据线、Apple Devices 驱动和信任状态。': 'Could not connect over USB. Check the data cable, Apple Devices driver and '
                                              'trust settings.',
 '依赖缺失，请安装隔离环境。': 'Dependencies are missing. Install the isolated environment.',
 '开发者服务或开发者镜像不可用。请检查手机版本、开发者模式及官方镜像挂载指引。': 'The developer service or disk image is unavailable. Check the iOS version, '
                                           'Developer Mode and upstream image mounting guide.',
 '开发者隧道失败。请重新连接 USB、解锁手机并运行隧道诊断。': 'Tunnel failed. Reconnect USB, unlock the phone and run the tunnel check.',
 '下载或依赖安装失败，请检查网络、证书及 Python 兼容性。': 'Download or installation failed. Check the network, certificates and Python version.',
 '（退出码 ': ' (exit code ',
 '命令失败（退出码 ': 'Command failed (exit code ',
 '）。原始输出未保存，以免泄露设备信息；请检查连接、信任和依赖后重试。': '). Check USB, trust and dependencies. Raw output was discarded to protect device '
                                       'information.',
 '操作已取消。': 'Cancelled.',
 '命令超时，已终止后台进程。请检查手机解锁、信任和连接状态。': 'Command timed out. The process was stopped. Check USB, trust and the phone lock screen.',
 '请先选择有效的 Python 解释器（建议 3.14.7）。': 'Select a valid Python interpreter (3.14.7 recommended).',
 '是': 'yes',
 '否，本版面向 Windows': 'no; Windows is required',
 'Windows Apple USB 硬件枚举：': 'Windows Apple USB interfaces: ',
 '无法读取；将继续检测 USB 通信服务': 'unavailable; continuing with USB service detection',
 ' 个接口（不等于手机数量）': ' interfaces detected',
 '可用': 'available',
 '不可用': 'unavailable',
 'pymobiledevice3 未安装，请点击“安装隔离环境”。': 'pymobiledevice3 is missing. Choose Install environment.',
 '当前版本与验证基线不同，请安装固定为 11.63.1 的隔离环境。': 'Unexpected backend version. Install the environment pinned to 11.63.1.',
 '环境诊断完成。检测到设备不代表定位已生效。': 'Diagnostics complete. Verify the actual location on the phone during testing.',
 '命令帮助与预期不一致，已停止操作。请检查依赖版本。': 'CLI help differs from the expected version. Check the installed dependencies.',
 '定位、清除和开发者模式命令帮助：校验通过。': 'Location, clear and Developer Mode commands verified.',
 'USB 返回格式异常，请检查 Apple Devices 服务。': 'Unexpected USB response. Check Apple Devices.',
 '请仅连接一台 USB iPhone。当前未检测到唯一设备；请检查数据线与 Apple Devices 驱动。': 'Connect exactly one iPhone by USB. Check the cable and Apple '
                                                           'Devices driver.',
 '当前连接的手机与本次定位手机不同。请重新接回原手机后恢复定位。': 'This is a different phone. Reconnect the original iPhone to restore its location.',
 '已连接': 'Connected',
 'Apple USB 通信：检测到一台设备（不显示设备标识）。': 'One Apple USB device detected.',
 '请选择受支持的 iPhone。': 'Select a supported iPhone.',
 '无法读取当前手机的 iOS 版本。请解锁、确认信任并重新检测。': 'Could not read iOS version. Unlock, confirm trust, then recheck.',
 '请先停止并恢复真实定位，再安装或修复环境。': 'Restore location before installing or repairing the environment.',
 '请先选择基础 Python 解释器。': 'Select the base Python interpreter first.',
 '正在创建或修复应用独立 venv，请等待……': 'Creating or repairing the virtual environment…',
 '正在从 PyPI 下载固定版本及依赖，最长等待 15 分钟……': 'Downloading the pinned version and dependencies from PyPI. This may take up to 15 '
                                    'minutes.',
 '依赖安装完成。': 'Dependencies installed.',
 '此版本早于 iOS 16，无需开发者模式开关。': 'This version predates iOS 16 and does not use a Developer Mode switch.',
 '开发者模式：': 'Developer Mode: ',
 '已开启': 'enabled',
 '未开启': 'disabled',
 '状态无法确认': 'unknown',
 '已请求显示开发者模式开关。请在手机设置 → 隐私与安全性中手动开启，完成重启并确认，再检测状态。': 'Developer Mode switch requested. Enable it on the phone, restart, '
                                                     'confirm, then check its status.',
 '传统 USB · 无需隧道': 'Legacy USB · No tunnel required',
 '旧版 iOS 走传统 USB 服务，定位需要匹配的开发者镜像。': 'This iOS version uses legacy USB and requires a matching Developer Disk Image for '
                                    'simulation.',
 '已验证 · ': 'Verified · ',
 '用户空间': 'userspace',
 '本次开发者隧道诊断成功。': 'Developer tunnel check passed.',
 '已有定位会话，请先恢复真实定位。': 'A session is already running. Restore the real location first.',
 '上次定位尚未确认恢复，请先点击“恢复真实定位”。': 'The previous session needs recovery. Choose Stop and restore location first.',
 '操作已取消；恢复标记已保留，请执行恢复真实定位。': 'Cancelled. The recovery marker was retained. Restore the real location.',
 '已发送传统 USB 定位指令，请在手机上确认；结束时点击恢复。': 'Legacy USB location command sent. Check the phone, then restore when finished.',
 '正在连接定位服务；尚未验证手机位置': 'Connecting to the location service. Check the phone for the actual position.',
 '定位服务启动超时，已停止进程并保留恢复标记。请检查连接后恢复真实定位。': 'Location service timed out. The process was stopped. Check USB and restore '
                                        'location.',
 '定位命令已进入等待状态；请在手机地图验证': 'Location session is waiting. Check Maps on the phone.',
 '定位进程已结束；请执行恢复真实定位': 'The location process ended. Restore the real location.',
 '清除命令成功；请在手机地图确认真实定位': 'Clear command succeeded. Check the real location in Maps.',
 '已发送清除模拟定位命令。如地图缓存未刷新，请重新打开地图并等待真实定位。': 'Clear command sent. If Maps still shows the cached position, reopen it and '
                                         'request the current location.',
 '未知': 'Unknown',
 '已按本次授权查询电脑公网出口，IP 仅显示在界面，不写入日志。此结果不代表 iPhone 网络出口。': 'Public IP lookup completed for this computer. The IP is displayed '
                                                       'here only and is excluded from logs.',
 '请选择已经安装的 VPN/代理客户端 EXE。': 'Select an installed VPN or proxy client executable.',
 '已启动所选现有客户端。请在客户端内连接已有配置；本程序不确认或保证出口变化。': 'Client launched. Connect to an existing profile in the client to change network '
                                           'egress.',
 '纬度': 'Latitude',
 '经度': 'Longitude',
 '点击或拖动选择坐标，精确值可在上方输入。': 'Click or drag to select a point. Use the fields above for an exact position.'}

# Some backend messages combine stable phrases with a version, count or exit code.
_PARTS = re.compile('|'.join(re.escape(key) for key in sorted(EN,key=len,reverse=True)))

def translate(text, language):
    if language != 'en':
        return text
    if text in EN:
        return EN[text]
    return _PARTS.sub(lambda match: EN[match[0]], text).replace('）', ')')
