# 盤中訊號介面與來源前置調查

待使用者提供券商／行情服務名稱，不自行登入私人帳戶或購買資料。

先實作來源無關的盤中報價評估介面，使用資料契約：symbol、timestamp（含時區）、price、open、high、low、volume_shares（當日累計股數）、source、simulated。盤中價格與量來自報價；歷史只用當日前的日線。

1. 測試缺報價、過期、未來時間、股票不符、未完成日線排除與成交量不外推。
2. intraday.py 計算「盤中候選，待收盤確認」，不等同已核准進場。採台灣普通交易時段 09:00–13:30，週末排除；此時段檢查不取代正式交易日／停牌驗證。
3. source file data/intraday-quotes.json 由獲授權來源的 adapter 寫入；缺失時顯示未接入。未提供 adapter 前不聲稱真實盤中追蹤完成。
4. 圖表顯示報價來源、時間、量比與缺失狀態。

成交量比較採「當日累計股數／前 20 日完整日均量」，門檻 1.5；這是保守的已達量門檻，沒有歷史同時段資料時不偽造同時段量比。FinMind 分 K 官方文件標示 sponsor 權限；Shioaji 官方串流總量整股單位為張，轉換需 ×1000，並需 API 帳戶。

來源：https://finmind.github.io/tutor/TaiwanMarket/Technical/ 、 https://sinotrade.github.io/zh/tutor/login/ 、 https://sinotrade.github.io/zh/tutor/market_data/streaming/stocks/ 。
