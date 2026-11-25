import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import Backend, Runner, coordinates, redact, error_summary

class CoreTests(unittest.TestCase):
    def test_coordinates(self):
        self.assertEqual(coordinates('34.0528', '-118.2516'), (34.0528, -118.2516))
        for pair in [('nan',0), (0,'inf'), (91,0), (0,-181), ('x',0)]:
            with self.assertRaises(ValueError): coordinates(*pair)

    def test_privacy(self):
        samples = [
            'Identifier: 00000000-1111222233334444',
            'UniqueDeviceID: ' + 'a'*40,
            'DeviceName: Synthetic Private Phone',
            r'C:\Users\SyntheticUser\file.txt',
            '192.0.2.123', '2001:db8::1234',
            'IMEI: 123456789012345',
        ]
        forbidden = ['1111222233334444', 'a'*40, 'Synthetic Private Phone', 'SyntheticUser', '192.0.2.123', '2001:db8::1234', '123456789012345']
        out = redact('\n'.join(samples))
        for secret in forbidden: self.assertNotIn(secret, out)

    def test_unknown_error_never_echoes(self):
        self.assertNotIn('SECRET', error_summary('unknown SECRET device', 1))

    def test_runner_timeout_and_cancel(self):
        r = Runner()
        with self.assertRaisesRegex(RuntimeError, '超时'):
            r.run([sys.executable,'-c','import time; time.sleep(30)'], timeout=.15)
        errors = []
        def job():
            try: r.run([sys.executable,'-c','import time; time.sleep(30)'])
            except RuntimeError as e: errors.append(str(e))
        t = threading.Thread(target=job); t.start()
        deadline = time.monotonic()+3
        while r.active is None and time.monotonic()<deadline: time.sleep(.01)
        r.cancel(); t.join(5)
        self.assertFalse(t.is_alive()); self.assertTrue(errors)
        self.assertIsNone(r.active)

    def test_single_device_and_target_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = Backend(tmp, lambda *a: None)
            for out in ['[]', '["a","b"]', '{}']:
                with patch.object(b,'cli',return_value=out), self.assertRaises(RuntimeError): b.device()
            with patch.object(b,'cli',return_value='["synthetic"]'):
                self.assertEqual(b.device(), 'synthetic')
                with self.assertRaisesRegex(RuntimeError, '不同'): b.device('other')

    def test_clear_success_and_failure_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            events = []; b = Backend(tmp, lambda *a: events.append(a))
            b.recovery.write_text('{}')
            b.sim_target = 'synthetic'
            with patch.object(b,'profile',return_value=(26,7)), patch.object(b,'device',return_value='synthetic'), patch.object(b,'cli',side_effect=RuntimeError('failed')):
                with self.assertRaises(RuntimeError): b.clear_location()
            self.assertTrue(b.recovery.exists())
            with patch.object(b,'profile',return_value=(26,7)), patch.object(b,'device',return_value='synthetic'), patch.object(b,'cli',return_value='') as cli:
                b.clear_location()
                self.assertIn('clear', cli.call_args.args)
            self.assertFalse(b.recovery.exists())

    def test_simulation_arguments_and_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = Backend(tmp, lambda *a: None)
            # Real harmless subprocess checks stdin-driven shutdown and watcher lifecycle.
            original = b.runner.spawn
            calls=[]
            def spawn(argv):
                calls.append(argv)
                return original([sys.executable,'-u','-c',"print('Press ENTER to exit>', flush=True); input()"])
            with patch.object(b,'profile',return_value=(26,7)), patch.object(b,'verify_help'), patch.object(b,'device',return_value='synthetic'), patch.object(b.runner,'spawn',side_effect=spawn):
                b.set_location(34.0528,-118.2516)
                p=b.sim
                self.assertTrue(b.recovery.exists())
                self.assertEqual(calls[0][-3:], ['--','34.0528','-118.2516'])
                self.assertIn('--userspace', calls[0])
                time.sleep(.2); b.stop_sim()
                self.assertIsNotNone(p.poll())
                self.assertTrue(b.recovery.exists())

    def test_version_routes(self):
        for action in ('set','clear'):
            for version in [(15,8),(16,7),(17,0),(17,3),(17,4),(18,5),(26,7)]:
                args=Backend.location_command(version,'synthetic',action)
                self.assertIn(action,args)
                self.assertIn('synthetic',args)
                self.assertEqual('dvt' in args,version >= (17,0))
                self.assertEqual('--userspace' in args,version >= (17,4))
                self.assertEqual('--tunnel' in args,(17,0) <= version < (17,4))

    def test_no_network_before_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp, patch('urllib.request.urlopen') as request:
            Backend(tmp, lambda *a: None)
            request.assert_not_called()

    def test_legacy_set_returns_and_clear_recovers(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = Backend(tmp, lambda *args: None)
            with patch.object(b, 'device', return_value='synthetic'), patch.object(b, 'profile', return_value=(16,7)), patch.object(b,'verify_help'), patch.object(b,'cli',return_value='') as cli:
                b.set_location(35,-120)
                self.assertEqual(cli.call_args.args, ('developer','simulate-location','set','--udid','synthetic','--','35.0','-120.0'))
                self.assertTrue(b.recovery.exists())
                self.assertIsNone(b.sim)
                b.clear_location()
                self.assertFalse(b.recovery.exists())
                self.assertEqual(cli.call_args.args, ('developer','simulate-location','clear','--udid','synthetic'))

if __name__ == '__main__': unittest.main()
