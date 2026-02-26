from typing import Protocol

from models import Stats, Team


class StatFetcher(Protocol):
    """
    Protocol to fetch the stats of a team.
    """

    def fetch(self, league_name: str, season: int, team_name: str) -> Stats: ...


class StatAdjuster(Protocol):
    """
    Protocol to adjust the stats of a team.
    """

    def adjust(self, team: Team, opponent: Team) -> Team: ...
