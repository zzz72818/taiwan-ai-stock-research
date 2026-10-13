import unittest
from datetime import datetime, timedelta
from intraday import evaluate_quote


class IntradayTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.fromisoformat('2026-10-14T10:00:00+08:00')
        start = self.now.date() - timedelta(days=65)
        self.bars = [dict(date=(start+timedelta(days=i)).isoformat(), open=100,
                          max=101, min=99, close=100, Trading_Volume=1000) for i in range(65)]
        self.quote = dict(symbol='2330', timestamp=self.now.isoformat(), price=105,
                          open=100, high=106, low=99, volume_shares=2000,
                          source='test-fixture', simulated=True)

    def test_provisional_signal_never_becomes_confirmed_entry(self):
        result = evaluate_quote(self.bars, self.quote, self.now, '2330')
        self.assertEqual(result['status'], '示範盤中候選')
        self.assertFalse(result['entry_approved'])
        self.assertTrue(result['provisional_candidate'])

    def test_missing_stale_future_wrong_symbol_blocked(self):
        self.assertEqual(evaluate_quote(self.bars, None, self.now, '2330')['status'], '盤中行情未接入')
        for field, value in [('timestamp',(self.now-timedelta(minutes=5)).isoformat()),
                             ('timestamp',(self.now+timedelta(minutes=5)).isoformat()),
                             ('symbol','2382')]:
            quote = dict(self.quote, **{field:value})
            result = evaluate_quote(self.bars, quote, self.now, '2330')
            self.assertFalse(result['provisional_candidate'])

    def test_volume_is_not_projected_from_time_of_day(self):
        result = evaluate_quote(self.bars, dict(self.quote, volume_shares=200), self.now, '2330')
        self.assertEqual(result['volume_ratio'], 0.2)
        self.assertEqual(result['status'], '盤中等待條件')

    def test_outside_session_blocks(self):
        now = self.now.replace(hour=15)
        self.assertEqual(evaluate_quote(self.bars, self.quote, now, '2330')['status'], '盤中監控時段外')

    def test_same_day_history_is_excluded(self):
        bars = self.bars + [dict(date=self.now.date().isoformat(), open=100,
                                 max=1000, min=99, close=900, Trading_Volume=99999)]
        self.assertEqual(evaluate_quote(self.bars,self.quote,self.now,'2330'),
                         evaluate_quote(bars,self.quote,self.now,'2330'))
