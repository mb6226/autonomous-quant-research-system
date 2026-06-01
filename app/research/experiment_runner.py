from app.research.dataset_builder import (
    ResearchDatasetBuilder,
)


class ExperimentRunner:

    def run(
        self,
        experiment,
        df,
    ):

        dataset = (
            ResearchDatasetBuilder()
            .build(df)
        )

        return {
            "experiment": experiment.name,
            "rows": len(dataset),
            "columns": len(dataset.columns),
        }
