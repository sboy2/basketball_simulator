from models import Team
from protocols import StatAdjuster


class GameSimulator:
    """
    Class to simulate a game, possession by possession using a Markov Chain.
    State space:
        - Home team possession

    """

    def __init__(self, home_team: Team, away_team: Team, neutral_site: bool = False):
        self.home_team = home_team
        self.away_team = away_team
        self.neutral_site = neutral_site

    def simulate(self, stat_adjuster: StatAdjuster):
        pass
