from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    ticker: str = "2330.TW"
    benchmark: str = "^TWII"
    years: int = 20
    tail_quantile: float = 0.10
    probability_threshold: float = 0.35
    daily_hedge_cost: float = 0.0015
    hedge_effectiveness: float = 0.70
    min_hedge_days: int = 40
    max_hedge_rate: float = 0.20
    min_training_days: int = 1_000
    random_state: int = 42
