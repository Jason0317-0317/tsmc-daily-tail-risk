# TSMC Daily Tail-Risk Forecast

以過去 20 年日資料預測台積電（`2330.TW`）下一交易日是否落入歷史最差 10% 報酬區間。這是獨立的每日版專案，不會修改或取代原有每週版。

> 僅供研究與教育用途，不構成投資建議。

## 方法

- **標籤**：下一交易日報酬低於當時訓練資料第 10 百分位；每個 walk-forward 分割獨立估計，避免前視偏誤。
- **特徵**：1、5、20、60 日報酬，5／20 日波動率、下行波動率、成交量變化、加權指數報酬、相對強弱及回撤。
- **模型**：具標準化與 `class_weight="balanced"` 的 Logistic Regression。
- **評估**：PR-AUC、ROC-AUC、precision、recall、F2、Brier score。
- **對沖決策**：以 walk-forward 機率和實際下一日報酬搜尋歷史淨效益最高的門檻；預設每日成本 0.15%、抵銷 70% 下跌，最多對沖歷史樣本的 20%。
- **結果追蹤**：列出最近 10 個已有實際結果的交易日。

## 執行

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements-dev.txt
python -m tailrisk
python -m pytest
```

產物會寫入 `artifacts/latest_prediction.json` 與 `artifacts/latest_report.md`。

## 每日自動化

GitHub Actions 於台北時間週一至週五 18:00 執行，也支援手動觸發。設定下列 Repository Secrets 後，會透過 Gmail SMTP 寄出 HTML 報告：

- `SENDER_EMAIL`
- `SENDER_PASSWORD`
- `RECEIVER_EMAIL`

休市日仍可能執行，但會使用最近一個有效交易日資料。若未設定郵件 Secrets，仍會產生 workflow artifact。
