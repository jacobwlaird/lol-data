import sqlalchemy as db
import configparser
from sqlalchemy import orm
from sys import argv

import pymysql

# well this script won't be used much, but alright we really out here.
accounts = ['spaynkee', 'dumat', 'archemlis', 'stylus_crude', 'dantheninja6156', 'csqward']

aws_config = configparser.ConfigParser()
aws_config.read('./aws.cfg')

aws_db_host = aws_config.get('DATABASE', 'db_id')
aws_db_user = aws_config.get('DATABASE', 'db_user')
aws_db_pw = aws_config.get('DATABASE', 'db_password')
aws_db_name = aws_config.get('DATABASE', 'db_name')

aws_engine = db.create_engine('mysql+pymysql://{}:{}@{}/{}'.format(aws_db_user, aws_db_pw, aws_db_host, aws_db_name), pool_size=100, max_overflow = 100)
aws_connection = aws_engine.connect()
aws_metadata = db.MetaData()
aws_sm = orm.sessionmaker(bind=aws_engine, autoflush=True, autocommit=False, expire_on_commit=True)
aws_matches_table = db.Table('matches', aws_metadata, autoload=True, autoload_with=aws_engine)

config = configparser.ConfigParser()
config.read('./general.cfg')

db_host = config.get('DATABASE', 'db_id')
db_user = config.get('DATABASE', 'db_user')
db_pw = config.get('DATABASE', 'db_password')
db_name = config.get('DATABASE', 'db_name')

engine = db.create_engine('mysql+pymysql://{}:{}@{}/{}'.format(db_user, db_pw, db_host, db_name), pool_size=100, max_overflow = 100)
connection = engine.connect()
metadata = db.MetaData()
sm = orm.sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=True)
matches_table = db.Table('matches', metadata, autoload=True, autoload_with=engine)

# for getting rows, something like this.
aws_session = orm.scoped_session(aws_sm)
results = aws_session.query(aws_matches_table).all() # this may not be all()
aws_session.close()

update = argv[1]
# updates the matches table
for row in results:
    try:
        matches_table_insert = db.insert(matches_table).values(match_id=row.match_id, 
                participants=row.participants,
                win=row.win,
                first_blood=row.first_blood,
                first_baron=row.first_baron,
                first_tower=row.first_tower,
                first_rift_herald=row.rift_herald,
                rift_herald_kills=None,
                first_dragon=row.first_dragon,
                dragon_kills=row.dragon_kills,
                first_inhib=None,
                inhib_kills=None,
                bans=None,
                enemy_bans=None,
                game_version=None,
                allies=row.allies,
                enemies=row.enemies,
                start_time=row.start_time,
                duration=row.duration
                )

        results = connection.execute(matches_table_insert)
        print("Adding {} to matches...".format(row.match_id))
    except Exception as e:
        continue

# get user_matches
for account in accounts:
    aws_user_matches_table = db.Table('{}_match_history'.format(account), aws_metadata, autoload=True, autoload_with=aws_engine)
    user_matches_table = db.Table('{}_match_history'.format(account), metadata, autoload=True, autoload_with=engine)

    aws_session = orm.scoped_session(aws_sm)
    results = aws_session.query(aws_user_matches_table).all() 
    aws_session.close()

    for row in results:
        if update == False:
            try:
                user_matches_insert = user_matches_table.insert().values(
                        match_id=row.match_id,
                        kills=row.kills,
                        deaths=row.deaths,
                        assists=row.assists,
                        role=row.role,
                        wards_placed=row.wards_placed,
                        damage_to_champs=row.damage_to_champions,
                        damage_to_turrets=row.damage_to_turrets,
                        vision_wards_bought=row.vision_wards_bought,
                        gold_per_minute=row.gold_per_minute,
                        creeps_per_minute=row.creeps_per_minute,
                        xp_per_minute=None,
                        champion=row.champion,
                        champion_name=row.champion_name,
                        enemy_champion=row.enemy_champion,
                        enemy_champion_name=row.enemy_champion_name,
                        first_blood=row.first_blood,
                        first_blood_assist=row.first_blood_assist,
                        items=None,
                        perks=None,
                        wards_killed=row.wards_killed)

                results = connection.execute(user_matches_insert)
                print("updating {} match history with match {}".format(account, row.match_id))
            except Exception as e:
                continue

        else:
            user_matches_update = user_matches_table.update().values(
                    kills=row.kills,
                    deaths=row.deaths,
                    assists=row.assists,
                    role=row.role,
                    wards_placed=row.wards_placed,
                    damage_to_champs=row.damage_to_champions,
                    damage_to_turrets=row.damage_to_turrets,
                    vision_wards_bought=row.vision_wards_bought,
                    gold_per_minute=row.gold_per_minute,
                    creeps_per_minute=row.creeps_per_minute,
                    xp_per_minute=None,
                    champion=row.champion,
                    champion_name=row.champion_name,
                    enemy_champion=row.enemy_champion,
                    enemy_champion_name=row.enemy_champion_name,
                    first_blood=row.first_blood,
                    first_blood_assist=row.first_blood_assist,
                    items=None,
                    perks=None,
                    wards_killed=row.wards_killed).where(user_matches_table.c.match_id==row.match_id)

            results = connection.execute(user_matches_update)
            print("updating {} match history with match {}".format(account, row.match_id))

