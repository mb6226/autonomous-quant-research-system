import os
from pprint import pprint

from app.research.experiment_runner import ExperimentRunner
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score


def test_mlp_classifier_run():
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")

    runner = ExperimentRunner()

    market = "BTCUSDT"
    timeframe = "1d"
    target_spec = "classification_up_down_5"

    df = runner._load_dataset(market, timeframe)
    df = runner.feature_factory.build(df)
    df["target"] = runner._parse_target(df, target_spec)

    features = [
        c
        for c in df.columns
        if str(df[c].dtype) in ["float64", "int64", "bool"]
    ]
    if "target" in features:
        features.remove("target")

    df = df.dropna(subset=features + ["target"]) if len(features) > 0 else df

    assert len(df) > 0, "Dataset is empty; cannot run test"

    split = int(len(df) * 0.8)
    X_train = df[features].iloc[:split]
    X_test = df[features].iloc[split:]
    y_train = df["target"].iloc[:split]
    y_test = df["target"].iloc[split:]

    model_impl = runner._get_model_impl("mlp")
    trained = model_impl.train(X_train, y_train)

    pred = trained.predict(X_test)

    print("TRAIN", len(X_train))
    print("TEST", len(X_test))

    acc = accuracy_score(y_test, pred)
    prec = precision_score(y_test, pred, zero_division=0)
    rec = recall_score(y_test, pred, zero_division=0)
    f1 = f1_score(y_test, pred, zero_division=0)
    cm = confusion_matrix(y_test, pred)

    print("Metrics")
    pprint({"accuracy": acc, "precision": prec, "recall": rec, "f1": f1})
    print("Confusion Matrix")
    print(cm)

    assert acc > 0


if __name__ == "__main__":
    test_mlp_classifier_run()
