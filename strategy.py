"""Daily, long-only entry candidates. No execution or return claims."""
from statistics import mean
from math import isfinite

VOLUME_RATIO = 1.5
BREAKOUT_BUFFER = 0.005
MAX_CONSOLIDATION_RANGE = 0.12


def analyze(bars):
    result, ranges = [], []
    for i, bar in enumerate(bars):
        high, low, close = (float(bar[k]) for k in ('max', 'min', 'close'))
        if not all(isfinite(float(bar[k])) for k in ('open', 'max', 'min', 'close', 'Trading_Volume')) or not 0 < low <= close <= high or not low <= float(bar['open']) <= high or float(bar['Trading_Volume']) < 0:
            raise ValueError('Invalid OHLC or volume')
        previous_close = float(bars[i - 1]['close']) if i else close
        ranges.append(max(high - low, abs(high - previous_close), abs(low - previous_close)))
        ma20 = mean(float(b['close']) for b in bars[i-19:i+1]) if i >= 19 else None
        ma60 = mean(float(b['close']) for b in bars[i-59:i+1]) if i >= 59 else None
        prior = bars[i-20:i] if i >= 20 else []
        breakout = max(float(b['max']) for b in prior) if prior else None
        volume_mean = mean(float(b['Trading_Volume']) for b in prior) if prior else None
        ratio = float(bar['Trading_Volume']) / volume_mean if volume_mean else None
        consolidation_range = ((breakout - min(float(b['min']) for b in prior)) /
                               mean(float(b['close']) for b in prior)) if prior else None
        consolidation = consolidation_range is not None and consolidation_range <= MAX_CONSOLIDATION_RANGE
        atr = mean(ranges[-14:]) if i >= 13 else None
        trend = ma60 is not None and close > ma20 > ma60
        signal = bool(trend and consolidation and breakout is not None and
                      close > breakout * (1 + BREAKOUT_BUFFER) and ratio is not None and ratio >= VOLUME_RATIO)
        next_trigger = max(float(b['max']) for b in bars[max(0, i-19):i+1]) if i >= 19 else None
        result.append(dict(**bar, ma20=ma20, ma60=ma60, breakout=breakout,
                           volume_ratio=ratio, atr=atr, trend=trend, signal=signal,
                           consolidation=consolidation, consolidation_range=consolidation_range,
                           next_trigger=next_trigger))
    return result
