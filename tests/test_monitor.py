import tempfile
import unittest
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from monitor import refresh, atomic_json
from unittest.mock import patch


class MonitorTests(unittest.TestCase):
    def test_transient_file_lock_is_retried(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent) as tmp:
            original = Path.replace
            attempts = []
            def replace(path, target):
                attempts.append(target)
                if len(attempts) == 1:
                    raise PermissionError('temporary lock')
                return original(path, target)
            with patch.object(Path, 'replace', replace):
                atomic_json(Path(tmp) / 'state.json', {'success': True})
            self.assertEqual(len(attempts), 2)

    def payload(self):
        from datetime import date, timedelta
        rows = [dict(date=(date(2026, 7, 1)+timedelta(days=i)).isoformat(),
                     open=100, max=101, min=99, close=100, Trading_Volume=1000)
                for i in range(65)]
        rows[-1].update(close=105, max=106, Trading_Volume=2000)
        return dict(status=200, data=rows)

    def test_refresh_changes_deduplicates_and_recovers(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent) as tmp:
            root = Path(tmp)
            now = datetime(2026, 9, 4, 19, tzinfo=ZoneInfo('Asia/Taipei'))
            fetch = lambda symbol: self.payload()
            refresh(root, now, fetch, {'2330': '台積電'})
            events = root / 'reports/events.jsonl'
            self.assertEqual(len(events.read_text(encoding='utf-8').splitlines()), 1)
            refresh(root, now, fetch, {'2330': '台積電'})
            self.assertEqual(len(events.read_text(encoding='utf-8').splitlines()), 1)
            def fail(symbol):
                raise OSError('network down')
            state = refresh(root, now, fail, {'2330': '台積電'})
            self.assertEqual(state['2330']['status'], '更新失敗')
            self.assertTrue((root / 'data/2330.json').exists())
            refresh(root, now, fetch, {'2330': '台積電'})
            self.assertEqual(len(events.read_text(encoding='utf-8').splitlines()), 3)

    def test_current_day_excluded_before_cutoff(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent) as tmp:
            now = datetime(2026, 9, 3, 10, tzinfo=ZoneInfo('Asia/Taipei'))
            state = refresh(Path(tmp), now, lambda symbol: self.payload(), {'2330': '台積電'})
            self.assertEqual(state['2330']['data_date'], '2026-09-02')

    def test_partial_failure_does_not_stop_other_stock(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent) as tmp:
            def fetch(symbol):
                if symbol == '2330':
                    raise OSError('offline')
                return self.payload()
            now = datetime(2026, 9, 4, 19, tzinfo=ZoneInfo('Asia/Taipei'))
            state = refresh(Path(tmp), now, fetch, {'2330': '台積電', '2382': '廣達'})
            self.assertEqual(state['2330']['status'], '更新失敗')
            self.assertEqual(state['2382']['status'], '候選，待盤前確認')
