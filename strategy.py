"""Daily, long-only entry candidates. No execution or return claims."""
from statistics import mean


def analyze(bars):
    result, ranges = [], []
    for i, bar in enumerate(bars):
        high, low, close = (float(bar[k]) for k in ('max', 'min', 'close'))
        if not 0 < low <= close <= high or float(bar['Trading_Volume']) < 0:
            raise ValueError('Invalid OHLC or volume')
        previous_close = float(bars[i - 1]['close']) if i else close
        ranges.append(max(high - low, abs(high - previous_close), abs(low - previous_close)))
        ma20 = mean(float(b['close']) for b in bars[i-19:i+1]) if i >= 19 else None
        ma60 = mean(float(b['close']) for b in bars[i-59:i+1]) if i >= 59 else None
        prior = bars[i-20:i] if i >= 20 else []
        breakout = max(float(b['max']) for b in prior) if prior else None
        volume_mean = mean(float(b['Trading_Volume']) for b in prior) if prior else None
        ratio = float(bar['Trading_Volume']) / volume_mean if volume_mean else None
        atr = mean(ranges[-14:]) if i >= 13 else None
        trend = ma60 is not None and close > ma20 > ma60
        signal = bool(trend and breakout is not None and close > breakout and ratio is not None and ratio >= 1.2)
        next_trigger = max(float(b['max']) for b in bars[max(0, i-19):i+1]) if i >= 19 else None
        result.append(dict(**bar, ma20=ma20, ma60=ma60, breakout=breakout,
                           volume_ratio=ratio, atr=atr, trend=trend, signal=signal,
                           next_trigger=next_trigger))
    return result
