""" get_champ_card_data.py

    This script parses through my individual and team data and returns a list of stats for
    various champions based on passed arguments. That data is then displayed in the website
    on an individuals 'dashboard'.
"""
import sys
import json
import requests
import pandas as pd # type: ignore

def main():
    """ Script Main Function

        Parameters:
            player      (str): Specifies the player we're returning data for.
            role        (str): Specifies the role we're returning data for.
            maxgames    (str): the number of games we consider when getting the stats.
            incnone     (str): the option for 'include None Role'.

        Riot often cannot identify what role a player played as, and returns None as their
        role. The include none option includes those games in our stats if 'true'.

        Returns:
            A json structure that looks something like this:

	[[
	{"champion": "Fiddlesticks", "role": "JUNGLE", "games": 18, "win_rate": 0.61,
	"kda": 3.28, "gpm": 328.32, "cspm": 0.68, "tower_damage": 896.17,
	"champion_damage": 18352.56, "wards_placed": 2.83, "vision_wards_bought": 2.83,
	"wards_killed": 3.33},

	{"champion": "Hecarim", "role": "JUNGLE", "games": 2, "win_rate": 0.0, "kda": 2.31,
	"gpm": 315.42, "cspm": 0.66, "tower_damage": 26.5, "champion_damage": 12251.0,
	"wards_placed": 3.5, "vision_wards_bought": 0.0, "wards_killed": 4.5}
	]]

    """

    player = sys.argv[1]
    role = sys.argv[2]
    maxgames = sys.argv[3]
    incnone = sys.argv[4]

    # Consider switching to db calls? hmm.
    team_data = requests.get("http://paulzplace.asuscomm.com/api/get_team_data?name="+sys.argv[1])

    team_matches = json.loads(team_data.text)
    team_matches_df = pd.DataFrame(team_matches)

    player_df = get_player_data(player)
    merged_matches = merge_team_and_player_df(player_df, team_matches_df)

    # if role is specified, include only those games.
    if role != "All":
        merged_matches = merged_matches[merged_matches['role'] == role.upper()]

    if incnone == "false":
        merged_matches = merged_matches[merged_matches['role'] != "NONE"]

    if maxgames == "All":
        merged_recent = merged_matches.sort_values('start_time', ascending=False)
    else:
        merged_recent = merged_matches.sort_values('start_time',\
                ascending=False).head(int(maxgames))

    merged_perf = get_performance_for_champ_role(merged_recent, role, incnone)

    array_of_champs = merged_perf.to_dict(orient="records")

    nested_array = []
    inner_array = []

    curr_index = 0
    for champ in array_of_champs:
        if curr_index >= 4:
            nested_array.append(inner_array)
            curr_index = 0
            inner_array = []

        inner_array.append(champ)
        curr_index = curr_index+1

    # if there are less than 5 champs, we have to do this or we get nothing.
    # also if we have leftover inners we attach them here.
    if len(inner_array) != 0:
        nested_array.append(inner_array)

    print(json.dumps(nested_array))

def get_player_data(player: str) -> pd.DataFrame:
    """ Gets a players data from an endpoint.

        Args:
            player: The name of a player to get data for.

        Returns:
            A dataframe containing all of the data we have for 'player'.
    """
    return pd.DataFrame(json.loads(requests.get(\
            f"http://paulzplace.asuscomm.com/api/get_user_data?name={player}").text))

def merge_team_and_player_df(player_df: pd.DataFrame, team_df: pd.DataFrame) -> pd.DataFrame:
    """ Merges a players matches dataframe with the data stored in the team dataframe.
        Also renames some columns while doing so.

        Args:
            player_df: A dataframe containing player specific data.
            team_df: A dataframe containing data associated with a team.

        Returns:
            A df with data from both the player_df and team_df.

    """
    combined_df = player_df.merge(team_df, left_on='match_id', right_on='match_id')
    combined_df = combined_df.drop(columns=["first_blood_y", "win_y"])
    combined_df = combined_df.rename(columns={"match_id_x": "match_id"})
    combined_df = combined_df.rename(columns={"first_blood_x": "first_blood"})
    combined_df = combined_df.rename(columns={"win_x": "win"})
    return combined_df

def get_performance_for_champ_role(player_matches: pd.DataFrame, what_role=None,\
    incnone="false") -> pd.DataFrame:

    """ Returns data based on a players champ/role stats. If a champ is played in multiple roles,
        this will return separate data for those roles. The return structure looks something like


        Args:
            player_matches:     Dataframe containing 'recent' games.
            what_role:           The role we're parsing data for.
            incnone:            Option to include 'none' as a role.

        Returns:
		A dataframe containing several stats indexed by champion/role
    """

    champs_df = pd.DataFrame(columns=['champion', 'role', 'games', 'win_rate',\
            'kda', 'gpm', 'cspm', 'tower_damage', 'champion_damage', 'wards_placed',\
            'vision_wards_bought', 'wards_killed'])

    # gets a list of all champions present in this players matches.
    champ_list = list(player_matches['champion_name'].value_counts().index)

    role_list = get_role_list(what_role, incnone)

    # For each champion present in this dataframe, get data for that champions 'role' games
    # For example, this would go through all of my kled games and break out stats for top, mid,
    # and jungle kled, IF we're getting data for all roles AND I had played kled in all those roles.
    for champ in champ_list:
        player_champ_matches = player_matches[player_matches['champion_name'] == champ]

        for role in role_list:
            # win ratio first
            champ_games_role = player_champ_matches[player_champ_matches['role'] == role]
            champ_wins = champ_games_role[champ_games_role['win'] == "Win"].shape[0]
            champ_fails = champ_games_role[champ_games_role['win'] == "Fail"].shape[0]

            if champ_wins > 0 or champ_fails > 0:
                total_games = champ_wins+champ_fails
                win_ratio = round(champ_wins / total_games, 2)

                # other stats second
                gpm = pd.to_numeric(champ_games_role['gold_per_minute']).mean().round(2)
                cspm = pd.to_numeric(champ_games_role['creeps_per_minute']).mean().round(2)
                tower_dmg = pd.to_numeric(champ_games_role['damage_to_turrets']).mean().round(2)
                champ_dmg = pd.to_numeric(champ_games_role['damage_to_champs']).mean().round(2)
                wards_placed = pd.to_numeric(champ_games_role['wards_placed']).mean().round(2)

                vision_bought = pd.to_numeric(champ_games_role['vision_wards_bought']).mean()\
                        .round(2)

                wards_killed = pd.to_numeric(champ_games_role['wards_killed']).mean().round(2)

                # kda calculation ( kill + assist ) / deaths
                if pd.to_numeric(champ_games_role['deaths']).mean() != 0:
                    # we have games with deaths so we're not dividing by 0. Cool.
                    kda = ((pd.to_numeric(champ_games_role['kills']).mean() \
                            + pd.to_numeric(champ_games_role['assists']).mean()) \
                            / pd.to_numeric(champ_games_role['deaths']).mean()).round(2)
                else:
                    # we don't have any deaths, so we don't include deaths because divide by 0 bad
                    kda = ((pd.to_numeric(champ_games_role['kills']).mean() \
                            + pd.to_numeric(champ_games_role['assists']).mean()).round(2))

                # builds the dataframe we're returning.
                champs_df.loc[len(champs_df)] = [champ, role, total_games, win_ratio,\
                        kda, gpm, cspm, tower_dmg, champ_dmg, wards_placed,\
                        vision_bought, wards_killed]

    return champs_df

def get_role_list(get_role: str, incnone: str) -> list:
    """ Returns a list of the roles we're parsing data for. Could be a single role, all roles,
        or either of these and 'None'.

        Args:
            role:       The role we're parsing data for.
            incnone:    Option to include 'none' as a role.

        Returns:
            A list of roles we want data for.
    """

    role_list = ['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'SUPPORT']

    if get_role not in (None, '', 'All'):
        role_list = []
        role_list.append(get_role.upper())

    if incnone == "true":
        role_list.append("NONE")

    return role_list

if __name__ == "__main__":
    main()
