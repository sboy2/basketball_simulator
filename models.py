from enum import Enum

from pydantic import BaseModel, field_validator


class League(str, Enum):
    """
    Model to store the supported leagues.
    """

    NBA = "nba"
    WNBA = "wnba"
    NCAAM = "ncaam"
    NCAAW = "ncaaw"


class Stats(BaseModel):
    """
    Model to store the stats of a team. Returned by the StatFetcher protocol.
    """

    # Offensive stats
    o_turnover_percentage: float
    o_rebound_percentage: float
    o_three_point_rate: float
    o_three_point_percentage: float
    o_free_throw_rate: float
    o_free_throw_percentage: float
    o_two_point_percentage: float
    o_two_point_rate: float
    # Defensive stats
    d_turnover_percentage: float
    d_rebound_percentage: float
    d_three_point_rate: float
    d_three_point_percentage: float
    d_free_throw_rate: float
    d_free_throw_percentage: float
    d_two_point_percentage: float
    d_two_point_rate: float
    # Style stats
    pace: float
    # Comparison stats
    simple_rating_system: float
    strength_of_schedule: float

    @field_validator(
        "o_turnover_percentage",
        "o_rebound_percentage",
        "o_three_point_rate",
        "o_three_point_percentage",
        "o_free_throw_rate",
        "o_free_throw_percentage",
        "o_two_point_percentage",
        "o_two_point_rate",
        "d_turnover_percentage",
        "d_rebound_percentage",
        "d_three_point_rate",
        "d_three_point_percentage",
        "d_free_throw_rate",
        "d_free_throw_percentage",
        "d_two_point_percentage",
        "d_two_point_rate",
    )
    def validate_percentage(cls, v: float) -> float:
        """
        Validate that the percentage is between 0 and 1.
        """
        if not 0 <= v <= 1:
            raise ValueError("Percentage must be between 0 and 1.")
        return v

    @field_validator("pace")
    def validate_pace(cls, v: float) -> float:
        """
        Validate that the pace is greater than 0.
        """
        if v <= 0:
            raise ValueError("Pace must be greater than 0.")
        return v


class Team(BaseModel):
    """
    Model to store a team and necessary information.
    """

    name: str
    league: League
    season: int
    stats: Stats

    @field_validator("season")
    def validate_season(cls, v: int) -> int:
        """
        Validate that the season is greater than 1900.
        """
        if v < 1900:
            raise ValueError("Season must be greater than 1900.")
        return v
