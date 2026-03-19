import numpy as np

from models import OffensiveStats, TeamStats
from protocols import StatAdjuster


class GamePredictor:
    """
    Predicts the probability of a home team winning a game using an analytical
    Markov Chain approach.

    Models each possession as an absorbing Markov Chain, uses FFT convolution
    over possessions to compute full score distributions, and computes win
    probability via outer product lower-triangle sum.
    """

    def predict(
        self,
        home: TeamStats,
        away: TeamStats,
        adjuster: StatAdjuster,
        neutral_site: bool = False,
    ) -> float:
        """
        Predict the probability of the home team winning.

        Adjusts stats for the matchup, computes possession point distributions,
        convolves over the number of possessions, and returns win probability.

        Parameters
        ----------
        home : TeamStats
            Home team's offensive and defensive stats.
        away : TeamStats
            Away team's offensive and defensive stats.
        adjuster : StatAdjuster
            Stat adjuster to use for the matchup.
        neutral_site : bool, optional
            Whether the game is played at a neutral site. Default is False.
            Note: home court advantage not yet implemented.

        Returns
        -------
        float
            Probability of the home team winning, between 0 and 1.
        """
        adjusted_home = adjuster.adjust(home.offensive, away.defensive)
        adjusted_away = adjuster.adjust(away.offensive, home.defensive)

        home_dist = self._calculate_point_distribution(adjusted_home)
        away_dist = self._calculate_point_distribution(adjusted_away)

        home_possessions, away_possessions = self._calculate_possessions(
            adjusted_home, adjusted_away
        )

        home_score_dist = self._score_distribution(home_dist, home_possessions)
        away_score_dist = self._score_distribution(away_dist, away_possessions)

        return self._win_probability(home_score_dist, away_score_dist)

    def _calculate_point_distribution(self, stats: OffensiveStats) -> np.ndarray:
        """
        Calculate the per-possession point distribution for a team.

        Uses pre-collapsed free throw sequences (option 2 absorbing chain) to
        compute absorption probabilities directly from adjusted stats.

        Parameters
        ----------
        stats : OffensiveStats
            Adjusted offensive stats for the team.

        Returns
        -------
        np.ndarray
            Probability vector of shape (5,) over {0, 1, 2, 3, 4} points.
        """
        t = stats.turnover_percentage
        two_r = stats.two_point_rate
        two_fr = stats.two_point_foul_rate
        two_p = stats.two_point_percentage
        three_r = stats.three_point_rate
        three_fr = stats.three_point_foul_rate
        three_p = stats.three_point_percentage
        ft = stats.free_throw_percentage
        no_tov = 1 - t

        p = np.zeros(5)

        # P(end_0pts): turnover, missed 2 (no foul), missed 2 (foul, miss both FTs),
        #              missed 3 (no foul), missed 3 (foul, miss all 3 FTs)
        p[0] = (
            t
            + no_tov * two_r * (1 - two_fr) * (1 - two_p)
            + no_tov * two_r * two_fr * (1 - two_p) * (1 - ft) ** 2
            + no_tov * three_r * (1 - three_fr) * (1 - three_p)
            + no_tov * three_r * three_fr * (1 - three_p) * (1 - ft) ** 3
        )

        # P(end_1pt): missed 2 (foul, make 1 of 2 FTs),
        #             missed 3 (foul, make 1 of 3 FTs)
        p[1] = (
            no_tov * two_r * two_fr * (1 - two_p) * 2 * ft * (1 - ft)
            + no_tov * three_r * three_fr * (1 - three_p) * 3 * ft * (1 - ft) ** 2
        )

        # P(end_2pts): made 2 (no foul), made 2 (foul, miss and-1),
        #              missed 2 (foul, make both FTs),
        #              missed 3 (foul, make 2 of 3 FTs)
        p[2] = (
            no_tov * two_r * (1 - two_fr) * two_p
            + no_tov * two_r * two_fr * two_p * (1 - ft)
            + no_tov * two_r * two_fr * (1 - two_p) * ft ** 2
            + no_tov * three_r * three_fr * (1 - three_p) * 3 * ft ** 2 * (1 - ft)
        )

        # P(end_3pts): made 2 (foul, make and-1), made 3 (no foul),
        #              made 3 (foul, miss and-1), missed 3 (foul, make all 3 FTs)
        p[3] = (
            no_tov * two_r * two_fr * two_p * ft
            + no_tov * three_r * (1 - three_fr) * three_p
            + no_tov * three_r * three_fr * three_p * (1 - ft)
            + no_tov * three_r * three_fr * (1 - three_p) * ft ** 3
        )

        # P(end_4pts): made 3 (foul, make and-1)
        p[4] = no_tov * three_r * three_fr * three_p * ft

        return p

    def _calculate_possessions(
        self, home: OffensiveStats, away: OffensiveStats
    ) -> tuple[int, int]:
        """
        Calculate the number of possessions for each team.

        Uses the average pace as the base possession count, inflated by each
        team's offensive rebound percentage to account for extra possessions.

        Parameters
        ----------
        home : OffensiveStats
            Adjusted offensive stats for the home team.
        away : OffensiveStats
            Adjusted offensive stats for the away team.

        Returns
        -------
        tuple[int, int]
            Number of possessions for the home and away teams respectively.
        """
        avg_pace = (home.pace + away.pace) / 2
        home_possessions = round(avg_pace * (1 + home.offensive_rebound_percentage))
        away_possessions = round(avg_pace * (1 + away.offensive_rebound_percentage))
        return home_possessions, away_possessions

    def _score_distribution(self, p: np.ndarray, n_possessions: int) -> np.ndarray:
        """
        Compute the full score distribution over n possessions via FFT convolution.

        Parameters
        ----------
        p : np.ndarray
            Per-possession point distribution of shape (5,).
        n_possessions : int
            Number of possessions.

        Returns
        -------
        np.ndarray
            Probability vector where index k is P(total score = k).
        """
        max_score = n_possessions * (len(p) - 1)
        p_padded = np.zeros(max_score + 1)
        p_padded[: len(p)] = p
        score_dist = np.fft.ifft(np.fft.fft(p_padded) ** n_possessions).real
        return score_dist

    def _win_probability(
        self, home_dist: np.ndarray, away_dist: np.ndarray
    ) -> float:
        """
        Compute win probability from two score distributions.

        Uses the outer product of the two distributions and sums the lower
        triangle where home score > away score.

        Parameters
        ----------
        home_dist : np.ndarray
            Home team score distribution.
        away_dist : np.ndarray
            Away team score distribution.

        Returns
        -------
        float
            Probability that home score > away score.
        """
        joint = np.outer(home_dist, away_dist)
        return float(np.tril(joint, k=-1).sum())
