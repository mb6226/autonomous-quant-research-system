from app.research.experiment_generator import (
    ExperimentGenerator,
)


def test_experiment_generator_basic():
    MARKETS = ["A", "B"]
    MODELS = ["m1", "m2", "m3"]
    TARGETS = ["t1", "t2"]
    FEATURE_SETS = ["f1", "f2"]

    gen = ExperimentGenerator(
        markets=MARKETS,
        models=MODELS,
        targets=TARGETS,
        feature_sets=FEATURE_SETS,
    )

    experiments = gen.generate()

    expected = len(MARKETS) * len(MODELS) * len(TARGETS) * len(FEATURE_SETS)
    print(f"TOTAL EXPERIMENTS = {expected}")

    assert len(experiments) == expected
    # quick content check
    first = experiments[0]
    assert first.market in MARKETS
    assert first.model in MODELS
    assert first.target in TARGETS
    assert first.feature_set in FEATURE_SETS
