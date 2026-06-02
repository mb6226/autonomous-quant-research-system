class Leaderboard:

    def rank(
        self,
        results,
        metric="r2",
    ):

        return sorted(
            results,
            key=lambda x: x[metric],
            reverse=True,
        )
