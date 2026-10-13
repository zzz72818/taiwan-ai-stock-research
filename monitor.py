"""Continuously refresh completed daily bars and record state changes locally."""
import argparse
import functools
import json
import os
import threading
import time
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
from strategy import analyze
from workflow import evaluate
from build_report import WATCHLIST
from file_io import replace_with_retry


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    replace_with_retry(temporary, path)


def fetch_data(symbol):
    query = urlencode(dict(dataset='TaiwanStockPrice', data_id=symbol, start_date='2025-01-01'))
    headers = {'User-Agent': 'TaiwanAIStockResearch/0.2'}
    if os.getenv('FINMIND_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['FINMIND_TOKEN']
    request = Request('https://api.finmindtrade.com/api/v4/data?' + query, headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def refresh(root, now, fetch=fetch_data, watchlist=WATCHLIST):
    state_path = root / 'reports/monitor-state.json'
    previous = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else {}
    state = {}
    for symbol in watchlist:
        try:
            payload = fetch(symbol)
            if payload.get('status') != 200 or not payload.get('data'):
                raise ValueError('來源沒有有效資料')
            rows = sorted(payload['data'], key=lambda b: b['date'])
            rows = [b for b in rows if b['date'] < now.date().isoformat() or
                    (b['date'] == now.date().isoformat() and now.hour >= 18)]
            if not rows or len({b['date'] for b in rows}) != len(rows):
                raise ValueError('資料缺失或日期重複')
            bars = analyze(rows)
            assessment = evaluate(bars[-1], now.date().isoformat())
            state[symbol] = dict(status=assessment['status'], data_date=rows[-1]['date'],
                                 checked_at=now.isoformat(), success=True,
                                 source_latest_date=max(b['date'] for b in payload['data']))
            atomic_json(root / f'data/{symbol}.json', dict(status=200, data=rows))
        except Exception as error:
            # Network and malformed data are isolated per symbol; old cache is never called fresh.
            state[symbol] = dict(status='更新失敗', success=False, checked_at=now.isoformat(),
                                 data_date=previous.get(symbol, {}).get('data_date'),
                                 error=type(error).__name__)
        old = previous.get(symbol, {})
        current = state[symbol]
        if (old.get('status'), old.get('data_date')) != (current['status'], current.get('data_date')):
            events = root / 'reports/events.jsonl'
            events.parent.mkdir(parents=True, exist_ok=True)
            with events.open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(dict(symbol=symbol, name=watchlist[symbol],
                                            previous_status=old.get('status'), **current), ensure_ascii=False) + '\n')
    atomic_json(state_path, state)
    return state


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--interval', type=int, default=900, help='poll seconds, minimum 60')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--cycles', type=int, help='optional bounded verification run')
    args = parser.parse_args()
    if args.interval < 60 or (args.cycles is not None and args.cycles < 1):
        parser.error('interval >= 60 and cycles >= 1 required')
    root = Path(__file__).resolve().parent
    os.chdir(root)
    (root / 'reports').mkdir(exist_ok=True)
    server = None
    if not args.once:
        handler = functools.partial(Handler, directory=str(root / 'reports'))
        server = ThreadingHTTPServer(('127.0.0.1', args.port), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        print(f'http://127.0.0.1:{args.port}/entry-dashboard.html', flush=True)
    cycles = 0
    try:
        while True:
            now = datetime.now(ZoneInfo('Asia/Taipei'))
            state = refresh(root, now)
            from build_report import main as build
            build()
            print(json.dumps(dict(cycle=cycles+1, checked_at=now.isoformat(), stocks=state), ensure_ascii=False), flush=True)
            cycles += 1
            if args.once or (args.cycles and cycles >= args.cycles):
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print('Monitor stopped', flush=True)
    finally:
        if server:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    main()
