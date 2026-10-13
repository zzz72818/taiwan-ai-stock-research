# AI 台股盤前進場研究

追蹤台積電 2330、廣達 2382、緯穎 6669、奇鋐 3017，以日線產生隔日波段進場候選。第一版是可在瀏覽器開啟的互動研究報告，不需 Python 第三方套件。

## 執行（Windows / Python 3.10+）

在專案根目錄執行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/download.ps1
python build_report.py
python -m unittest discover -s tests -v
```

以瀏覽器開啟 `reports/entry-dashboard.html`，切換股票、資料範圍與查看游標數據。若 python 指令不可用，改成實際 Python 執行檔完整路徑。

資料來源：[FinMind API](https://finmind.github.io/quickstart/)。可選擇以 FINMIND_TOKEN 環境變數設定自己的 token；請勿寫入程式碼。上述下載／報告指令是單次執行，啟動下方 monitor.py 才會持續更新；來源不是盤中行情。

## 研究規則

### 規則式分析流程

參考 [TradingAgents](https://github.com/TauricResearch/TradingAgents) 的分析、多空研究與風險決策分工，自行實作 `workflow.py`，不需模型 API。

流程：技術條件 → 支持／未達條件 → 資料與波動風險 → 待確認決策。畫面顯示四檔總覽與每項條件，`reports/signals.json` 保存相同評估供其他工具讀取。

初始風險門檻：距資料日超過 5 個日曆日則待更新；ATR14／收盤超過 6% 則暫緩。這些門檻尚未回測，日曆間隔不取代交易日完整性驗證。分析日期採台灣日期，舊報告跨日會提示重新產生。新聞、財報、持倉未接入，需人工複核，候選不等於已核准下單。

前 20 日最高最低差／平均收盤不超過 12%（盤整），收盤超過前 20 日最高價 0.5%，收盤高於 MA20、MA20 高於 MA60、成交量為前 20 日均量至少 1.5 倍。先暖機 60 筆。訊號只能作為下一交易日的待確認候選，不代表當日成交。圖表同時顯示含當日的下一次觀察門檻。

## 持續追蹤

```powershell
python monitor.py
```

開啟 http://127.0.0.1:8765/entry-dashboard.html 。每 15 分鐘查詢四檔日線，頁面每 60 秒重新載入；僅監控程序運行時持續更新，Ctrl+C 停止。電腦休眠或關機時停止，未建立自動啟動服務。

Windows 背景啟動可用 `powershell -ExecutionPolicy Bypass -File scripts/start-monitor.ps1 -PythonPath "你的 python.exe 完整路徑"`；停止用 `powershell -ExecutionPolicy Bypass -File scripts/stop-monitor.ps1`。程式輸出保存於 `reports/monitor.log`，錯誤於 `reports/monitor-error.log`。啟動後請檢查頁面最近查詢時間與日誌，不把程序啟動訊息當作資料成功保證。

這是「收盤確認」策略，不是即時盤中行情。台灣時間 18:00 前排除當日日線，避免未完成資料影響訊號；18:00 是保守截點，不是來源發布保證。每次顯示來源最新日與實際分析資料日。盤中即時突破監控仍需額外行情來源。

單次更新用 `python monitor.py --once`；輪詢頻率可用 `--interval 900` 設定，最少 60 秒。資料錯誤時保留舊快取但阻止候選狀態，畫面顯示更新失敗。`reports/events.jsonl` 保存首次觀察與資料日／狀態變化，同一日同狀態不重複記錄，`reports/monitor-state.json` 保存最新抓取狀態。事件是歷史觀察，不能作為當前進場許可。

### 盤中來源狀態

尚未開通行情服務，因此真實盘中追蹤未完成。已提供 `intraday.evaluate_quote` 判斷介面；`data/intraday-quotes.json` 可由有權限的來源 adapter 寫入。頂層以股票代號為 key，每筆必須有 symbol、timestamp（含時區）、price、open、high、low、volume_shares（當日累計股數）、source、simulated（布林）。本專案目前不附已連線的 adapter，也不自動開戶或訂閱。

盤中判斷拒絕超過 120 秒、未來時間、股票不符及當日未完成歷史資料；台灣普通時段之外不判定。成交量使用累計量／前 20 日完整日均量，沒有同時段歷史資料時不推估同時段量比。候選需收盤確認，無交易許可。正式交易日、盤中風控與真实行情接入仍需驗證。

原始價格尚未調整除權息；規則尚未完成績效回測、價格區間、停損、資金與風險設定。資料新鮮度以圖上日期為準。第一版不實際下單。

## GitHub

公開 repository： https://github.com/zzz72818/taiwan-ai-stock-research 。只上傳程式、文件與測試；`.gitignore` 排除行情快取、生成報告、金鑰與診斷資料。程式碼授權尚未指定。

完整月計畫：`docs/plans/2026-10-13-stock-project-roadmap.md`。
