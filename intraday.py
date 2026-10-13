"""Evaluate source-provided intraday quotes without inventing a live feed."""
from datetime import datetime, time
from math import isfinite
from zoneinfo import ZoneInfo
from strategy import analyze
from workflow import evaluate


def evaluate_quote(history, quote, now, symbol):
    result = dict(status='盤中行情未接入', provisional_candidate=False, entry_approved=False,
                  volume_ratio=None, price=None, timestamp=None, source=None)
    if quote is None:
        return result
    try:
        if now.tzinfo is None:
            raise ValueError('aware time required')
        local = now.astimezone(ZoneInfo('Asia/Taipei'))
        if local.weekday() >= 5 or not time(9) <= local.time().replace(tzinfo=None) <= time(13, 30):
            return dict(result, status='盤中監控時段外')
        timestamp = datetime.fromisoformat(quote['timestamp'])
        if timestamp.tzinfo is None or quote['symbol'] != symbol or not quote['source']:
            raise ValueError('invalid quote identity')
        age = (now - timestamp).total_seconds()
        if age < 0 or age > 120 or timestamp.astimezone(ZoneInfo('Asia/Taipei')).date() != local.date():
            return dict(result, status='報價日期或新鮮度異常')
        if not isinstance(quote['simulated'], bool):
            raise ValueError('simulated flag must be boolean')
        prices = [float(quote[k]) for k in ('price', 'open', 'high', 'low', 'volume_shares')]
        if not all(isfinite(v) for v in prices) or prices[-1] < 0:
            raise ValueError('invalid numbers')
        prior = sorted([b for b in history if b['date'] < local.date().isoformat()], key=lambda b: b['date'])
        if not prior or len({b['date'] for b in prior}) != len(prior):
            raise ValueError('missing or duplicate history')
        if (local.date() - datetime.fromisoformat(prior[-1]['date']).date()).days > 5:
            return dict(result, status='歷史資料待更新')
        current = dict(date=local.date().isoformat(), open=prices[1], max=prices[2], min=prices[3],
                       close=prices[0], Trading_Volume=prices[4])
        bar = analyze(prior + [current])[-1]
        assessment = evaluate(bar, local.date().isoformat())
        candidate = assessment['eligible']
        status = ('示範盤中候選' if quote['simulated'] else '盤中候選，待收盤確認') if candidate else '盤中等待條件'
        if assessment['status'] in ('風險暫緩', '資料不足'):
            status = assessment['status']
        return dict(result, status=status, provisional_candidate=candidate,
                    volume_ratio=bar['volume_ratio'], price=prices[0], timestamp=quote['timestamp'],
                    source=quote['source'], simulated=quote['simulated'], checks=assessment['checks'],
                    volume_definition='當日累計股數／前 20 日完整日均量，非同時段量比')
    except (ValueError, KeyError, TypeError):
        return dict(result, status='盤中報價格式異常')
