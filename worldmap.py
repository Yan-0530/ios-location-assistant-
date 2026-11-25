"""Geographic overview with a shared equirectangular drawing and picking transform."""
import tkinter as tk
from coastline import LAND
from core import coordinates

def viewport(width,height):
    scale=min((width-2)/360,(height-2)/180)
    return (width-360*scale)/2,(height-180*scale)/2,scale

class WorldMap(tk.Canvas):
    def __init__(self,parent,app):
        super().__init__(parent,height=280,bg='#142432',highlightthickness=0,cursor='crosshair')
        self.app=app
        self.dragging=False
        self.bind('<Configure>',self.resize)
        self.bind('<ButtonPress-1>',self.press)
        self.bind('<B1-Motion>',self.move)
        self.bind('<ButtonRelease-1>',self.release)
        for var in (app.lat,app.lon):
            var.trace_add('write',self.marker)

    def resize(self,event):
        w,h=event.width,event.height
        desired=max(100,min(w//2,round(self.app.scale*390)))
        if abs(desired-int(self.cget('height')))>1:
            self.configure(height=desired)
        if min(w,h)<4:return
        self.delete('all')
        x,y,s=viewport(w,h)
        self.create_rectangle(x,y,x+360*s,y+180*s,fill='#172c3b',outline='#354e60')
        for lon in range(30,360,30):
            self.create_line(x+lon*s,y,x+lon*s,y+180*s,fill='#254050')
        for lat in range(30,180,30):
            self.create_line(x,y+lat*s,x+360*s,y+lat*s,fill='#254050')
        for ring in LAND:
            coords=[y+(90-n)*s if i%2 else x+(180+n)*s for i,n in enumerate(ring)]
            self.create_polygon(coords,fill='#446071',outline='')
        self.marker()

    def marker(self,*_):
        self.delete('pin')
        try:lat,lon=coordinates(self.app.lat.get(),self.app.lon.get())
        except ValueError:return
        x,y,s=viewport(self.winfo_width(),self.winfo_height())
        if s<=0:return
        px,py=x+(lon+180)*s,y+(90-lat)*s
        self.create_line(px,y,px,y+180*s,fill='#86b4cc',dash=(3,5),tags='pin')
        self.create_line(x,py,x+360*s,py,fill='#86b4cc',dash=(3,5),tags='pin')
        r=5*self.app.scale
        self.create_oval(px-r,py-r,px+r,py+r,fill='#76c1ff',outline='white',width=2,tags='pin')

    def press(self,e):
        x,y,s=viewport(self.winfo_width(),self.winfo_height())
        self.dragging=s>0 and x<=e.x<=x+360*s and y<=e.y<=y+180*s
        if self.dragging:self.move(e)

    def move(self,e):
        if not self.dragging:return
        x,y,s=viewport(self.winfo_width(),self.winfo_height())
        if s<=0:return
        lon=max(-180,min(180,(e.x-x)/s-180))
        lat=max(-90,min(90,90-(e.y-y)/s))
        self.app.set_custom(lat,lon)

    def release(self,e):
        self.move(e)
        self.dragging=False
