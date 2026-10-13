import unittest
from workflow import evaluate


class WorkflowTests(unittest.TestCase):
    def snapshot(self):
        return dict(date='2026-10-13', close=105, ma20=101, ma60=100,
                    breakout=104, volume_ratio=1.5, atr=2, signal=True,
                    consolidation=True, consolidation_range=0.02)

    def test_candidate_requires_all_checks(self):
        result = evaluate(self.snapshot(), '2026-10-13')
        self.assertEqual(result['status'], '候選，待盤前確認')
        self.assertEqual(len(result['checks']), 6)
        self.assertTrue(result['manual_review'])

    def test_stale_data_blocks_candidate(self):
        result = evaluate(self.snapshot(), '2026-10-20')
        self.assertEqual(result['status'], '資料待更新')
        self.assertFalse(result['eligible'])

    def test_future_data_is_invalid(self):
        self.assertEqual(evaluate(self.snapshot(), '2026-10-12')['status'], '資料日期異常')

    def test_high_volatility_blocks_candidate(self):
        bar = self.snapshot()
        bar['atr'] = 10
        self.assertEqual(evaluate(bar, '2026-10-13')['status'], '風險暫緩')

    def test_volume_failure_is_explained(self):
        bar = self.snapshot()
        bar['volume_ratio'] = 1.0
        result = evaluate(bar, '2026-10-13')
        self.assertEqual(result['status'], '等待條件')
        self.assertIn('成交量確認', result['bear'])

    def test_insufficient_history_is_not_a_candidate(self):
        bar = self.snapshot()
        bar['ma60'] = None
        self.assertEqual(evaluate(bar, '2026-10-13')['status'], '資料不足')


if __name__ == '__main__':
    unittest.main()
