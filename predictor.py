import numpy as np

from models import Team
from protocols import StatAdjuster


class GamePredictor:
    """
    Class to predict the probability of a team winning a game.
    """

    def __init__(
        self,
        home_team: Team,
        away_team: Team,
        adjuster: StatAdjuster,
        neutral_site: bool = False,
    ):
        self.home_team = home_team
        self.away_team = away_team
        self.neutral_site = neutral_site

    def _calculate_point_distribution(self, team: Team) -> np.ndarray:
        """
        Calculate the point distribution for a team.
        """
        point_distribution = np.zeros(5)

        # Calculate the probability of scoring 0 points
        zero_point_probability = team.offensive.turnover_percentage
        zero_point_probability += (1 - team.offensive.turnover_percentage) * (
            team.offensive.two_point_rate
            * (1 - team.offensive.two_point_foul_rate)
            * (1 - team.offensive.two_point_percentage)
        )
        point_distribution[0] = zero_point_probability

        return point_distribution
