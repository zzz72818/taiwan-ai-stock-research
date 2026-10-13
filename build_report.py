"""Render cached FinMind responses into a dependency-free HTML research report."""
import json
from datetime import datetime, timezone
from pathlib import Path
from strategy import analyze

WATCHLIST = {'2330': '台積電', '2382': '廣達', '6669': '緯穎', '3017': '奇鋐'}


def main():
    stocks = []
    for symbol, name in WATCHLIST.items():
        path = Path('data') / f'{symbol}.json'
        try:
            payload = json.loads(path.read_text(encoding='utf-8-sig'))
            if payload.get('status') != 200 or not payload.get('data'):
                raise ValueError('來源未回傳有效資料')
            rows = sorted(payload['data'], key=lambda b: b['date'])
            if len({b['date'] for b in rows}) != len(rows):
                raise ValueError('日期重複')
            stocks.append(dict(symbol=symbol, name=name, bars=analyze(rows),
                               fetched=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()))
        except (OSError, ValueError, KeyError) as error:
            stocks.append(dict(symbol=symbol, name=name, error=str(error)))
    template = Path('report_template.html').read_text(encoding='utf-8')
    content = template.replace('__DATA__', json.dumps(stocks, ensure_ascii=False).replace('</', '<\\/'))
    Path('reports').mkdir(exist_ok=True)
    output = Path('reports/entry-dashboard.html')
    output.write_text(content, encoding='utf-8')
    for stock in stocks:
        if 'error' in stock:
            print(stock['symbol'], stock['error'])
        else:
            last = stock['bars'][-1]
            print(stock['symbol'], last['date'], 'bars=', len(stock['bars']),
                  'close=', last['close'], 'candidate=', last['signal'])
    print(output.resolve())


if __name__ == '__main__':
    main()
