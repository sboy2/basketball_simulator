from io import StringIO

import bs4
import pandas as pd
import requests

from models import League, Stats
from protocols import StatFetcher


class BBallRefStatFetcher(StatFetcher):
    """
    Fetcher for team stats from Basketball Reference.

    Fetches and caches team statistics from Basketball Reference for NBA, WNBA,
    NCAA Men's, and NCAA Women's basketball. Supports basic and advanced stats
    with cleaning and derived metrics.
    """

    def __init__(self):
        """
        Initialize the fetcher and in-memory caches for each league.
        """
        self.pro_base_url = "https://www.basketball-reference.com"
        self.ncaam_base_url = "https://www.sports-reference.com/cbb/seasons/men"
        self.ncaaw_base_url = "https://www.sports-reference.com/cbb/seasons/women"

        self.ncaam_stats: dict[int, pd.DataFrame] = {}
        self.ncaaw_stats: dict[int, pd.DataFrame] = {}
        self.nba_stats: dict[int, pd.DataFrame] = {}
        self.wnba_stats: dict[int, pd.DataFrame] = {}

    def fetch(self, league: League, season: int, team_name: str) -> Stats:
        """
        Fetch team stats for the given league, season, and team.

        Delegates to the appropriate league-specific fetcher. `season` should be
        the year in which the championship was played.

        Parameters
        ----------
        league : League
            The league to fetch stats for ("ncaam", "ncaaw", "nba", "wnba").
        season : int
            Season year (championship year).
        team_name : str
            Name of the team to fetch stats for.

        Returns
        -------
        Stats
            Team statistics for the given season.
        """
        if league == League.NCAAM:
            return self.fetch_ncaam(season, team_name)
        elif league == League.NCAAW:
            return self.fetch_ncaaw(season, team_name)
        elif league == League.NBA:
            return self.fetch_nba(season, team_name)
        elif league == League.WNBA:
            return self.fetch_wnba(season, team_name)

    def fetch_nba(self, season: int, team_name: str) -> Stats:
        """
        Fetch team stats from Basketball Reference for the NBA.

        Parameters
        ----------
        season : int
            Season year (championship year).
        team_name : str
            Name of the NBA team.

        Returns
        -------
        Stats
            Team statistics for the given season.
        """
        raise NotImplementedError("Fetching NBA stats is not implemented.")

    def fetch_wnba(self, season: int, team_name: str) -> Stats:
        """
        Fetch team stats from Basketball Reference for the WNBA.

        Parameters
        ----------
        season : int
            Season year (championship year).
        team_name : str
            Name of the WNBA team.

        Returns
        -------
        Stats
            Team statistics for the given season.
        """
        raise NotImplementedError("Fetching WNBA stats is not implemented.")

    def fetch_ncaam(self, season: int, team_name: str) -> Stats:
        """
        Fetch team stats from Basketball Reference for NCAA Men's basketball.

        Fetches and caches basic and advanced school/opponent stats for the
        season, then returns stats for the requested team.

        Parameters
        ----------
        season : int
            Season year (championship year).
        team_name : str
            Name of the school/team.

        Returns
        -------
        Stats
            Team statistics for the given season.
        """
        if season not in self.ncaam_stats:
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

            for table_id, table in tables.items():
                tables[table_id] = self._clean_table(
                    table,
                    self._NCAA_DROP_COLUMNS[table_id],
                    self._NCAA_SCALE_COLUMNS.get(table_id, None),
                    self._NCAA_RENAME_COLUMNS.get(table_id, None),
                )
                tables[table_id] = self._calculate_stats(table_id, tables[table_id])

            merged_df = (
                tables["basic_school_stats"]
                .join(tables["basic_opp_stats"], how="inner")
                .join(tables["adv_school_stats"], how="inner")
                .join(tables["adv_opp_stats"], how="inner")
            )

            self.ncaam_stats[season] = merged_df

        team_stats = Stats(**self.ncaam_stats[season].loc[team_name])

        return team_stats

    def fetch_ncaaw(self, season: int, team_name: str) -> Stats:
        """
        Fetch team stats from Basketball Reference for NCAA Women's basketball.

        Fetches and caches basic and advanced school/opponent stats for the
        season, then returns stats for the requested team.

        Parameters
        ----------
        season : int
            Season year (championship year).
        team_name : str
            Name of the school/team.

        Returns
        -------
        Stats
            Team statistics for the given season.
        """
        if season not in self.ncaaw_stats:
            stat_types = ["school", "opponent", "advanced-school", "advanced-opponent"]

            urls = [
                f"{self.ncaaw_base_url}/{season}-{stat_type}-stats.html"
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

            for table_id, table in tables.items():
                tables[table_id] = self._clean_table(
                    table,
                    self._NCAA_DROP_COLUMNS[table_id],
                    self._NCAA_SCALE_COLUMNS.get(table_id, None),
                    self._NCAA_RENAME_COLUMNS.get(table_id, None),
                )
                tables[table_id] = self._calculate_stats(table_id, tables[table_id])

            merged_df = (
                tables["basic_school_stats"]
                .join(tables["basic_opp_stats"], how="inner")
                .join(tables["adv_school_stats"], how="inner")
                .join(tables["adv_opp_stats"], how="inner")
            )

            self.ncaaw_stats[season] = merged_df

        team_stats = Stats(**self.ncaaw_stats[season].loc[team_name])

        return team_stats

    _NCAA_BASE_DROP_COLUMNS = [
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
    ]
    _NCAA_DROP_COLUMNS = {
        "basic_school_stats": [
            *_NCAA_BASE_DROP_COLUMNS,
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
        ],
        "basic_opp_stats": [
            *_NCAA_BASE_DROP_COLUMNS,
            ("Overall", "SRS"),
            ("Overall", "SOS"),
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
        ],
        "adv_school_stats": [
            *_NCAA_BASE_DROP_COLUMNS,
            ("Overall", "SRS"),
            ("Overall", "SOS"),
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
        ],
        "adv_opp_stats": [
            *_NCAA_BASE_DROP_COLUMNS,
            ("Overall", "SRS"),
            ("Overall", "SOS"),
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
        ],
    }
    _NCAA_SCALE_COLUMNS = {
        "adv_school_stats": ["o_turnover_percentage", "o_rebound_percentage"],
        "adv_opp_stats": ["d_turnover_percentage", "d_rebound_percentage"],
    }
    _NCAA_RENAME_COLUMNS = {
        "basic_school_stats": {
            "SRS": "simple_rating_system",
            "SOS": "strength_of_schedule",
        },
        "adv_school_stats": {
            "Pace": "pace",
            "TOV%": "o_turnover_percentage",
            "ORB%": "o_rebound_percentage",
        },
        "adv_opp_stats": {
            "Pace": "pace",
            "TOV%": "d_turnover_percentage",
            "ORB%": "d_rebound_percentage",
        },
    }

    def _clean_table(
        self,
        table: pd.DataFrame,
        drop_columns: list[str],
        scale_columns: list[str] = None,
        rename_columns: dict[str, str] = None,
    ) -> pd.DataFrame:
        """
        Clean a stats table for downstream use.

        Drops unnecessary columns and blank rows/columns, sets the index to
        team/school name, optionally renames and scales columns, and converts
        values to numeric.

        Parameters
        ----------
        table : pd.DataFrame
            Raw table from Basketball Reference.
        drop_columns : list of str
            Column identifiers to drop.
        scale_columns : list of str, optional
            Column names to scale by 1/100. Default is None.
        rename_columns : dict of str to str, optional
            Mapping from current column names to new names. Default is None.

        Returns
        -------
        pd.DataFrame
            Cleaned table with team/school as index and numeric values.

        Raises
        ------
        ValueError
            If the table index name is not "School" or "Team".
        """
        table = table.dropna(axis=1, how="all").drop(  # Drop blank columns
            columns=drop_columns
        )
        table.columns = table.columns.droplevel(0)
        table = table.set_index(
            "School" if "School" in table.columns else "Team", drop=True
        )
        table = table[table.index.notna()]
        if table.index.name == "School":
            table = table[table.index != "School"]
        elif table.index.name == "Team":
            table = table[table.index != "Team"]
        else:
            raise ValueError(f"Index name {table.index.name} not supported.")
        table = table.apply(pd.to_numeric)
        if rename_columns:
            table = table.rename(columns=rename_columns)
        if scale_columns:
            for column in scale_columns:
                table[column] /= 100

        return table

    def _calculate_stats(self, table_id: str, table: pd.DataFrame) -> pd.DataFrame:
        """
        Compute shooting percentages and rates from raw counting stats.

        Adds offensive (school) or defensive (opponent) 2P/3P/FT rates and
        percentages, then drops the original FG/3P/FT columns.

        Parameters
        ----------
        table_id : str
            One of "basic_school_stats" or "basic_opp_stats".
        table : pd.DataFrame
            Table with raw FG, FGA, 3P, 3PA, FT, FTA columns.

        Returns
        -------
        pd.DataFrame
            Table with derived shooting rate and percentage columns.
        """
        if table_id == "basic_school_stats":
            table["o_three_point_rate"] = table["3PA"] / table["FGA"]
            table["o_three_point_percentage"] = table["3P"] / table["3PA"]
            table["o_free_throw_rate"] = table["FTA"] / table["FGA"]
            table["o_free_throw_percentage"] = table["FT"] / table["FTA"]
            table["o_two_point_percentage"] = (table["FG"] - table["3P"]) / (
                table["FGA"] - table["3PA"]
            )
            table["o_two_point_rate"] = 1 - table["o_three_point_rate"]
            table = table.drop(columns=["FG", "FGA", "3P", "3PA", "FT", "FTA"])
        elif table_id == "basic_opp_stats":
            table["d_three_point_rate"] = table["3PA"] / table["FGA"]
            table["d_three_point_percentage"] = table["3P"] / table["3PA"]
            table["d_free_throw_rate"] = table["FTA"] / table["FGA"]
            table["d_free_throw_percentage"] = table["FT"] / table["FTA"]
            table["d_two_point_percentage"] = (table["FG"] - table["3P"]) / (
                table["FGA"] - table["3PA"]
            )
            table["d_two_point_rate"] = 1 - table["d_three_point_rate"]
            table = table.drop(columns=["FG", "FGA", "3P", "3PA", "FT", "FTA"])

        return table
