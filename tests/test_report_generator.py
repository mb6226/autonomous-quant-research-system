import os
from app.research.report_generator import ReportGenerator
from app.research.multi_market_runner import ResearchRunResult
from app.research.experiment_runner import ExperimentResultSimple
from app.research.auto_leaderboard import AutoLeaderboard
import json


def test_report_generator_creates_md():
    # load existing research_results.json
    path = os.path.join(os.getcwd(), "artifacts", "research_results.json")
    assert os.path.exists(path), "research_results.json missing for test"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # build ExperimentResultSimple list
    results = []
    for item in data:
        ers = ExperimentResultSimple(market=item.get("market"), timeframe="1d", model=item.get("model"), target=item.get("target"), accuracy=item.get("accuracy"), rows=None)
        results.append(ers)

    lb = AutoLeaderboard()
    lb.add_many(results)

    rr = ResearchRunResult(total_experiments=len(results), successful_experiments=sum(1 for r in results if r.accuracy is not None), failed_experiments=0, leaderboard=lb, results=results)

    rg = ReportGenerator()
    out = rg.generate(rr)

    assert os.path.exists(out)
    assert os.path.getsize(out) > 0

    with open(out, "r", encoding="utf-8") as f:
        txt = f.read()
    assert "Research Report" in txt
    assert "Leaderboard" in txt
    assert "Summary" in txt

    print("REPORT GENERATED")
    print(out)
