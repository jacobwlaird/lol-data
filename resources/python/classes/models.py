""" models.py

    This python file contains all the models we'll use in this project. That means one model for
    every table in our database.

"""
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, String, DateTime, Time,\
        Float, Text

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

#pylint: disable=too-many-instance-attributes # This should be fine for models.
#pylint: disable=too-many-arguments # this is fine for models.
#pylint: disable=too-few-public-methods # also fine for models.
#pylint: disable=C0103 # columns are named id, which makes the linter angry.
#pylint: disable=W0622 # columns are named id, which makes the linter angry.
#pylint: disable=too-many-locals # Should be fine. Tables too large maybe?
class TeamData(Base):
    """ TeamData is the model for our team_data table.

        # bunch of stuff to add here. Don't puss out.
        Attributes:
            match_id          (int): Primary Key; the match_id for the match.
            game_version      (str): The version of the game that the match was played on.
            win               (str): Did our team win the game?
            participants      (str): List of friends we had in the game.

    """
    __tablename__ = "team_data"
    match_id = Column(BigInteger, primary_key=True)
    game_version = Column(String(40))
    win = Column(String(10))
    participants = Column(String(80))
    first_blood = Column(SmallInteger)
    first_baron= Column(SmallInteger)
    first_tower = Column(SmallInteger)
    first_dragon = Column(SmallInteger)
    first_inhib = Column(SmallInteger)
    first_rift_herald = Column(SmallInteger)
    ally_dragon_kills = Column(Integer)
    ally_rift_herald_kills = Column(Integer)
    inhib_kills = Column(Integer)
    bans = Column(String(80))
    enemy_bans = Column(String(80))
    allies = Column(String(80))
    enemies = Column(String(80))
    enemy_dragon_kills = Column(Integer)
    enemy_rift_herald_kills = Column(Integer)
    start_time = Column(DateTime)
    duration = Column(Time)

    def __init__(self, match_id=None, participants=None, win=None, first_blood=None,\
            first_baron=None, first_tower=None, first_rift_herald=None,\
            ally_rift_herald_kills=None, first_dragon=None, ally_dragon_kills=None,\
            first_inhib=None, inhib_kills=None, bans=None, enemy_bans=None, game_version=None,\
            allies=None,enemies=None, start_time=None, enemy_rift_herald_kills=None,\
            enemy_dragon_kills=None, duration=None):


        self.match_id = match_id
        self.participants = participants
        self.win = win
        self.first_blood = first_blood
        self.first_baron = first_baron
        self.first_tower = first_tower
        self.first_rift_herald = first_rift_herald
        self.ally_rift_herald_kills = ally_rift_herald_kills
        self.first_dragon = first_dragon
        self.ally_dragon_kills = ally_dragon_kills
        self.first_inhib = first_inhib
        self.inhib_kills = inhib_kills
        self.bans = bans
        self.enemy_bans = enemy_bans
        self.game_version = game_version
        self.allies = allies
        self.enemies = enemies
        self.start_time = start_time
        self.enemy_rift_herald_kills = enemy_rift_herald_kills
        self.enemy_dragon_kills = enemy_dragon_kills
        self.duration = duration

class MatchData(Base):
    """ MatchData is the model for our match_data table.

        Attributes:
            match_id          (int): Primary Key; the match_id for the match.
            game_version      (str): The version of the game that the match was played on.

    """
    __tablename__ = "match_data"
    id = Column(Integer, primary_key=True)
    match_id = Column(BigInteger)
    player = Column(String(40))
    role = Column(String(10))
    champion = Column(Integer)
    champion_name = Column(String(40))
    enemy_champion = Column(Integer)
    enemy_champion_name = Column(String(40))
    first_blood = Column(SmallInteger)
    first_blood_assist = Column(SmallInteger)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    damage_to_champs = Column(Integer)
    damage_to_turrets = Column(Integer)
    gold_per_minute = Column(Float)
    creeps_per_minute = Column(Float)
    xp_per_minute = Column(Float)
    wards_placed = Column(Integer)
    vision_wards_bought = Column(Integer)
    wards_killed = Column(Integer)
    items = Column(String(200))
    perks = Column(String(100))

    def __init__(self, id=None, match_id = None, player = None, role = None, champion = None,\
            champion_name = None, enemy_champion = None, enemy_champion_name = None,\
            first_blood = None, first_blood_assist = None, kills = None, deaths = None,\
            assists = None, damage_to_champs = None, damage_to_turrets = None,\
            gold_per_minute = None, creeps_per_minute = None, xp_per_minute = None,\
            wards_placed = None, vision_wards_bought = None, wards_killed = None,\
            items = None, perks = None, win = None):

        self.id = id
        self.match_id = match_id
        self.player = player
        self.role = role
        self.champion = champion
        self.champion_name = champion_name
        self.enemy_champion = enemy_champion
        self.enemy_champion_name = enemy_champion_name
        self.first_blood = first_blood
        self.first_blood_assist = first_blood_assist
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.damage_to_champs = damage_to_champs
        self.damage_to_turrets = damage_to_turrets
        self.gold_per_minute = gold_per_minute
        self.creeps_per_minute = creeps_per_minute
        self.xp_per_minute = xp_per_minute
        self.wards_placed = wards_placed
        self.vision_wards_bought = vision_wards_bought
        self.wards_killed = wards_killed
        self.items = items
        self.perks = perks

class LeagueUsers(Base):
    """ TeamData is the model for our team_data table.

        Attributes:
            id              (int): Primary Key; the id for each user.
            summoner_name   (str): The summoner name of the user
            riot_id         (str): The unique riot id for the user.

    """
    __tablename__ = "league_users"
    id = Column(Integer, primary_key=True)
    summoner_name = Column(String(30))
    riot_id = Column(String(400))

    def __init__(self, id=None, summoner_name = None, riot_id = None):
        self.id = id
        self.summoner_name = summoner_name
        self.riot_id = riot_id

class ScriptRuns(Base):
    """ ScriptRuns is the model for our script_runs table.

        Attributes:
            id              (int): Primary Key; the id for each script run.
            source          (str): Where the script is running. [Prod, test, manual], etc.
            status          (str): The outcome of the script. [Success, Failure]
            matches_added   (str): A list of matches added by this script run.
            start_time      (dte): the start time of this script run.
            end_time        (dte): the end time of this script run.
            message         (str): A column for any error messages encountered during the run.

    """
    __tablename__ = "script_runs"
    id = Column(Integer, primary_key=True)
    source = Column(String(50))
    status = Column(String(20))
    matches_added = Column(String(60000))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    message = Column(String(1000))


    def __init__(self, id=id, source = None, status = None, matches_added = None,\
            start_time = None, end_time = None, message = None):
        self.id = id
        self.source = source
        self.status = status
        self.matches_added = matches_added
        self.start_time = start_time
        self.end_time = end_time
        self.message = message

class JsonData(Base):
    """ JsonData is the model for our json_data table.

        Attributes:
            match_id        (int): Primary Key; the match_id associated with this json_data.
            json_data       (txt): The raw json returned by riot games api.

    """
    __tablename__ = "json_data"
    __table_args__ = {"mysql_default_charset":"utf8"}

    match_id = Column(BigInteger, primary_key=True)
    json_data = Column(Text)

    def __init__(self, match_id=None, json_data = None):
        self.match_id = match_id
        self.json_data = json_data

class Champions(Base):
    """ Champions is the model for the champions table.

        Attributes:
            key         (int): Primary Key; the integer associated with this champion.
            id          (str): The short identifier for the champion. Ex: Nunu for Nunu & Willump
            name        (str): The full name of the champion
            title       (str): The flavor title for the champion Ex: The Dark Child (Annie)
            blurb       (str): The flavor text for the champion. Their backstory.

    """

    __tablename__ = "champions"
    key = Column(Integer, primary_key=True)
    id = Column(String(30))
    name = Column(String(30))
    title = Column(String(50))
    blurb = Column(String(400))

    def __init__(self, key=None, id=None, name=None, title=None, blurb=None):
        self.key = key
        self.id = id
        self.name = name
        self.title = title
        self.blurb = blurb


class Items(Base):
    """ Item is the model for the items table.

        Attributes:
            key         (int): Primary Key; the integer associated with this item.
            name        (str): The full name of the item

    """

    __tablename__ = "items"
    key = Column(Integer, primary_key=True)
    name = Column(String(60))

    def __init__(self, key=None, name=None):
        self.key = key
        self.name = name
