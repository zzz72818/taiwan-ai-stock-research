import unittest
from strategy import analyze


class StrategyTests(unittest.TestCase):
    def bars(self):
        return [dict(date=f"day-{i}", open=100, max=101, min=99,
                     close=100, Trading_Volume=1000) for i in range(65)]

    def test_breakout_uses_previous_bars(self):
        bars = self.bars()
        bars[-1].update(close=105, max=106, Trading_Volume=2000)
        result = analyze(bars)[-1]
        self.assertTrue(result['signal'])
        self.assertEqual(result['breakout'], 101)

    def test_future_bars_do_not_change_past_signal(self):
        bars = self.bars()
        before = analyze(bars)
        bars.append(dict(date='future', open=1000, max=1001, min=999,
                         close=1000, Trading_Volume=99999))
        self.assertEqual(before, analyze(bars)[:-1])

    def test_insufficient_history_never_signals(self):
        self.assertFalse(any(b['signal'] for b in analyze(self.bars()[:59])))

    def test_no_breakout_no_signal(self):
        self.assertFalse(any(b['signal'] for b in analyze(self.bars())))

    def test_bad_price_rejected(self):
        bars = self.bars()
        bars[-1]['close'] = -1
        with self.assertRaises(ValueError):
            analyze(bars)

    def test_wide_range_is_not_consolidation(self):
        bars = self.bars()
        bars[-10]['min'] = 70
        bars[-1].update(close=105, max=106, Trading_Volume=2000)
        self.assertFalse(analyze(bars)[-1]['signal'])

    def test_small_breakout_and_weak_volume_rejected(self):
        bars = self.bars()
        bars[-1].update(close=101.2, max=102, Trading_Volume=2000)
        self.assertFalse(analyze(bars)[-1]['signal'])
        bars[-1].update(close=105, max=106, Trading_Volume=1400)
        self.assertFalse(analyze(bars)[-1]['signal'])


if __name__ == '__main__':
    unittest.main()
