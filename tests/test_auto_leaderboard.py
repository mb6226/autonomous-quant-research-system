from dataclasses import dataclass

from app.research.auto_leaderboard import AutoLeaderboard


@dataclass
class FakeResult:
    market: str
    model: str
    accuracy: float = None
    r2: float = None


def test_auto_leaderboard_ordering():
    lb = AutoLeaderboard()

    results = [
        FakeResult(market="BTCUSDT", model="xgboost", accuracy=0.56),
        FakeResult(market="USOIL", model="xgboost", accuracy=0.54),
        FakeResult(market="XAUUSD", model="lightgbm", accuracy=0.53),
        FakeResult(market="EURUSD", model="xgboost", accuracy=0.45),
    ]

    lb.add_many(results)

    top = lb.top(10)

    # print TOP 10 as requested
    print("TOP 10")
    for i, r in enumerate(top, start=1):
        print(f"{i} {r.market} {r.model} {r.accuracy:.2f}")

    assert len(top) == 4
    assert top[0].market == "BTCUSDT"
    assert top[1].market == "USOIL"
    assert top[2].market == "XAUUSD"
    assert top[3].market == "EURUSD"
