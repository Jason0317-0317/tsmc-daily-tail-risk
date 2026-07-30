import numpy as np
import pandas as pd
import pytest

from tailrisk.config import Config
from tailrisk.data import download_market_data
from tailrisk.features import FEATURE_COLUMNS, build_features
from tailrisk.model import train_and_forecast
from tailrisk.reporting import render_email_html


def test_daily_features_and_forward_target():
    index = pd.date_range("2020-01-02", periods=90, freq="B")
    daily = pd.DataFrame({
        "close": 100 * np.cumprod(np.full(90, 1.01)),
        "benchmark_close": 200 * np.cumprod(np.full(90, 1.005)),
        "volume": np.linspace(1_000, 2_000, 90),
    }, index=index)
    result = build_features(daily)
    assert result.return_1d.dropna().iloc[-1] == pytest.approx(.01)
    assert pd.isna(result.forward_return_1d.iloc[-1])


def synthetic_result():
    rng, rows = np.random.default_rng(42), 1_420
    frame = pd.DataFrame(
        rng.normal(0, .02, (rows, len(FEATURE_COLUMNS))),
        columns=FEATURE_COLUMNS,
        index=pd.date_range("2019-01-02", periods=rows, freq="B"),
    )
    frame["forward_return_1d"] = rng.normal(.0004, .018, rows)
    frame.loc[frame.index[-1], "forward_return_1d"] = np.nan
    return train_and_forecast(frame, Config())


def test_training_and_recent_daily_results():
    result = synthetic_result()
    assert 0 <= result.probability <= 1
    assert result.training_rows == 1_419
    assert 130 <= result.positive_rows <= 150
    assert len(result.recent_results) == 10
    assert {"as_of", "probability", "actual_return", "outcome"} <= result.recent_results[-1].keys()


def test_download_retries_and_returns_daily_rows(monkeypatch):
    index = pd.date_range("2020-01-02", periods=1_300, freq="B")
    columns = pd.MultiIndex.from_product([["Adj Close", "Volume"], ["2330.TW", "^TWII"]])
    complete = pd.DataFrame(100.0, index=index, columns=columns)
    responses = iter([pd.DataFrame(), complete])
    calls = []

    def fake_download(*args, **kwargs):
        calls.append(kwargs)
        return next(responses)

    monkeypatch.setattr("tailrisk.data.yf.download", fake_download)
    monkeypatch.setattr("tailrisk.data.sleep", lambda _: None)
    daily = download_market_data(Config())
    assert len(daily) == 1_300
    assert len(calls) == 2
    assert calls[0]["threads"] is False


def test_html_email_contains_daily_scores():
    result = synthetic_result()
    html = render_email_html(result, Config())
    assert "下一交易日尾部風險預測" in html
    assert "最近 10 個交易日" in html
    assert "PR-AUC" in html
    assert result.recent_results[-1]["as_of"] in html
