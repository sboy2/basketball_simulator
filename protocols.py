from typing import Protocol

from models import Team, TeamStats


class StatFetcher(Protocol):
    """
    Protocol to fetch the stats of a team.
    """

    def fetch(self, league_name: str, season: int, team_name: str) -> TeamStats: ...


class StatAdjuster(Protocol):
    """
    Protocol to adjust the stats of a team.
    """

    def adjust(self, team: Team, opponent: Team) -> Team: ...
