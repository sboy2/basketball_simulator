from adjusters import SOSWeightedStatAdjuster
from fetchers import BBallRefStatFetcher
from models import League
from predictor import GamePredictor

SEASON = 2026
LEAGUE = League.NCAAM


def main():
    fetcher = BBallRefStatFetcher()
    predictor = GamePredictor()

    print("Basketball Game Predictor")
    print("=========================")
    print("Commands: 'list' to show all team names, 'quit' to exit")
    print("Fetching stats, this may take a moment...\n")

    # Pre-populate cache so 'list' is available immediately
    try:
        fetcher.fetch(LEAGUE, SEASON, "")
    except KeyError:
        pass  # Expected — cache is populated, empty string just isn't a valid team

    while True:
        home = input("Home team (or 'list'/'quit'): ").strip()
        if home.lower() == "quit":
            break
        if home.lower() == "list":
            teams = sorted(fetcher.ncaam_offensive_stats[SEASON].index.tolist())
            print("\n" + "\n".join(teams) + "\n")
            continue

        away = input("Away team: ").strip()

        try:
            home_stats = fetcher.fetch(LEAGUE, SEASON, home)
        except KeyError:
            print(f"\nCould not find '{home}'. Type 'list' to see all team names.\n")
            continue

        try:
            away_stats = fetcher.fetch(LEAGUE, SEASON, away)
        except KeyError:
            print(f"\nCould not find '{away}'. Type 'list' to see all team names.\n")
            continue

        total_teams = len(fetcher.ncaam_offensive_stats[SEASON])
        adjuster = SOSWeightedStatAdjuster(total_teams=total_teams)

        home_win_prob = predictor.predict(home_stats, away_stats, adjuster)
        away_win_prob = 1 - home_win_prob

        print(f"\n{home}: {home_win_prob:.1%}")
        print(f"{away}: {away_win_prob:.1%}\n")


if __name__ == "__main__":
    main()
