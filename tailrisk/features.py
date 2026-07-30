import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "return_1d", "return_5d", "return_20d", "return_60d",
    "volatility_5d", "volatility_20d", "downside_volatility_20d",
    "volume_change_5d", "benchmark_return_1d", "relative_return_5d",
    "drawdown_20d",
]


def build_features(daily: pd.DataFrame) -> pd.DataFrame:
    f = daily.copy()
    f["return_1d"] = f.close.pct_change()
    f["return_5d"] = f.close.pct_change(5)
    f["return_20d"] = f.close.pct_change(20)
    f["return_60d"] = f.close.pct_change(60)
    f["volatility_5d"] = f.return_1d.rolling(5).std()
    f["volatility_20d"] = f.return_1d.rolling(20).std()
    f["downside_volatility_20d"] = f.return_1d.clip(upper=0).rolling(20).std()
    f["volume_change_5d"] = f.volume.pct_change(5)
    f["benchmark_return_1d"] = f.benchmark_close.pct_change()
    f["relative_return_5d"] = f.return_5d - f.benchmark_close.pct_change(5)
    f["drawdown_20d"] = f.close / f.close.rolling(20).max() - 1
    f["forward_return_1d"] = f.close.shift(-1) / f.close - 1
    return f.replace([np.inf, -np.inf], np.nan)
