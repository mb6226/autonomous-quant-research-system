import pandas as pd


class DatasetValidator:

    def validate(
        self,
        df: pd.DataFrame,
    ) -> list[str]:

        errors: list[str] = []

        if len(df) == 0:
            errors.append(
                "empty_dataset"
            )
            return errors

        if "timestamp" not in df.columns:
            errors.append(
                "missing_timestamp"
            )
            return errors

        duplicate_count = (
            df["timestamp"]
            .duplicated()
            .sum()
        )

        if duplicate_count > 0:
            errors.append(
                f"duplicates:{duplicate_count}"
            )

        if not (
            df["timestamp"]
            .is_monotonic_increasing
        ):
            errors.append(
                "timestamps_not_sorted"
            )

        return errors
