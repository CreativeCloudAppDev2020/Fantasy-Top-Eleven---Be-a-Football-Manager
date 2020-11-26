"""
This file contains code for the game "Fantasy Top Eleven - Be a Football Manager".
Author: DtjiSoftwareDeveloper
"""


# Game version: 1


# Importing necessary libraries

import sys
import uuid
import pickle
import copy
import random
from datetime import datetime
import os
from mpmath import *

mp.pretty = True


# Static variables


# Both home and away coefficients to help in calculating home and away scores of football matches. Home coefficient >
# away coefficient as there is home advantage for home teams.
HOME_COEFFICIENT = 1.25
AWAY_COEFFICIENT = 1


# Creating static functions to be used throughout the game.


def is_number(string: str) -> bool:
    try:
        mpf(string)
        return True
    except ValueError:
        return False


def triangular(n: int) -> int:
    return int(n * (n - 1) / 2)


def mpf_sum_of_list(a_list: list) -> mpf:
    return mpf(str(sum(mpf(str(elem)) for elem in a_list if is_number(str(elem)))))


def mpf_average_of_list(a_list: list) -> mpf:
    if len(a_list) == 0:
        raise ValueError
    return mpf_sum_of_list(a_list) / len(a_list)


def load_game_data(file_name):
    # type: (str) -> Game
    return pickle.load(open(file_name, "rb"))


def save_game_data(game_data, file_name):
    # type: (Game, str) -> None
    pickle.dump(game_data, open(file_name, "wb"))


def clear():
    # type: () -> None
    if sys.platform.startswith('win'):
        os.system('cls')  # For Windows System
    else:
        os.system('clear')  # For Linux System


# Creating necessary classes


class Manager:
    """
    This class contains attributes of a football manager.
    """

    def __init__(self, name, club):
        # type: (str, Club) -> None
        self.manager_id: str = str(uuid.uuid1())  # Generating random manager ID
        self.name: str = name
        self.club: Club = club

    def clone(self):
        # type: () -> Manager
        return copy.deepcopy(self)


class Club:
    """
    This class contains attributes of a club in this game.
    """

    MIN_FOOTBALL_PLAYERS: int = 16
    MAX_FOOTBALL_PLAYERS: int = 32

    def __init__(self, name, stadium):
        # type: (str, Stadium) -> None
        self.club_id: str = str(uuid.uuid1())  # Generating random club ID
        self.name: str = name
        self.level: int = 1
        self.__player_list: list = []  # initial value
        self.club_academy: ClubAcademy = ClubAcademy()
        self.starting_eleven: StartingEleven = StartingEleven()
        self.home_stadium: Stadium = stadium
        self.budget: mpf = mpf("1e6")
        self.home_dollar_ticket_price: mpf = mpf("1.5")

    def get_skill_level(self):
        # type: () -> mpf
        """
        Calculating the skill level of the club.
        :return: skill level
        """

        return mpf_average_of_list([football_player.get_rating() for football_player in
                                    self.starting_eleven.get_football_players()])

    def get_player_list(self):
        # type: () -> list
        return self.__player_list

    def add_football_player(self, football_player):
        # type: (FootballPlayer) -> bool
        if len(self.__player_list) < self.MAX_FOOTBALL_PLAYERS:
            self.__player_list.append(football_player)
            return True
        return False

    def remove_football_player(self, football_player):
        # type: (FootballPlayer) -> bool
        if football_player in self.__player_list and len(self.__player_list) > self.MIN_FOOTBALL_PLAYERS:
            self.__player_list.remove(football_player)
            return True
        return False

    def clone(self):
        # type: () -> Club
        return copy.deepcopy(self)


class Stadium:
    """
    This class contains attributes of a stadium where matches are held in.
    """

    def __init__(self, name, level_up_dollars_cost):
        # type: (str, mpf) -> None
        self.name: str = name
        self.level: int = 1
        self.capacity: int = 10000
        self.level_up_dollars_cost: mpf = level_up_dollars_cost

    def level_up(self):
        # type: () -> None
        self.level += 1
        self.capacity *= 2
        self.level_up_dollars_cost *= mpf("10") ** self.level

    def clone(self):
        # type: () -> Stadium
        return copy.deepcopy(self)


class ClubAcademy:
    """
    This class contains attributes of the academy of a club.
    """

    def __init__(self):
        # type: () -> None
        self.__football_players: list = []  # initial value

    def get_football_players(self):
        # type: () -> list
        return self.__football_players

    def add_football_player(self, football_player):
        # type: (FootballPlayer) -> None
        self.__football_players.append(football_player)

    def remove_football_player(self, football_player):
        # type: (FootballPlayer) -> bool
        if football_player in self.__football_players:
            self.__football_players.remove(football_player)
            return True
        return False

    def clone(self):
        # type: () -> ClubAcademy
        return copy.deepcopy(self)


class FootballPlayer:
    """
    This class contains attributes of a football player.
    """

    def __init__(self, name, position, country, stats, market_value):
        # type: (str, Position, str, FootballPlayerStats, mpf) -> None
        self.football_player_id: str = str(uuid.uuid1())  # Generating random football player ID
        self.name: str = name
        self.position: Position = position
        self.role: Position = position
        self.__playable_positions: list = [self.position]
        self.country: str = country
        self.age: int = 17
        self.stats: FootballPlayerStats = stats
        self.market_value: mpf = market_value

    def get_playable_positions(self):
        # type: () -> list
        return self.__playable_positions

    def learn_position(self, position):
        # type: (Position) -> bool
        if position not in self.__playable_positions:
            self.__playable_positions.append(position)
            return True
        return False

    def set_role(self, role):
        # type: (Position) -> None
        self.role = role

    def get_rating(self):
        # type: () -> mpf
        """
        Calculating the rating of the football player.
        :return: None
        """

        rating_penalty: float = 0 if self.role in self.__playable_positions else 0.1
        if self.position.position_type in ["GK", "DF"]:
            return mpf_average_of_list([self.stats.get_defense() * 1.15, self.stats.get_attack(),
                                        self.stats.get_physical_and_mental()]) * (1 - rating_penalty)
        elif self.position.position_type == "MF":
            return mpf_average_of_list([self.stats.get_defense(), self.stats.get_attack(),
                                        self.stats.get_physical_and_mental() * 1.15]) * (1 - rating_penalty)
        else:
            return mpf_average_of_list([self.stats.get_defense(), self.stats.get_attack() * 1.15,
                                        self.stats.get_physical_and_mental()]) * (1 - rating_penalty)

    def clone(self):
        # type: () -> FootballPlayer
        return copy.deepcopy(self)


class FootballPlayerStats:
    """
    This class contains attributes of football player stats.
    """

    def __init__(self, tackling, marking, positioning, heading, bravery, passing, dribbling, crossing, shooting,
                 finishing, fitness, strength, aggression, speed, creativity):
        # type: (mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf, mpf) -> None
        self.tackling: mpf = tackling
        self.marking: mpf = marking
        self.positioning: mpf = positioning
        self.heading: mpf = heading
        self.bravery: mpf = bravery
        self.passing: mpf = passing
        self.dribbling: mpf = dribbling
        self.crossing: mpf = crossing
        self.shooting: mpf = shooting
        self.finishing: mpf = finishing
        self.fitness: mpf = fitness
        self.strength: mpf = strength
        self.aggression: mpf = aggression
        self.speed: mpf = speed
        self.creativity: mpf = creativity

    def get_defense(self):
        # type: () -> mpf
        return mpf_average_of_list([self.tackling, self.marking, self.positioning, self.heading, self.bravery])

    def get_attack(self):
        # type: () -> mpf
        return mpf_average_of_list([self.passing, self.dribbling, self.crossing, self.shooting, self.finishing])

    def get_physical_and_mental(self):
        # type: () -> mpf
        return mpf_average_of_list([self.fitness, self.strength, self.aggression, self.speed, self.creativity])

    def clone(self):
        # type: () -> FootballPlayerStats
        return copy.deepcopy(self)


class Position:
    """
    This class contains attributes of a position of a football player.
    """

    POSSIBLE_VALUES: list = ["GK", "CB", "RB", "LB", "DMF", "RWB", "LWB", "CMF", "RMF", "LMF", "AMF", "RW",
                             "LW", "ST", "CF"]

    def __init__(self, value):
        # type: (str) -> None
        self.value: str = value if value in self.POSSIBLE_VALUES else self.POSSIBLE_VALUES[0]
        self.position_type: str = "GK" if self.value == "GK" else "DF" if self.value in ["CB", "RB", "LB"] else \
            "MF" if self.value in ["DMF", "RWB", "LWB", "CMF", "RMF", "LMF", "AMF"] else "FW"

    def clone(self):
        # type: () -> Position
        return copy.deepcopy(self)


class StartingEleven:
    """
    This class contains attributes of a starting eleven of a club.
    """

    NUMBER_OF_PLAYERS: int = 11

    def __init__(self):
        # type: () -> None
        self.__football_players: list = []  # initial value

    def add_football_player(self, football_player):
        # type: (FootballPlayer) -> bool
        if len(self.__football_players) < self.NUMBER_OF_PLAYERS:
            if football_player.role == "GK" and self.goalkeeper_exists():
                return False

            self.__football_players.append(football_player)
            return True
        return False

    def goalkeeper_exists(self):
        # type: () -> bool
        for football_player in self.__football_players:
            if football_player.role == "GK":
                return True

        return False

    def remove_football_player(self, football_player):
        # type: (FootballPlayer) -> bool
        if football_player in self.__football_players:
            self.__football_players.remove(football_player)
            return True
        return False

    def get_football_players(self):
        # type: () -> list
        return self.__football_players

    def clone(self):
        # type: () -> StartingEleven
        return copy.deepcopy(self)


class Competition:
    """
    This class contains attributes of a club competition in this game.
    """

    def __init__(self, name, level, number_of_participants):
        # type: (str, int, int) -> None
        self.competition_id: str = str(uuid.uuid1())  # Generating random competition ID
        self.name: str = str(name.upper()) + " LEVEL " + str(level)
        self.level: int = level
        self.number_of_participants: int = number_of_participants
        self.__participants: list = []  # initial value

    def get_participants(self):
        # type: () -> list
        return self.__participants

    def add_participant(self, participant):
        # type: (Club) -> bool
        if len(self.__participants) < self.number_of_participants:
            self.__participants.append(participant)
            return True
        return False

    def remove_participant(self, participant):
        # type: (Club) -> bool
        if participant in self.__participants:
            self.__participants.remove(participant)
            return True
        return False

    def clone(self):
        # type: () -> Competition
        return copy.deepcopy(self)


class League(Competition):
    """
    This class contains attributes of a league in this game.
    """

    def __init__(self, name, level, number_of_participants, country):
        # type: (str, int, int, str) -> None
        Competition.__init__(self, name, level, number_of_participants)
        self.country: str = country


class LeagueCup(Competition):
    """
    This class contains attributes of a league cup in this game.
    """

    def __init__(self, name, level, number_of_participants, country):
        # type: (str, int, int, str) -> None
        Competition.__init__(self, name, level, number_of_participants)
        self.country: str = country


class ChampionsLeague(Competition):
    """
    This class contains attributes of the Champions League in this game.
    """


class LeagueTable:
    """
    This class contains attributes of the league table.
    """


class FootballMatch:
    """
    This class contains attributes of a football match.
    """

    def __init__(self, home_team, away_team):
        # type: (Club, Club) -> None
        self.home_team: Club = home_team
        self.away_team: Club = away_team

    def home_score(self):
        # type: () -> int
        """
        Generating the home score in the match.
        :return: home score
        """

    def away_score(self):
        # type: () -> int
        """
        Generating the away score in the match.
        :return: away score
        """

    def clone(self):
        # type: () -> FootballMatch
        return copy.deepcopy(self)


class Game:
    """
    This class contains attributes of the saved game data.
    """

    def __init__(self, countries):
        # type: (list) -> None
        self.__countries: list = countries
        self.__clubs: list = []
        self.__football_players: list = []
        self.__leagues: dict = {}  # country is the key
        self.__league_cups: dict = {}  # country level is the key
        self.__champions_leagues: dict = {}  # champions league level is the key

    def remove_retired_players(self):
        # type: () -> None
        for football_player in self.__football_players:
            if football_player.age > 35:
                self.__football_players.remove(football_player)

    def add_new_player(self):
        # type: () -> None
        """
        Adding a new football player
        :return: None
        """

    def add_new_level(self):
        # type: () -> None
        highest_level: int = 0  # initial value
        for league in self.__leagues.values():
            if league.level > highest_level:
                highest_level = league.level

        # TODO: Add league, league cup, and Champions League of level highest_level + 1
        for country in self.__countries:
            new_league: League = League(str(country) + " LEAGUE", highest_level + 1, 20, country)
            self.__leagues[country] = new_league
            new_league_cup: LeagueCup = LeagueCup(str(country) + " LEAGUE CUP", highest_level + 1, 20, country)
            self.__league_cups[country] = new_league_cup
            new_champions_league: ChampionsLeague

    def get_countries(self):
        # type: () -> list
        return self.__countries

    def get_clubs(self):
        # type: () -> list
        return self.__clubs

    def get_football_players(self):
        # type: () -> list
        return self.__football_players

    def get_leagues(self):
        # type: () -> dict
        return self.__leagues

    def get_league_cups(self):
        # type: () -> dict
        return self.__league_cups

    def get_champions_leagues(self):
        # type: () -> dict
        return self.__champions_leagues

    def clone(self):
        # type: () -> Game
        return copy.deepcopy(self)


# Creating main function used to run the game.


def main():
    """
    This main function is used to run the game.
    :return: None
    """

    print("Welcome to 'Fantasy Top Eleven - Be a Football Manager' by 'DtjiSoftwareDeveloper'.")
    print("This game is about managing a football club to make your football club the greatest club ")
    print("in the fantasy world.")


if __name__ == '__main__':
    main()
