from app.features.feature_factory import (
    FeatureFactory,
)

from app.targets.target_factory import (
    TargetFactory,
)


class ResearchDatasetBuilder:

    def build(
        self,
        df,
    ):

        df = (
            FeatureFactory()
            .build(df)
        )

        df[
            "target_forward_return_5"
        ] = (
            TargetFactory()
            .forward_return(
                df,
                periods=5,
            )
        )

        return df
