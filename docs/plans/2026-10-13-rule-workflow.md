# 規則式分析流程

使用者要求參考 TradingAgents 分析流程並實作規則式工具。

1. tests/test_workflow.py：先執行，確認 workflow 模組缺少；再實作。
2. workflow.py：evaluate(snapshot, as_of) 產生五項條件、多空依據、資料與 ATR 風險、候選狀態和人工檢查清單。只依指定截點資料判斷。原 signal 保留為技術訊號，不冒充風險核准。
3. build_report.py：使用 Asia/Taipei 的報告日期產生四檔評估，輸出本機 JSON 和 HTML。資料缺失個股獨立標錯。
4. report_template.html：四檔總覽、逐項條件及多空／風險／決策，保留原價格圖。頁面到另一天時顯示需要重新產生報告，防止舊快照被誤認為當日結果。
5. 驗證：完整 unittest、真實快取產生報告、瀏覽器四檔切換與新流程內容檢查。

門檻：歷史至少 60 筆；量比 >= 1.2；日曆資料間隔 <= 5 日；ATR14 / close <= 6%。日曆間隔不是交易日驗證，長假可能需人工檢查。參數未經回測。新聞／財報未接入，不給予虛構分數或買進許可。參考架構而非複製 TradingAgents 程式碼。

來源：https://github.com/TauricResearch/TradingAgents （2026-10-13 查閱）。
