"""Desktop view for GeoShift. The map uses a bundled public-domain coastline."""
import tkinter as tk
from tkinter import ttk
from worldmap import WorldMap
from core import PRESETS, coordinates

BG = '#10151e'
NAV = '#151d28'
CARD = '#1c2533'
LINE = '#323e4e'
MUTED = '#a0afc2'
TEXT = '#edf3fa'
BLUE = '#84b7ff'
FONT = 'Microsoft YaHei UI'
PAGES = ['控制面板','设备管理','环境检测','网络配置','虚拟定位','运行日志','设置']
ICONS = ['\ue80f','\ue8ea','\ue950','\ue774','\ue707','\ue8a5','\ue713']

def label(parent, value='', *, variable=None, size=10, color=TEXT, bold=False, **kwargs):
    return tk.Label(parent, text=value, textvariable=variable, fg=color, bg=parent['bg'],
                    anchor='w', font=(FONT,size,'bold' if bold else 'normal'), **kwargs)

def card(parent, title):
    shell = tk.Frame(parent, bg=CARD, highlightbackground=LINE, highlightthickness=1)
    body = tk.Frame(shell, bg=CARD, padx=15, pady=10)
    body.pack(fill='both', expand=True)
    label(body,title,size=11,bold=True).pack(anchor='w',pady=(0,5))
    return shell,body

class Dashboard:
    def __init__(self,app):
        self.app=app
        app.configure(bg=BG)
        width=min(round(1080*app.scale), app.winfo_screenwidth()-32)
        height=min(round(860*app.scale), app.winfo_screenheight()-84)
        app.geometry(f'{width}x{height}')
        app.minsize(min(width,round(800*app.scale)),min(height,round(560*app.scale)))
        style=ttk.Style(app)
        style.theme_use('clam')
        style.configure('.',font=(FONT,10))
        style.configure('TButton',background='#29394d',foreground=TEXT,borderwidth=0,padding=(12,6))
        style.map('TButton',background=[('active','#364e6c'),('disabled','#222b39')],foreground=[('disabled','#8090a2')])
        style.configure('Primary.TButton',background='#2b5489',foreground='#f1f7ff')
        style.configure('TCombobox',fieldbackground=BG,foreground=TEXT,background=CARD,arrowcolor=BLUE)
        style.map('TCombobox',fieldbackground=[('readonly',BG)],foreground=[('readonly',TEXT)])
        app.option_add('*TCombobox*Listbox.background',CARD)
        app.option_add('*TCombobox*Listbox.foreground',TEXT)
        self.model=tk.StringVar(value='等待检测')
        self.os=tk.StringVar(value='连接并解锁 iPhone')
        self.checks={k:tk.StringVar(value='待检测') for k in ('Python','pymobiledevice3','Apple USB','开发者隧道')}
        top=tk.Frame(app,bg=CARD,padx=17,pady=7); top.pack(fill='x')
        label(top,'◎',size=17,color=BLUE).pack(side='left')
        label(top,'  虚拟定位助手',size=14,bold=True).pack(side='left')
        label(top,'   /   iOS Location Manager',color=MUTED).pack(side='left')
        self.language_button=ttk.Button(top,command=app.toggle_language)
        self.language_button.pack(side='right',padx=(12,0))
        label(top,'v0.3',color=MUTED).pack(side='right')
        bar=tk.Frame(app,bg=NAV,padx=14,pady=5); bar.pack(side='bottom',fill='x')
        app.cancel_button=ttk.Button(bar,text='取消当前操作',command=app.cancel,state='disabled')
        app.cancel_button.pack(side='right')
        label(bar,variable=app.status,color=BLUE,wraplength=610).pack(side='left')
        rail=tk.Frame(app,bg=NAV,width=round(156*app.scale)); rail.pack(side='left',fill='y'); rail.pack_propagate(False)
        credit=tk.Frame(rail,bg=NAV)
        credit.pack(side='bottom',fill='x',padx=9,pady=14)
        tk.Frame(credit,bg=LINE,height=1).pack(fill='x',pady=(0,7))
        label(credit,'开发者',size=9,color=BLUE).pack(anchor='w')
        label(credit,'Yan以及他忠实的AI大人',size=9,color=MUTED,
              wraplength=round(137*app.scale),justify='left').pack(anchor='w',pady=(2,0))
        self.nav={}
        for name,icon in zip(PAGES,ICONS):
            row=tk.Frame(rail,bg=NAV); row.pack(fill='x',padx=7,pady=(8,0))
            glyph=tk.Label(row,text=icon,font=('Segoe MDL2 Assets',13),fg=BLUE,bg=NAV); glyph.pack(side='left',padx=(10,3))
            button=tk.Button(row,text=name,command=lambda n=name:self.show(n),bg=NAV,fg=TEXT,
                    activebackground='#283d58',activeforeground=TEXT,font=(FONT,10,'bold'),anchor='w',relief='flat',bd=0,pady=7)
            button.pack(side='left',expand=True,fill='x')
            glyph.bind('<Button-1>',lambda e,n=name:self.show(n))
            self.nav[name]=(row,glyph,button)
        shell=tk.Frame(app,bg=BG); shell.pack(fill='both',expand=True)
        self.canvas=tk.Canvas(shell,bg=BG,highlightthickness=0)
        scroll=ttk.Scrollbar(shell,command=self.canvas.yview)
        scroll.pack(side='right',fill='y')
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(fill='both',expand=True)
        self.content=tk.Frame(self.canvas,bg=BG,padx=18,pady=12)
        win=self.canvas.create_window(0,0,anchor='nw',window=self.content)
        self.canvas.bind('<Configure>',lambda e:self.canvas.itemconfigure(win,width=e.width))
        self.content.bind('<Configure>',lambda e:self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        app.bind('<MouseWheel>',self.wheel,add='+')
        self.heading=label(self.content,'设备控制中心',size=21,bold=True)
        self.heading.pack(fill='x',pady=(0,10))
        self.sections={}
        pair=tk.Frame(self.content,bg=BG); self.sections['overview']=pair
        for i,(title,var,note) in enumerate([('USB 设备',self.model,self.os),('网络出口',app.ip,None)]):
            panel,body=card(pair,title); panel.grid(row=0,column=i,sticky='nsew',padx=(0,5) if not i else (5,0))
            pair.columnconfigure(i,weight=1,uniform='top')
            label(body,variable=var,size=14,color=BLUE,bold=True,wraplength=330).pack(anchor='w')
            label(body,'电脑公网 IP 与国家' if note is None else '',variable=note,color=MUTED).pack(anchor='w')
        env=self.section('env','运行环境')
        for name,var in self.checks.items():
            row=tk.Frame(env,bg=CARD);row.pack(fill='x')
            label(row,name).pack(side='left'); label(row,variable=var,color=BLUE).pack(side='right')
        row=self.row(env)
        self.action(row,'检测环境 / USB',self.diagnose,True)
        self.action(row,'安装隔离环境…',app.install)
        self.action(row,'检测开发者隧道',self.tunnel)
        gps=self.section('gps','虚拟定位')
        row=self.row(gps)
        label(row,'目标地区',color=MUTED).pack(side='left',padx=(0,8))
        country=self.countries=ttk.Combobox(row,state='readonly',width=14)
        country.pack(side='left',padx=(0,8));country.bind('<<ComboboxSelected>>',self.pick_country)
        app.cities=ttk.Combobox(row,state='readonly',width=16)
        app.cities.pack(side='left');app.cities.bind('<<ComboboxSelected>>',self.pick_city)
        fields=self.row(gps)
        for title,var in [('纬度',app.lat),('经度',app.lon)]:
            field=tk.Frame(fields,bg=BG,padx=10,pady=3); field.pack(side='left',fill='x',expand=True,padx=(0,6))
            label(field,title,size=9,color=MUTED).pack(anchor='w')
            tk.Entry(field,textvariable=var,fg=TEXT,bg=BG,insertbackground=TEXT,font=('Segoe UI',13),
                     width=9,bd=0,highlightthickness=0).pack(fill='x')
        actions=self.row(gps)
        self.action(actions,'开始静态定位',app.start,True)
        self.action(actions,'停止并恢复真实定位',app.clear)
        label(gps,'点击或拖动选择坐标，精确值可在上方输入。',color=MUTED).pack(anchor='w',pady=(8,2))
        self.map=WorldMap(gps,app)
        self.map.pack(fill='x',pady=(2,0))
        dev=self.section('dev','开发者模式')
        label(dev,'在 iOS 16 及以后版本，进入「设置 → 隐私与安全性 → 开发者模式」，开启后按手机提示重启并确认。',color=MUTED,wraplength=560,justify='left').pack(anchor='w')
        row=self.row(dev)
        self.action(row,'显示手机开关…',app.developer)
        self.action(row,'读取模式状态',lambda:app.work(lambda:app.backend.developer('developer-mode-status')))
        compat=self.section('compat','设备兼容性')
        for title,info in [('iOS 16 及以前','传统 USB 定位服务，需要匹配的开发者镜像。'),('iOS 17.0–17.3','Windows 需要事先启动管理员 tunneld 服务。'),('iOS 17.4 及以后','在受支持设备上自动建立用户空间隧道。'),('Android 真机','需在手机开发者选项选择模拟位置应用。本版提供 iPhone 控制。')]:
            label(compat,title,bold=True).pack(anchor='w',pady=(5,0))
            label(compat,info,color=MUTED,wraplength=540).pack(anchor='w')
        net=self.section('network','公网出口')
        label(net,'查询会向 ipapi.co 发送电脑的出口 IP。手机网络出口由手机自身的网络配置决定。',color=MUTED,wraplength=540,justify='left').pack(anchor='w')
        row=self.row(net); self.action(row,'授权查询公网 IP…',app.query_ip); self.action(row,'启动已有 VPN / 代理…',app.vpn)
        settings=self.section('settings','Python 解释器')
        label(settings,'手机后台优先使用已安装的独立环境。可在这里选择创建环境使用的 python.exe。',color=MUTED,wraplength=540).pack(anchor='w')
        self.action(self.row(settings),'选择基础 Python…',app.choose_python)
        notice=self.section('notice','发布声明')
        label(notice,'虚拟定位助手目前仅通过 GitHub 官方仓库发布。禁止二次转载或转售本软件。',color=MUTED,wraplength=540,justify='left').pack(anchor='w')
        logs=self.section('log','脱敏事件记录')
        app.logbox=tk.Text(logs,state='disabled',height=14,bg=BG,fg=TEXT,font=(FONT,10),relief='flat',padx=10,pady=8,wrap='word')
        app.logbox.pack(fill='x')
        ttk.Button(self.row(logs),text='导出脱敏日志…',command=app.export).pack(side='left')
        self.static=[]
        self.dynamic=[]
        self.capture_text(app)
        self.show(PAGES[0])
        self.refresh_language()

    def capture_text(self,parent):
        # Keep source variables canonical. Translate only their display mirrors.
        for widget in parent.winfo_children():
            self.capture_text(widget)
            if not isinstance(widget,(tk.Label,tk.Button,ttk.Button)):continue
            if widget is self.language_button or widget is self.heading:continue
            var=widget.cget('textvariable')
            if var:
                source=tk.StringVar(self.app,name=str(var))
                display=tk.StringVar(self.app)
                def update(*_,src=source,dst=display):
                    dst.set(self.app.tr(src.get()))
                source.trace_add('write',update)
                widget.configure(textvariable=display)
                self.dynamic.append((source,display,update))
            else:
                self.static.append((widget,widget.cget('text')))

    def refresh_language(self):
        for widget,text in self.static:widget.configure(text=self.app.tr(text))
        for _,__,update in self.dynamic:update()
        self.language_button.configure(text='English' if self.app.language=='zh' else '中文')
        self.heading.configure(text=self.app.tr('设备控制中心' if self.page==PAGES[0] else self.page))
        self.refresh_presets()

    def refresh_presets(self):
        country=self.app.country.get()
        self.countries.configure(values=[self.app.tr(k) for k in PRESETS])
        self.countries.current(list(PRESETS).index(country))
        names=list(PRESETS[country])
        self.app.cities.configure(values=[self.app.tr(k) for k in names])
        self.app.cities.current(names.index(self.app.city.get()))

    def pick_country(self,_):
        self.app.country.set(list(PRESETS)[self.countries.current()])
        self.app.change_country()

    def pick_city(self,_):
        self.app.city.set(list(PRESETS[self.app.country.get()])[self.app.cities.current()])
        self.app.change_city()

    def wheel(self,e):
        if e.widget.winfo_toplevel()==self.app and e.widget.winfo_class() not in ('Text','TCombobox'):
            self.canvas.yview_scroll(-int(e.delta/120),'units')

    def row(self,parent):
        row=tk.Frame(parent,bg=parent['bg']); row.pack(fill='x',pady=(6,0)); return row

    def section(self,key,title):
        shell,body=card(self.content,title)
        self.sections[key]=shell
        return body

    def action(self,row,title,command,primary=False):
        b=ttk.Button(row,text=title,command=command,style='Primary.TButton' if primary else 'TButton')
        b.pack(side='left',padx=(0,7)); self.app.buttons.append(b)

    def show(self,name):
        sections={
          '控制面板':('overview','env','gps'),'设备管理':('overview','dev','compat'),
          '环境检测':('env','settings'),'网络配置':('overview','network'),
          '虚拟定位':('gps','dev'),'运行日志':('log',),'设置':('settings','notice','compat')}
        for key,widgets in self.nav.items():
            for w in widgets:w.configure(bg='#263e60' if key==name else NAV)
        self.page=name
        self.heading.configure(text=self.app.tr('设备控制中心' if name=='控制面板' else name))
        for p in self.sections.values():p.pack_forget()
        for k in sections[name]:self.sections[k].pack(fill='x',pady=(0,9))
        self.canvas.yview_moveto(0)

    def diagnose(self):
        self.model.set('检测中…'); self.os.set('正在读取 USB 信息')
        for var in self.checks.values():var.set('待检测')
        def finished(ok):
            if not ok and self.model.get()=='检测中…':
                self.model.set('未确认设备'); self.os.set('请检查 USB 与信任状态')
        self.app.work(self.app.backend.diagnose,finished)

    def tunnel(self):
        self.checks['开发者隧道'].set('检测中…')
        def finished(ok):
            if not ok:self.checks['开发者隧道'].set('检测失败')
        self.app.work(self.app.backend.tunnel,finished)

