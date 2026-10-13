"""Render cached FinMind responses into a dependency-free HTML research report."""
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from strategy import analyze
from workflow import evaluate

WATCHLIST = {'2330': '台積電', '2382': '廣達', '6669': '緯穎', '3017': '奇鋐'}


def main():
    stocks = []
    as_of = datetime.now(ZoneInfo('Asia/Taipei')).date().isoformat()
    state_path = Path('reports/monitor-state.json')
    monitor_state = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else {}
    events_path = Path('reports/events.jsonl')
    events = [json.loads(line) for line in events_path.read_text(encoding='utf-8').splitlines() if line] if events_path.exists() else []
    for symbol, name in WATCHLIST.items():
        path = Path('data') / f'{symbol}.json'
        try:
            payload = json.loads(path.read_text(encoding='utf-8-sig'))
            if payload.get('status') != 200 or not payload.get('data'):
                raise ValueError('來源未回傳有效資料')
            rows = sorted(payload['data'], key=lambda b: b['date'])
            if len({b['date'] for b in rows}) != len(rows):
                raise ValueError('日期重複')
            analyzed = analyze(rows)
            assessment = evaluate(analyzed[-1], as_of)
            update = monitor_state.get(symbol)
            if update and not update['success']:
                assessment.update(status='更新失敗', eligible=False)
                assessment['risks'].append('目前顯示舊快取，最新來源更新失敗')
            stocks.append(dict(symbol=symbol, name=name, bars=analyzed,
                               assessment=assessment, monitor=update,
                               events=[event for event in events if event['symbol'] == symbol][-8:],
                               fetched=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()))
        except (OSError, ValueError, KeyError) as error:
            stocks.append(dict(symbol=symbol, name=name, error=str(error)))
    template = Path('report_template.html').read_text(encoding='utf-8')
    content = template.replace('__DATA__', json.dumps(stocks, ensure_ascii=False).replace('</', '<\\/'))
    Path('reports').mkdir(exist_ok=True)
    output = Path('reports/entry-dashboard.html')
    temporary = output.with_suffix('.tmp')
    temporary.write_text(content, encoding='utf-8')
    temporary.replace(output)
    signals = Path('reports/signals.json')
    temporary = signals.with_suffix('.tmp')
    temporary.write_text(json.dumps([
        {k: v for k, v in stock.items() if k != 'bars'} for stock in stocks
    ], ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(signals)
    for stock in stocks:
        if 'error' in stock:
            print(stock['symbol'], stock['error'])
        else:
            last = stock['bars'][-1]
            print(stock['symbol'], last['date'], 'bars=', len(stock['bars']),
                  'close=', last['close'], 'status=', stock['assessment']['status'])
    print(output.resolve())


if __name__ == '__main__':
    main()
