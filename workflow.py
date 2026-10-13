"""Deterministic research workflow inspired by TradingAgents' role separation."""
from datetime import date
from strategy import VOLUME_RATIO, BREAKOUT_BUFFER, MAX_CONSOLIDATION_RANGE


def evaluate(bar, as_of, max_age_days=5, max_atr_ratio=0.06):
    close = float(bar['close'])
    if close <= 0:
        raise ValueError('Close must be positive')
    age = (date.fromisoformat(as_of) - date.fromisoformat(bar['date'])).days
    ready = all(bar.get(k) is not None for k in ('ma20', 'ma60', 'breakout', 'volume_ratio', 'atr', 'consolidation_range'))
    definitions = [
        ('歷史暖機', ready, '至少 60 筆日線與有效指標'),
        ('均線趨勢', ready and bar['ma20'] > bar['ma60'], 'MA20 > MA60'),
        ('價格趨勢', ready and close > bar['ma20'], '收盤 > MA20'),
        ('盤整確認', ready and bar['consolidation_range'] <= MAX_CONSOLIDATION_RANGE, '前 20 日振幅／均價 <= 12%'),
        ('前高突破', ready and close > bar['breakout'] * (1 + BREAKOUT_BUFFER), '收盤 > 前 20 日最高價 × 1.005'),
        ('成交量確認', ready and bar['volume_ratio'] >= VOLUME_RATIO, '量比 >= 1.5'),
    ]
    checks = [dict(name=name, passed=bool(passed), rule=rule) for name, passed, rule in definitions]
    atr_ratio = bar['atr'] / close if ready else None
    technical = all(c['passed'] for c in checks)
    risks = []
    if age < 0:
        status = '資料日期異常'
        risks.append('行情日期晚於分析截點')
    elif age > max_age_days:
        status = '資料待更新'
        risks.append(f'距資料日期 {age} 個日曆日，超過 {max_age_days} 日門檻')
    elif not ready:
        status = '資料不足'
    elif atr_ratio > max_atr_ratio:
        status = '風險暫緩'
        risks.append(f'ATR／收盤超過 {max_atr_ratio:.0%} 研究門檻')
    else:
        status = '候選，待盤前確認' if technical else '等待條件'
    risks.extend(['原始價格未還原除權息', '四檔同屬 AI 題材，持倉集中度需另檢查'])
    return dict(as_of=as_of, data_date=bar['date'], age_days=age, status=status,
                eligible=status == '候選，待盤前確認', technical_candidate=technical,
                checks=checks, bull=[c['name'] for c in checks[1:] if c['passed']],
                bear=[c['name'] for c in checks if not c['passed']],
                atr_ratio=atr_ratio, risks=risks,
                manual_review=['重大公告與隔夜消息', '除權息或停牌', '隔日跳空與可接受價格', '停損、資金與部位'],
                missing_inputs=['新聞', '財報', '實際持倉'],
                parameters=dict(volume_ratio=VOLUME_RATIO, breakout_buffer=BREAKOUT_BUFFER,
                                consolidation_range=MAX_CONSOLIDATION_RANGE,
                                max_age_days=max_age_days, max_atr_ratio=max_atr_ratio))
