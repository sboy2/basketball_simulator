from dataclasses import dataclass


@dataclass
class Stats:
    """
    Dataclass to store the stats of a team. Returned by the StatFetcher protocol.
    """

    # Offensive stats
    o_field_goal_percentage: float
    o_turnover_percentage: float
    o_rebound_percentage: float
    o_three_point_rate: float
    o_three_point_percentage: float
    o_free_throw_rate: float
    # Defensive stats
    d_field_goal_percentage: float
    d_turnover_percentage: float
    d_rebound_percentage: float
    d_three_point_rate: float
    d_three_point_percentage: float
    d_free_throw_rate: float
    # Style stats
    pace: float
    # Comparison stats
    simple_rating_system: float
    strength_of_schedule: float


@dataclass
class Team:
    """
    Dataclass to store a team and necessary information.
    """

    name: str
    league_name: str
    season: int
    stats: Stats
