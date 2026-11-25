"""Offline UI contract tests: no device mutation, installation or network access."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import App

class GuiTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.app=App(self.tmp.name); self.app.update()
    def tearDown(self):
        self.app.destroy(); self.tmp.cleanup()
    def test_declining_install_and_ip_does_nothing(self):
        with patch('main.messagebox.askyesno',return_value=False), patch.object(self.app,'work') as work:
            self.app.install(); self.app.query_ip(); work.assert_not_called()
    def test_negative_coordinate_preset_and_custom_validation(self):
        self.app.country.set('美国'); self.app.change_country()
        self.assertEqual(self.app.lon.get(),'-118.2516')
        self.app.lat.set('nan')
        with patch('main.messagebox.showerror') as error, patch.object(self.app,'work') as work:
            self.app.start(); error.assert_called_once(); work.assert_not_called()
    def test_footer_visible(self):
        self.assertTrue(self.app.cancel_button.winfo_viewable())
        self.assertLess(self.app.cancel_button.winfo_rooty()+self.app.cancel_button.winfo_height(), self.app.winfo_rooty()+self.app.winfo_height())

    def test_map_drag_updates_custom_point_without_device_command(self):
        from worldmap import viewport
        view=self.app.dashboard
        view.show('虚拟定位')
        self.app.update()
        canvas=view.map
        x,y,s=viewport(canvas.winfo_width(),canvas.winfo_height())
        with patch.object(self.app,'work') as work:
            canvas.event_generate('<ButtonPress-1>',x=round(x+180*s),y=round(y+90*s))
            canvas.event_generate('<B1-Motion>',x=round(x+140*s),y=round(y+110*s))
            canvas.event_generate('<ButtonRelease-1>',x=round(x+140*s),y=round(y+110*s))
            self.assertAlmostEqual(float(self.app.lat.get()),-20,delta=0.51/s)
            self.assertAlmostEqual(float(self.app.lon.get()),-40,delta=0.51/s)
            self.assertEqual(self.app.country.get(),'自定义')
            work.assert_not_called()

    def test_switch_preserves_page_coordinates_and_consent(self):
        app=self.app
        view=app.dashboard
        view.show('虚拟定位')
        app.set_custom(48.8566,2.3522)
        view.language_button.invoke()
        self.assertEqual(view.heading.cget('text'),'Location')
        self.assertEqual(view.countries.get(),'Custom')
        self.assertEqual(app.cities.get(),'Custom coordinates')
        self.assertEqual(float(app.lon.get()),2.3522)
        with patch('main.messagebox.askyesno',return_value=False) as consent, patch.object(app,'work') as work:
            app.query_ip()
            self.assertEqual(consent.call_args.args[0],'Allow public IP lookup')
            work.assert_not_called()
        self.assertEqual(app.pref_path.read_text('ascii'),'en')
        app.toggle_language()
        self.assertEqual(view.heading.cget('text'),'虚拟定位')
        self.assertEqual(view.countries.get(),'自定义')

if __name__=='__main__': unittest.main()
