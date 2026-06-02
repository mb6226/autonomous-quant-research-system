def test_research_components_import():
    # Import major automation components to ensure they load without executing heavy work
    from app.research.experiment_generator import ExperimentGenerator
    from app.research.experiment_runner import ExperimentRunner
    from app.research.multi_market_runner import MultiMarketRunner
    from app.research.auto_leaderboard import AutoLeaderboard
    from app.research.feature_selector import FeatureSelector
    from app.research.report_generator import ReportGenerator

    # simple sanity checks
    assert ExperimentGenerator is not None
    assert ExperimentRunner is not None
    assert MultiMarketRunner is not None
    assert AutoLeaderboard is not None
    assert FeatureSelector is not None
    assert ReportGenerator is not None
