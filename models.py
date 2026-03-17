from abc import ABC
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


class Stats(BaseModel, ABC):
    """
    Model to store the stats of a team. Returned by the StatFetcher protocol.
    """

    pace: float
    turnover_percentage: float
    two_point_rate: float
    two_point_foul_rate: float
    two_point_percentage: float
    three_point_rate: float
    three_point_foul_rate: float
    three_point_percentage: float
    free_throw_percentage: float

    @field_validator(
        "turnover_percentage",
        "two_point_rate",
        "two_point_foul_rate",
        "two_point_percentage",
        "three_point_rate",
        "three_point_foul_rate",
        "three_point_percentage",
        "free_throw_percentage",
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


class OffensiveStats(Stats):
    """
    Model to store the offensive stats of a team.
    """

    offensive_rebound_percentage: float

    @field_validator("offensive_rebound_percentage")
    def validate_offensive_rebound_percentage(cls, v: float) -> float:
        """
        Validate that the offensive rebound percentage is between 0 and 1.
        """
        if not 0 <= v <= 1:
            raise ValueError("Offensive rebound percentage must be between 0 and 1.")
        return v


class DefensiveStats(Stats):
    """
    Model to store the defensive stats of a team.
    """

    defensive_rebound_percentage: float

    @field_validator("defensive_rebound_percentage")
    def validate_defensive_rebound_percentage(cls, v: float) -> float:
        """
        Validate that the defensive rebound percentage is between 0 and 1.
        """
        if not 0 <= v <= 1:
            raise ValueError("Defensive rebound percentage must be between 0 and 1.")
        return v


class TeamStats(BaseModel):
    """
    Model to store the stats of a team.
    """

    offensive: OffensiveStats
    defensive: DefensiveStats


class Team(BaseModel):
    """
    Model to store a team and necessary information.
    """

    name: str
    league: League
    season: int
    stats: OffensiveStats

    @field_validator("season")
    def validate_season(cls, v: int) -> int:
        """
        Validate that the season is greater than 1900.
        """
        if v < 1900:
            raise ValueError("Season must be greater than 1900.")
        return v
