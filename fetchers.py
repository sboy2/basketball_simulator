from io import StringIO

import bs4
import pandas as pd
import requests

from models import League, Stats
from protocols import StatFetcher


class BBallRefStatFetcher(StatFetcher):
    """
    Class to fetch the stats of a team from the BBallRef API.
    """

    def __init__(self):
        self.pro_base_url = "https://www.basketball-reference.com"
        self.college_base_url = "https://www.sports-reference.com/cbb/seasons"
        self.ncaam_base_url = "https://www.sports-reference.com/cbb/seasons/men"
        self.ncaaw_base_url = "https://www.sports-reference.com/cbb/seasons/women"

        self.ncaam_stats = None
        self.ncaaw_stats = None
        self.nba_stats = None
        self.wnba_stats = None

    def fetch(self, league: League, season: int, team_name: str) -> Stats:
        """
        Fetch the stats of a team from the BBallRef API. `season` should be the year that the
        championship was played in.
        """
        if league == League.NCAAM:
            return self.fetch_ncaam(season, team_name)
        elif league == League.NCAAW:
            return self.fetch_ncaaw(season, team_name)

    def fetch_nba(self, season: int, team_name: str) -> Stats:
        """
        Fetch the stats of a team from the NBA API.
        """
        pass

    def fetch_wnba(self, season: int, team_name: str) -> Stats:
        """
        Fetch the stats of a team from the WNBA API.
        """
        pass

    def fetch_ncaam(self, season: int, team_name: str) -> Stats:
        """
        Fetch the stats of a team from the NCAA Men's Basketball API.
        """
        if self.ncaam_stats is None:
            stat_types = ["school", "opponent", "advanced-school", "advanced-opponent"]

            urls = [
                f"{self.ncaam_base_url}/{season}-{stat_type}-stats.html"
                for stat_type in stat_types
            ]

            responses = [requests.get(url) for url in urls]

            table_ids = [
                "basic_school_stats",
                "basic_opp_stats",
                "adv_school_stats",
                "adv_opp_stats",
            ]
            tables = {}
            for table_id, response in zip(table_ids, responses):
                soup = bs4.BeautifulSoup(response.text, "html.parser")
                table = soup.find("table", id=table_id)
                df = pd.read_html(StringIO(str(table)))[0]
                tables[table_id] = df

            tables["basic_school_stats"] = (
                tables["basic_school_stats"]
                .dropna(axis=1, how="all")  # Drop blank columns
                .drop(  # Drop unnecessary columns
                    columns=[
                        ("Unnamed: 0_level_0", "Rk"),
                        ("Overall", "G"),
                        ("Overall", "W"),
                        ("Overall", "L"),
                        ("Overall", "W-L%"),
                        ("Conf.", "W"),
                        ("Conf.", "L"),
                        ("Home", "W"),
                        ("Home", "L"),
                        ("Away", "W"),
                        ("Away", "L"),
                        ("Points", "Tm."),
                        ("Points", "Opp."),
                        ("Totals", "MP"),
                        ("Totals", "FG%"),
                        ("Totals", "3P%"),
                        ("Totals", "FT%"),
                        ("Totals", "AST"),
                        ("Totals", "PF"),
                        ("Totals", "ORB"),
                        ("Totals", "TRB"),
                        ("Totals", "STL"),
                        ("Totals", "BLK"),
                        ("Totals", "TOV"),
                    ]
                )
            )

            tables["basic_school_stats"].columns = tables[
                "basic_school_stats"
            ].columns.droplevel(0)

            tables["basic_school_stats"] = tables["basic_school_stats"].set_index(
                "School", drop=True
            )

            tables["basic_school_stats"] = tables["basic_school_stats"][
                tables["basic_school_stats"].index.notna()
            ]
            tables["basic_school_stats"] = tables["basic_school_stats"][
                tables["basic_school_stats"].index != "School"
            ]
            tables["basic_school_stats"] = tables["basic_school_stats"].apply(
                pd.to_numeric
            )

            tables["basic_school_stats"]["o_field_goal_percentage"] = (
                tables["basic_school_stats"]["FG"] / tables["basic_school_stats"]["FGA"]
            )
            tables["basic_school_stats"]["o_three_point_rate"] = (
                tables["basic_school_stats"]["3PA"]
                / tables["basic_school_stats"]["FGA"]
            )
            tables["basic_school_stats"]["o_three_point_percentage"] = (
                tables["basic_school_stats"]["3P"] / tables["basic_school_stats"]["3PA"]
            )
            tables["basic_school_stats"]["o_free_throw_rate"] = (
                tables["basic_school_stats"]["FTA"]
                / tables["basic_school_stats"]["FGA"]
            )
            tables["basic_school_stats"]["o_free_throw_percentage"] = (
                tables["basic_school_stats"]["FT"] / tables["basic_school_stats"]["FTA"]
            )

            tables["basic_school_stats"] = tables["basic_school_stats"].drop(
                columns=[  # Drop columns only used for calculations
                    "FG",
                    "FGA",
                    "3P",
                    "3PA",
                    "FT",
                    "FTA",
                ]
            )

            tables["basic_school_stats"] = tables["basic_school_stats"].rename(
                columns={"SRS": "simple_rating_system", "SOS": "strength_of_schedule"}
            )

            tables["basic_opp_stats"] = (
                tables["basic_opp_stats"]
                .dropna(axis=1, how="all")  # Drop blank columns
                .drop(  # Drop unnecessary columns
                    columns=[
                        ("Unnamed: 0_level_0", "Rk"),
                        ("Overall", "G"),
                        ("Overall", "W"),
                        ("Overall", "L"),
                        ("Overall", "W-L%"),
                        ("Overall", "SRS"),
                        ("Overall", "SOS"),
                        ("Conf.", "W"),
                        ("Conf.", "L"),
                        ("Home", "W"),
                        ("Home", "L"),
                        ("Away", "W"),
                        ("Away", "L"),
                        ("Points", "Tm."),
                        ("Points", "Opp."),
                        ("Opponent", "MP"),
                        ("Opponent", "FG%"),
                        ("Opponent", "3P%"),
                        ("Opponent", "FT%"),
                        ("Opponent", "AST"),
                        ("Opponent", "PF"),
                        ("Opponent", "ORB"),
                        ("Opponent", "TRB"),
                        ("Opponent", "STL"),
                        ("Opponent", "BLK"),
                        ("Opponent", "TOV"),
                    ]
                )
            )

            tables["basic_opp_stats"].columns = tables[
                "basic_opp_stats"
            ].columns.droplevel(0)

            tables["basic_opp_stats"] = tables["basic_opp_stats"].set_index(
                "School", drop=True
            )

            tables["basic_opp_stats"] = tables["basic_opp_stats"][
                tables["basic_opp_stats"].index.notna()
            ]
            tables["basic_opp_stats"] = tables["basic_opp_stats"][
                tables["basic_opp_stats"].index != "School"
            ]
            tables["basic_opp_stats"] = tables["basic_opp_stats"].apply(pd.to_numeric)

            tables["basic_opp_stats"]["d_field_goal_percentage"] = (
                tables["basic_opp_stats"]["FG"] / tables["basic_opp_stats"]["FGA"]
            )
            tables["basic_opp_stats"]["d_three_point_rate"] = (
                tables["basic_opp_stats"]["3PA"] / tables["basic_opp_stats"]["FGA"]
            )
            tables["basic_opp_stats"]["d_three_point_percentage"] = (
                tables["basic_opp_stats"]["3P"] / tables["basic_opp_stats"]["3PA"]
            )
            tables["basic_opp_stats"]["d_free_throw_rate"] = (
                tables["basic_opp_stats"]["FTA"] / tables["basic_opp_stats"]["FGA"]
            )
            tables["basic_opp_stats"]["d_free_throw_percentage"] = (
                tables["basic_opp_stats"]["FT"] / tables["basic_opp_stats"]["FTA"]
            )

            tables["basic_opp_stats"] = tables["basic_opp_stats"].drop(
                columns=[  # Drop columns only used for calculations
                    "FG",
                    "FGA",
                    "3P",
                    "3PA",
                    "FT",
                    "FTA",
                ]
            )

            tables["adv_school_stats"] = (
                tables["adv_school_stats"]
                .dropna(axis=1, how="all")  # Drop blank columns
                .drop(  # Drop unnecessary columns
                    columns=[
                        ("Unnamed: 0_level_0", "Rk"),
                        ("Overall", "G"),
                        ("Overall", "W"),
                        ("Overall", "L"),
                        ("Overall", "W-L%"),
                        ("Overall", "SRS"),
                        ("Overall", "SOS"),
                        ("Conf.", "W"),
                        ("Conf.", "L"),
                        ("Home", "W"),
                        ("Home", "L"),
                        ("Away", "W"),
                        ("Away", "L"),
                        ("Points", "Tm."),
                        ("Points", "Opp."),
                        ("School Advanced", "ORtg"),
                        ("School Advanced", "FTr"),
                        ("School Advanced", "3PAr"),
                        ("School Advanced", "TS%"),
                        ("School Advanced", "TRB%"),
                        ("School Advanced", "AST%"),
                        ("School Advanced", "STL%"),
                        ("School Advanced", "BLK%"),
                        ("School Advanced", "eFG%"),
                        ("School Advanced", "FT/FGA"),
                    ]
                )
            )

            tables["adv_school_stats"].columns = tables[
                "adv_school_stats"
            ].columns.droplevel(0)

            tables["adv_school_stats"] = tables["adv_school_stats"].set_index(
                "School", drop=True
            )

            tables["adv_school_stats"] = tables["adv_school_stats"][
                tables["adv_school_stats"].index.notna()
            ]

            tables["adv_school_stats"] = tables["adv_school_stats"][
                tables["adv_school_stats"].index != "School"
            ]

            tables["adv_school_stats"] = tables["adv_school_stats"].rename(
                columns={
                    "Pace": "pace",
                    "TOV%": "o_turnover_percentage",
                    "ORB%": "o_rebound_percentage",
                }
            )

            tables["adv_school_stats"] = tables["adv_school_stats"].apply(pd.to_numeric)

            tables["adv_school_stats"]["o_turnover_percentage"] = (
                tables["adv_school_stats"]["o_turnover_percentage"] / 100
            )
            tables["adv_school_stats"]["o_rebound_percentage"] = (
                tables["adv_school_stats"]["o_rebound_percentage"] / 100
            )

            tables["adv_opp_stats"] = (
                tables["adv_opp_stats"]
                .dropna(axis=1, how="all")  # Drop blank columns
                .drop(  # Drop unnecessary columns
                    columns=[
                        ("Unnamed: 0_level_0", "Rk"),
                        ("Overall", "G"),
                        ("Overall", "W"),
                        ("Overall", "L"),
                        ("Overall", "W-L%"),
                        ("Overall", "SRS"),
                        ("Overall", "SOS"),
                        ("Conf.", "W"),
                        ("Conf.", "L"),
                        ("Home", "W"),
                        ("Home", "L"),
                        ("Away", "W"),
                        ("Away", "L"),
                        ("Points", "Tm."),
                        ("Points", "Opp."),
                        ("Opponent Advanced", "Pace"),
                        ("Opponent Advanced", "ORtg"),
                        ("Opponent Advanced", "FTr"),
                        ("Opponent Advanced", "3PAr"),
                        ("Opponent Advanced", "TS%"),
                        ("Opponent Advanced", "TRB%"),
                        ("Opponent Advanced", "AST%"),
                        ("Opponent Advanced", "STL%"),
                        ("Opponent Advanced", "BLK%"),
                        ("Opponent Advanced", "eFG%"),
                        ("Opponent Advanced", "FT/FGA"),
                    ]
                )
            )

            tables["adv_opp_stats"].columns = tables["adv_opp_stats"].columns.droplevel(
                0
            )

            tables["adv_opp_stats"] = tables["adv_opp_stats"].set_index(
                "School", drop=True
            )

            tables["adv_opp_stats"] = tables["adv_opp_stats"][
                tables["adv_opp_stats"].index.notna()
            ]

            tables["adv_opp_stats"] = tables["adv_opp_stats"][
                tables["adv_opp_stats"].index != "School"
            ]

            tables["adv_opp_stats"] = tables["adv_opp_stats"].rename(
                columns={
                    "Pace": "pace",
                    "TOV%": "d_turnover_percentage",
                    "ORB%": "d_rebound_percentage",
                }
            )

            tables["adv_opp_stats"] = tables["adv_opp_stats"].apply(pd.to_numeric)

            tables["adv_opp_stats"]["d_turnover_percentage"] = (
                tables["adv_opp_stats"]["d_turnover_percentage"] / 100
            )
            tables["adv_opp_stats"]["d_rebound_percentage"] = (
                tables["adv_opp_stats"]["d_rebound_percentage"] / 100
            )

            merged_df = (
                tables["basic_school_stats"]
                .join(tables["basic_opp_stats"], how="inner")
                .join(tables["adv_school_stats"], how="inner")
                .join(tables["adv_opp_stats"], how="inner")
            )

            self.ncaam_stats = merged_df

        team_stats = Stats(**self.ncaam_stats.loc[team_name])

        return team_stats

    def fetch_ncaaw(self, season: int, team_name: str) -> Stats:
        """
        Fetch the stats of a team from the NCAA Women's Basketball API.
        """
        pass
