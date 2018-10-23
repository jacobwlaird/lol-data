import requests
import json
import csv
import os
import os.path
import time
import pymysql
import pymysql.cursors as cursors
import json
import pandas as pd
import configparser

base_summoner_url = "https://na1.api.riotgames.com/lol/summoner/v3/"
base_match_url = "https://na1.api.riotgames.com/lol/match/v3/"
account_name_url = "summoners/by-name/"
matches_url = "matchlists/by-account/"
match_url = "matches/"

config = configparser.ConfigParser()
config.read('/Users/david/Desktop/pycrap/general.cfg')


db_host = config.get('DATABASE', 'db_id')
db_user = config.get('DATABASE', 'db_user')
db_pw = config.get('DATABASE', 'db_password')
db_name = config.get('DATABASE', 'db_name')

connection = pymysql.connect(db_host, db_user, db_pw, db_name, cursorclass=cursors.SSCursor)

api_key = config.get('RIOT', 'api_key')

accounts = ['spaynkee', 'dumat', 'archemlis', 'csqward', 'stylus_crude', 'dantheninja6156']
def run_sql(sql_query, return_amount="all"):
    fetched = None
    cursor = connection.cursor()
    cursor.execute(sql_query)
    if return_amount == "all":
        fetched = cursor.fetchall()
    elif return_amount == "one":
        fetched = cursor.fetchone()
    cursor.close()
    connection.commit()
    return fetched

def get_account_info(name, start_index, end_index):
    try:
        account_response = requests.get(''.join([base_summoner_url, account_name_url, name, "?api_key=", api_key]))
        account_response.raise_for_status()
        account_data = json.loads(account_response.text)
        account_id = str(account_data['accountId'])
        time.sleep(1)
        player_matches_response = requests.get(''.join([base_match_url, matches_url, account_id, "?beginIndex=", str(start_index), "&endIndex=", str(end_index), "&api_key=", api_key]))
        player_matches_response.raise_for_status()
        player_matches = json.loads(player_matches_response.text)
    except Exception as e:
        print(e)
        print("Get_account_info broke")
        
        
    return player_matches
    
def get_match_data(match_id):
    try:
        print(''.join(["getting match data for ", str(match_id)]))
        time.sleep(1)
        matches_response = requests.get(''.join([base_match_url, match_url, str(match_id), "?api_key=", api_key]))
        matches_response.raise_for_status()
        match_data = json.loads(matches_response.text)
    except Exception as e:
        print(e)
        print("Get_match_data broke, trying again")
        time.sleep(120)
        match_data = get_match_data(match_id)
        
        
    return match_data
            
def add_user_match_history(name, start_index=0, end_index=100):
    
    previous_player_matches = []
    added_matches = []
    
    player_matches = get_account_info(name, start_index, end_index)
    select_previous_matches = "SELECT match_id FROM {}_match_history;".format(name)
    player_match_history = pd.read_sql(select_previous_matches, connection)
        
    for match in player_match_history['match_id']:
        previous_player_matches.append(match)
    
    # could maybe improve this by just selecting games that are in user table but not in matches
    for match in player_matches['matches']:
        if str(match['gameId']) not in previous_player_matches and match['gameId'] > 200000000:
            if match['queue'] == 400 or match['queue'] == 420 or match['queue'] == 440 or match['queue'] == 700:
                if match['role'] == 'DUO_SUPPORT':
                    lane = "SUPPORT"
                else:
                    lane = match['lane']

                match_sql_insert = "INSERT INTO {}_match_history(match_id, role, champion) VALUES ({}, '{}', {});".format(name, match['gameId'], lane, match['champion'])
                run_sql(match_sql_insert)
                added_matches.append(match['gameId'])
    return added_matches

def add_match_to_matches(player_matches, big_daters, name):
    print("adding {}'s matches to matches table".format(name))
    matches_added = []
    previous_matches = []
    
    select_matches_from_matches = "SELECT match_id FROM matches;"
    matches_history = pd.read_sql(select_matches_from_matches, connection)

    for match in matches_history['match_id']:   
        previous_matches.append(str(match))
    
    print(previous_matches)
    for player_match in player_matches:
        select_match_id_and_champion = "SELECT match_id, champion, role FROM {}_match_history WHERE match_id = {};".format(name, player_match)
        user_match_history = pd.read_sql(select_match_id_and_champion, connection)
    
        match_id = str(user_match_history['match_id'][0])
        champion = str(user_match_history['champion'][0])

        if match_id not in previous_matches:
            match_data = big_daters[int(match_id)]
            print("Game was not in previous matches, better add it.")
            
            for participant in match_data['participants']:
                participant_champ = str(participant['championId'])
                
                if participant_champ == champion:
                    match_insert = "INSERT INTO matches(match_id, participants) VALUES ({}, '{}');".format(match_id, name)
                    run_sql(match_insert)
                    matches_added.append(match_id)
                    
        else:
            print("game was already in there. better updte it.")
            select_statement = "SELECT participants FROM matches WHERE match_id = {};".format(match_id)
            participants = run_sql(select_statement, 'one')
            participants = participants[0]
            
            list_of_participants = participants.split(',')

            if name not in list_of_participants:
                new_participants = ''.join([participants, ",", name])
                match_update = "UPDATE matches SET participants = '{}' WHERE match_id  = {};".format(new_participants, match_id)
                run_sql(match_update)
                
    return matches_added
    
def update_player_data(user_matches_added, big_daters, name):
    print("updating {}'s player data".format(name))

    for match in user_matches_added:
        select_champion = "SELECT champion FROM {}_match_history WHERE match_id = {}".format(name, match)
        user_match_history = pd.read_sql(select_champion, connection)
        
        champion = str(user_match_history['champion'][0])
        
        match_data = big_daters[int(match)]
            
        for participant in match_data['participants']:
            participant_champ = str(participant['championId'])
            
            if participant_champ == champion:
                kills = participant['stats']['kills']
                deaths = participant['stats']['deaths']
                assists = participant['stats']['assists']
                wards_placed = participant['stats']['wardsPlaced']
                damage_to_champs = participant['stats']['totalDamageDealtToChampions']
                damage_to_turrets = participant['stats']['damageDealtToTurrets']
                vision_wards_bought = participant['stats']['visionWardsBoughtInGame']
                wards_killed = participant['stats']['wardsKilled']
                
                if 'firstBloodKill' in participant['stats']:
                    first_blood_kill = participant['stats']['firstBloodKill']
                else:
                    first_blood_kill = 0
                    
                if 'firstBloodAssist' in participant['stats']:
                    first_blood_assist = participant['stats']['firstBloodAssist']
                else:
                    first_blood_assist = 0

                update_stats_sql = "UPDATE {}_match_history SET kills = {}, deaths = {}, assists = {}, damage_to_champions = {}, damage_to_turrets = {}, wards_placed = {}, vision_wards_bought = {}, wards_killed = {}, first_blood = {}, first_blood_assist = {} WHERE match_id = {};".format(name, kills, deaths, assists, damage_to_champs, damage_to_turrets, wards_placed, vision_wards_bought, wards_killed, first_blood_kill, first_blood_assist, match)
                run_sql(update_stats_sql)
                
                update_champion_sql = "UPDATE {}_match_history SET champion_name = (SELECT c_name FROM champions WHERE {}_match_history.`champion` = c_id) WHERE match_id = {}".format(name, name, match)
                run_sql(update_champion_sql)
                
    return
    
def update_team_data(matches_added, big_daters, name):
    print("Updating team data for matches.")
    
    for match in matches_added:
        select_match_id_and_champion = "SELECT match_id, champion FROM {}_match_history WHERE match_id = {}".format(name, match)
        user_match_history = pd.read_sql(select_match_id_and_champion, connection)
            
        match_id = str(user_match_history['match_id'][0])
        champion = str(user_match_history['champion'][0])
       
        match_data = big_daters[int(match)]
           
        for participant in match_data['participants']:
            participant_champ = str(participant['championId'])
                
            if participant_champ == champion:
                team_id = participant['teamId']
                if team_id == 100:
                    team_data = match_data['teams'][0]
                elif team_id == 200:
                    team_data = match_data['teams'][1]
                
                game_outcome = team_data['win']
                first_baron = team_data['firstBaron']
                first_tower = team_data['firstTower']
                rift_herald = team_data['firstRiftHerald']
                first_dragon = team_data['firstDragon']
                dragon_kills = team_data['dragonKills']
                first_blood = team_data['firstBlood']
                
                champ_row = pd.read_sql("SELECT c_name FROM champions WHERE c_id = {}".format(champion), connection)
                champ_name = champ_row['c_name'][0]
                
                match_update = """UPDATE matches SET win = '{}', first_blood = {}, first_baron = {}, first_tower = {}, first_dragon = {}, rift_herald = {}, dragon_kills = {}, allies = "{}" WHERE match_id = {};""".format(game_outcome, first_blood, first_baron, first_tower, first_dragon, rift_herald, dragon_kills, champ_name, match)
                run_sql(match_update)
                
    return
    
def update_allies_enemies(new_matches, big_daters, name):
    print("updating matches allied and enemy champions")
    for match in new_matches:
        select_match_id_and_champion = "SELECT match_id, champion FROM {}_match_history WHERE match_id = {}".format(name, match)
        user_match_history = pd.read_sql(select_match_id_and_champion, connection)
            
        match_id = str(user_match_history['match_id'][0])
        champion = str(user_match_history['champion'][0])
       
        match_data = big_daters[int(match)]
           
        for participant in match_data['participants']:
            participant_champ = str(participant['championId'])
                
            if participant_champ == champion:
                team_id = participant['teamId']
               
                allied_players = []
                enemy_players = []
            
                for individual in match_data['participants']:
                    if str(individual['championId']) == champion:
                        continue
                    
                    if individual['teamId'] == team_id:
                        allied_players.append(individual)
                    else:
                        enemy_players.append(individual)
                        
                # get our champion name so we can put it into allies if there's nothing there yet.
                our_champ = pd.read_sql("SELECT c_name FROM champions WHERE c_id = {}".format(champion), connection)
                our_champ = our_champ['c_name'][0]
                
                for player in allied_players:
                    player_champ = pd.read_sql("SELECT c_name FROM champions WHERE c_id = {}".format(str(player['championId'])), connection)
                    current_allies = pd.read_sql("SELECT allies FROM matches WHERE match_id = {}".format(match_id), connection)
                    if not current_allies['allies'][0]:
                        run_sql("""UPDATE matches SET allies = "{}" WHERE match_id = {};""".format(our_champ, match_id))
                        current_allies = pd.read_sql("SELECT allies FROM matches WHERE match_id = {}".format(match_id), connection)
                        
                    run_sql("""UPDATE matches SET allies = "{},{}" WHERE match_id = {};""".format(current_allies['allies'][0], player_champ['c_name'][0], match_id))
                
                for enemy in enemy_players:
                    enemy_player_champ = pd.read_sql("SELECT c_name FROM champions WHERE c_id = {}".format(str(enemy['championId'])), connection)
                    current_enemies = pd.read_sql("SELECT enemies FROM matches WHERE match_id = {};".format(match_id), connection)
                    
                    if not current_enemies['enemies'][0]:
                        run_sql("""UPDATE matches SET enemies = "{}" WHERE match_id = {};""".format(enemy_player_champ['c_name'][0], match_id))
                        continue
                    
                    run_sql("""UPDATE matches SET enemies = "{},{}" WHERE match_id = {};""".format(current_enemies['enemies'][0], enemy_player_champ['c_name'][0], match_id))
    return

def update_match_time(new_matches, big_daters):
    print("Updating match duration and start time")
    for match in new_matches:
        match_data = big_daters[int(match)]
        
        start_t = match_data['gameCreation']
        # Creation includes miliseconds which we don't care about.
        start_t = start_t / 1000
        start_t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_t))
        
        # Duration might go over an hour, so i have to use a check for presentability's sake
        duration = match_data['gameDuration']
        if duration > 3600:
            duration = time.strftime("%H:%M:%S", time.gmtime(duration))
        else:
            duration = time.strftime("%M:%S", time.gmtime(duration))
        # Make the sql statements, insert the data, run
        update_start_time = 'UPDATE matches SET start_time = "{}" WHERE match_id = "{}"'.format(start_t, match)
        run_sql(update_start_time)
        update_duration = 'UPDATE matches SET duration = "{}" WHERE match_id = "{}"'.format(duration, match)
        run_sql(update_duration)
        
    return

def update_player_timeline(new_player_matches, big_daters, name):
    print("updating {}'s timeline".format(name))
    for match in new_player_matches:
        select_match_id_and_champion = "SELECT match_id, champion FROM {}_match_history WHERE match_id = {}".format(name, match)
        user_match_history = pd.read_sql(select_match_id_and_champion, connection)
            
        match_id = str(user_match_history['match_id'][0])
        champion = str(user_match_history['champion'][0])
       
        match_data = big_daters[int(match)]
           
        for participant in match_data['participants']:
            participant_champ = str(participant['championId'])
            if participant_champ == champion:
                timeline = participant['timeline']
                
                num_of_deltas = 0
                total_gold = 0
                total_creeps = 0
                creeps = 0
                gpm = 0
                
                # this one might need some work still.
                try:
                    for deltas, value in timeline['goldPerMinDeltas'].items():
                        total_gold += value
                        num_of_deltas += 1
                        
                    gpm = float(total_gold / num_of_deltas)
                        
                    for deltas, value in timeline['creepsPerMinDeltas'].items():
                        total_creeps += value
                        
                    creeps = float(total_creeps / num_of_deltas)
                    break
                except Exception as e:
                    print("NO gold per minute or creeps per minute deltas, GTFO")
                    break
                    
                
        gpm_update = "UPDATE {}_match_history SET gold_per_minute = {} WHERE match_id = {};".format(name, gpm, match)
        run_sql(gpm_update)
        
        creeps_update = "UPDATE {}_match_history SET creeps_per_minute = {} WHERE match_id = {};".format(name, creeps, match)
        run_sql(creeps_update)
                
    return

def update_player_opponent(match, match_data, name, role):
     # pull our role from the DB. If it's none, we outtie.
    if role == "none":
        print("No lane was assigned for {} for match {}, so no enemy_champion can be assigned.".format(name, match))
        return
    
    select_match_id_and_champion = "SELECT match_id, champion, role FROM {}_match_history WHERE match_id = {}".format(name, match)
    user_match_history = pd.read_sql(select_match_id_and_champion, connection)
    
    match_id = str(user_match_history['match_id'][0])
    champion = str(user_match_history['champion'][0])
    lane = str(user_match_history['role'][0])
    
    for participant in match_data['participants']:
        participant_champ = str(participant['championId'])
        
        # If the participant is us, then grab our team.
        if participant_champ == champion:
            team_id = participant['teamId']
            break
        
    player_roles = {}
    support_items = [3301, 3096, 3069, 3033, 3098, 3092, 3302, 3097, 3401]
    for participant in match_data['participants']:
        if participant['teamId'] != team_id:
    
            sql_champ_ratios = pd.read_sql("SELECT top_ratio, jungle_ratio, middle_ratio, bottom_ratio, support_ratio FROM champions WHERE c_id = {}".format(participant['championId']), connection)
            
            champ_ratios = {'top': sql_champ_ratios['top_ratio'][0], 'jungle': sql_champ_ratios['jungle_ratio'][0], 'middle': sql_champ_ratios['middle_ratio'][0], 'bottom': sql_champ_ratios['bottom_ratio'][0], 'support': sql_champ_ratios['support_ratio'][0]}
            player_roles[participant['participantId']] = {'top': 0, 'jungle': 0, 'middle': 0, 'bottom': 0, 'support': 0}
            
            # pull from play ratios
            for position, ratio in champ_ratios.items():
                player_roles[participant['participantId']][position] += ratio
            
            # goes through summoner spells and adds weight
            spell_1 = participant['spell1Id']
            spell_2 = participant['spell2Id']
            # smite is 11
            # heal is 7
            # tp is 12
            
            if spell_1 == 12 or spell_2 == 12:
                # they have TP
                player_roles[participant['participantId']]['top'] += .5
                player_roles[participant['participantId']]['middle'] += .4
             
            if spell_1 == 11 or spell_2 == 11:
                # they have smite
                player_roles[participant['participantId']]['jungle'] += 1
                 
            if spell_1 == 7 or spell_2 == 7:
                # they have heal
                player_roles[participant['participantId']]['bottom'] += .5
            
            # ancient coin 3301
            # nomads medal 3096
            # remnant of the ascended 3069

            # spelltheifs edge 3303
            # frostfang 3098
            # remnant of the watcher 3092
            
            # relic shield 3302
            # targons brace 3097
            # remnant of the aspect 3401
            
            particip_items = [participant['stats']['item1'], participant['stats']['item2'], participant['stats']['item3'], participant['stats']['item4'], participant['stats']['item5'], participant['stats']['item6'], participant['stats']['item0']]

            for item in support_items:
                if item in particip_items:
                    # it's a support item.
                    player_roles[participant['participantId']]['support'] += 1
        
            # trys to make sure we don't mis-classify mid as top.
            highest_score = max(player_roles[participant['participantId']], key=player_roles[participant['participantId']].get)
            
            # if top and middle are the highest, then 
            if float(abs(player_roles[participant['participantId']]['top'] - player_roles[participant['participantId']]['middle'])) < .25 and (highest_score == 'top' or highest_score == "middle"):
                print("ENEMY Top and middle were too close to tell.. BAIL")
                continue
                    
        top_scores = {}
        jungle_scores = {}
        middle_scores = {}
        bottom_scores = {}
        support_scores = {}
        enemy_team = {}
        
        for key, value in player_roles.items():
            for position, score in value.items():
                if position == 'top':
                    top_scores[key] = score
                
                if position == 'jungle':
                    jungle_scores[key] = score
                     
                if position == 'middle':
                    middle_scores[key] = score
                      
                if position == 'bottom':
                    bottom_scores[key] = score
                     
                if position == 'support':    
                    support_scores[key] = score
            
    # now we have 5 dicts like top_score = {1: .2, 2: .5, 6: 1.4, 8: .2, 9: 1}
    enemy_team['top'] = max(top_scores, key=top_scores.get)
    enemy_team['jungle'] = max(jungle_scores, key=jungle_scores.get)
    enemy_team['middle'] = max(middle_scores, key=middle_scores.get)
    enemy_team['bottom'] = max(bottom_scores, key=bottom_scores.get)
    enemy_team['support'] = max(support_scores, key=support_scores.get)
    
    derived_players = []
    # need to make sure that each value is different for these 5 keys.
    for key, value in enemy_team.items():
        derived_players.append(value)
        
    derived_players = set(derived_players)
    if len(derived_players) != 5:
        print("Couldn't figure out where everyone was. BAIL")
        return # we didn't get unique lanes for all 5 people. BAIL
    
    # if everything checks out, then we can pull role here.
    enemy_laner = enemy_team[role]

    for participant in match_data['participants']:
        if participant['participantId'] == enemy_laner:
            enemy_champ = participant['championId']

    opponent_update = """UPDATE {}_match_history SET enemy_champion = {} WHERE match_id = {};""".format(name, enemy_champ, match)
    run_sql(opponent_update)

    opponent_champ_name = pd.read_sql("SELECT c_name FROM champions WHERE c_id = {}".format(str(enemy_champ)), connection)
    opponent_name_update = """UPDATE {}_match_history SET enemy_champion_name = "{}" WHERE match_id = {};""".format(name, opponent_champ_name['c_name'][0], match)
    run_sql(opponent_name_update)
    return

def update_player_role(new_player_matches, big_daters, name):
    print("updating {}'s champions and opponents".format(name))
    for match in new_player_matches:
        select_champion = "SELECT champion, role FROM {}_match_history WHERE match_id = {}".format(name, match)
        user_match_history = pd.read_sql(select_champion, connection)
        role = user_match_history['role'][0]
        champion = str(user_match_history['champion'][0])
       
        match_data = big_daters[match]
        
        player_roles = {}
        support_items = [3301, 3096, 3069, 3033, 3098, 3092, 3302, 3097, 3401]
        for participant in match_data['participants']:
            participant_champ = str(participant['championId'])
            
            # If the participant is us, then grab our team.
            if participant_champ == champion:
                # pull me from DB at a later date.
                sql_champ_ratios = pd.read_sql("SELECT top_ratio, jungle_ratio, middle_ratio, bottom_ratio, support_ratio FROM champions WHERE c_id = {}".format(participant['championId']), connection)
                
                champ_ratios = {'top': sql_champ_ratios['top_ratio'][0], 'jungle': sql_champ_ratios['jungle_ratio'][0], 'middle': sql_champ_ratios['middle_ratio'][0], 'bottom': sql_champ_ratios['bottom_ratio'][0], 'support': sql_champ_ratios['support_ratio'][0]}
                player_roles = {'top': 0, 'jungle': 0, 'middle': 0, 'bottom': 0, 'support': 0}
                
                # pull from play ratios
                for position, ratio in champ_ratios.items():
                    player_roles[position] += ratio
                
                # goes through summoner spells and adds weight
                spell_1 = participant['spell1Id']
                spell_2 = participant['spell2Id']
                
                # smite is 11
                # heal is 7
                # tp is 12
                
                if spell_1 == 12 or spell_2 == 12:
                    # they have TP
                    player_roles['top'] += .5
                    player_roles['middle'] += .4
                 
                if spell_1 == 11 or spell_2 == 11:
                    # they have smite
                    player_roles['jungle'] += 1
                     
                if spell_1 == 12 or spell_2 == 12:
                    # they have heal
                    player_roles['bottom'] += .5
                
                # ancient coin 3301
                # nomads medal 3096
                # remnant of the ascended 3069
    
                # spelltheifs edge 3303
                # frostfang 3098
                # remnant of the watcher 3092
                
                # relic shield 3302
                # targons brace 3097
                # remnant of the aspect 3401
                
                particip_items = [participant['stats']['item1'], participant['stats']['item2'], participant['stats']['item3'], participant['stats']['item4'], participant['stats']['item5'], participant['stats']['item6'], participant['stats']['item0']]
    
                for item in support_items:
                    if item in particip_items:
                        # it's a support item.
                        player_roles['support'] += 1
                
                # trys to make sure we don't mis-classify mid as top.
                if float(abs(player_roles['top'] - player_roles['middle'])) < .25 and (role == 'top' or role == 'middle'):
                    run_sql("UPDATE {}_match_history SET role = '{}' WHERE match_id = {};".format(name, "none", match))
                    print("Player ROLE for Top and middle were too close to tell.. BAIL")
                    break
                
                
                highest_score = max(player_roles, key=player_roles.get)
                run_sql("UPDATE {}_match_history SET role = '{}' WHERE match_id = {};".format(name, highest_score, match))
                
                update_player_opponent(match, match_data, name, highest_score)
    return
    
    
def main():
    
    matches_rows_added = 0
    big_daters = {}
    new_daters = {}

    for name in accounts:
        print("Updating {}'s matches".format(name))
        
        start_index = 0
        bigly_new_user_matches = []
        # Can change the 99 to up to like 2800 (the highest number of games any of the players has played) to gather more matches.
        while start_index <= 3000:
            new_user_matches = add_user_match_history(name, start_index, start_index+100)
            if not new_user_matches:
                break
            
            for match in new_user_matches:
                bigly_new_user_matches.append(match)
                
            start_index += 100
            
        # if there were no new matches added for a user, just move on with our lives.
        if not bigly_new_user_matches:
            print("no new matches to be found for {}".format(name))
            continue
        
        # get a dict of all matches game data by calling get_match_data for each match and adding the json dict
        new_daters = big_daters
        
        for key in list(big_daters.keys()):
            if key not in bigly_new_user_matches:
                del new_daters[key]
                
        for match in bigly_new_user_matches:
            if match not in new_daters:
                new_daters[match] = get_match_data(match)

        big_daters = new_daters
        
        print("added {} new matches to {}".format(len(bigly_new_user_matches), name))
        update_player_data(bigly_new_user_matches, big_daters, name)
        update_player_timeline(bigly_new_user_matches, big_daters, name)
        
        #updates our role, and uses that to find theirs.
        update_player_role(bigly_new_user_matches, big_daters, name)
        # get role?
        
       
        new_matches = add_match_to_matches(bigly_new_user_matches, big_daters, name)
        
        update_team_data(new_matches, big_daters, name)
        update_allies_enemies(new_matches, big_daters, name)
        
        update_match_time(new_matches, big_daters)
        matches_rows_added += len(new_matches)
        
    print("added {} new matches to matches table".format(matches_rows_added))
    
if __name__ == "__main__":
    main()
    
# runeDto
# 	runeId

# fix enemy lane champ.
