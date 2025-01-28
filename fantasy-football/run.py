from espn_api.football import League

# Input your ESPN Fantasy Football login details and league info
# Replace these values with your actual credentials
espn_s2 = "AEBmqMJP6qyWCJx%2Fy%2FdlU29D7jtwqmW74FYutaJaoV16mm82z91LycMdFEGARNAjeKroFek4QIjo%2F3ddACFYsf9s5kdtOf53aNaWSY%2B0CDumQq%2BXYWFy91gikghVZbxi6HeAg9TevI6nhFyyVg14FxPJHdG35OP6GeMQV2VKFRciTOR6KK%2Fl59XElpWA4%2BL6agbLMusinYdRqTbKSY4v0aI8%2FFb1tM7uCVjhjXzdPU8Ss1%2BPM6QX2G1o0Yv8r%2FHAMlLTHUrBPHYV5vviDHHqqeTDWvkZpS570n4VwB12KRUc4rKEUQfCWnzJxM1VFeeSGYg%3D"
swid = "c4719ea8-ba6e-4067-9592-3ca060cd14d7"
league_ids = [1198961, 1542043, 1004103369, 635235368]  # Replace with your league IDs
season_year = 2024  # Replace with the current season year
last_name = "Diderich"

def get_league_data():
    leagues = []
    for league_id in league_ids:
        league = League(
            league_id=league_id, year=season_year, espn_s2=espn_s2, swid=swid
        )
        leagues.append(league)
    return leagues


def generate_player_overview(leagues):
    players_in_leagues = {}
    opponents_players = {}

    for league in leagues:
        teams = league.teams  # All teams in the league
        matchups = league.scoreboard()  # Current matchups

        # Find players on your teams
        for my_team in teams:
            for owner in my_team.owners:
                if last_name == owner["lastName"]:
                    for player in my_team.roster:
                        if player.name not in players_in_leagues:
                            players_in_leagues[player.name] = 0
                        players_in_leagues[player.name] += 1

        # Find players you're playing against
        for matchup in matchups:
            if any(
                last_name == owner["lastName"] for owner in matchup.home_team.owners
            ):
                opponent = matchup.away_team
            elif any(
                last_name == owner["lastName"] for owner in matchup.away_team.owners
            ):
                opponent = matchup.home_team
            else:
                continue

            for player in opponent.roster:
                if player.name not in opponents_players:
                    opponents_players[player.name] = 0
                opponents_players[player.name] += 1

    return players_in_leagues, opponents_players


def print_overview(players_in_leagues, opponents_players):
    print("\nPlayers on Your Teams Across Leagues:")
    for player, count in players_in_leagues.items():
        print(f"{player}: {count} league(s)")

    print("\nPlayers You're Playing Against Across Leagues:")
    for player, count in opponents_players.items():
        print(f"{player}: {count} league(s)")

# Main execution
try:
    print("Fetching league data...")
    leagues = get_league_data()

    print("Generating player overview...")
    players_in_leagues, opponents_players = generate_player_overview(leagues)

    print("Printing overview:")
    print_overview(players_in_leagues, opponents_players)

except Exception as e:
    print(f"An error occurred: {e}")
