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

資料來源：[FinMind API](https://finmind.github.io/quickstart/)。可選擇以 FINMIND_TOKEN 環境變數設定自己的 token；請勿寫入程式碼。抓取與報告產生是手動執行，不會自動更新，也不是盤中行情。

## 研究規則

收盤突破前 20 日最高價、收盤高於 MA20、MA20 高於 MA60、成交量為前 20 日均量至少 1.2 倍。先暖機 60 筆。訊號只能作為下一交易日的待確認候選，不代表當日成交。圖表同時顯示含當日的下一次觀察門檻。

原始價格尚未調整除權息；規則尚未完成績效回測、價格區間、停損、資金與風險設定。資料新鮮度以圖上日期為準。第一版不實際下單。

## GitHub

公開 repository： https://github.com/zzz72818/taiwan-ai-stock-research 。只上傳程式、文件與測試；`.gitignore` 排除行情快取、生成報告、金鑰與診斷資料。程式碼授權尚未指定。

完整月計畫：`docs/plans/2026-10-13-stock-project-roadmap.md`。
