import logging
import random
import sys
import argparse
import string
import time
from pprint import pprint

class Game_Play:

    def start_game(self, args):
        factory = PlayerFactory()
        player1 = factory.getPlayer(args.player1)
        self.player_objects.append(player1)
        player2 = factory.getPlayer(args.player2)
        self.player_objects.append(player2)
        return random.choice(self.player_objects)

    def is_winner(self, player):
        if player.score >= 100 or (player.current_roll_total + player.score) >= 100:
            print(f"{player.name} won!")
            sys.exit(0)

    def timeout_winner(self):
        winner = {'score': 0}
        for player in self.player_objects:
            if player.score > winner['score']:
                winner['score'] = player.score
                winner['name'] = player.name
        sys.exit(f"TIMEOUT: Winner is {winner['name']}, with a score of {winner['score']}")

    def get_next_player(self, current_player):
        for i in range(0, self.num_players):
            if current_player.name == self.player_objects[i].name:
                if i == self.num_players-1:
                    i=0
                else:
                    i+=1
                return self.player_objects[i]

    def roll_or_hold(self, current_player, args):
        answer = input(f"Player {current_player.name}: Score {current_player.score}, roll(r) or hold(h)? ")
        if answer != 'r' and answer != 'h':
            print("You must answer with a lowercase r or h")
            answer = input(f"r or h: ")
            self.roll_or_hold(player)
        if answer == 'r':
            return True
        else:
            return False

class TimedGameProxy(Game_Play):
    def __init__(self, args):
        self.start_time = time.time()
        self.end_time = self.start_time + 60
        self.player_objects = []
        self.num_players = 2
        self.start_game(args)

    def has_time_expired(self, player):
        if time.time() > self.end_time:
            # announce the is_winner
            self.timeout_winner()

class Player:
    def __init__(self):
        self.score = 0
        self.current_roll_total = 0

    def make_player(self, name, age):
        self.name = name
        self.age =  age
        self.type = 'human'

    def update_score(self, player, current_roll_total):
        self.score = self.score + self.current_roll_total
        print(f"Current score for {player.name} is {self.score}")

    def update_current_roll_total(self, player, current_roll):
        self.current_roll_total = self.current_roll_total + current_roll
        print(f"Current roll is {current_roll}. Current turn score for {player.name} is {self.current_roll_total} and saved score is {player.score}")

    def get_player_info(self):
        p = input(f"Player Enter your name:")
        a = input(f"Player Enter your age:")
        return (p, a)

class PlayerFactory:
    def __init__(self):
        pass

    def getPlayer(self, player_type):
        if player_type == 'computer':
            print("Initilizing Computer Player...")
            computer_player = ComputerPlayer()
            computer_player.make_player()
            return computer_player

        if player_type == 'human':
            player = Player()
            (p, a) = player.get_player_info()
            player.make_player(p, a)
            return player

class ComputerPlayer(Player):
    def make_player(self):
        self.name = self.make_name()
        self.age = 0
        self.type = 'computer'

    def should_i_hold(self):
        if self.current_roll_total < 25 and self.current_roll_total < (100 - self.current_roll_total):
            return True

    def make_name(self):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(10))

class Turn():

    def roll_dice(self):
        roll = random.randint(1,6)
        return roll

    def is_roll_a_one(self, current_roll):
        if current_roll == 1:
            return True
        else:
            return False

    def user_rolled_1(self, current_player, new_game):
        next_player = new_game.get_next_player(current_player)
        next_player.current_roll_total = 0
        print(f"You rolled a 1: next player up is {next_player.name}")
        return next_player

    def user_scored_points(self, current_player, current_roll, new_game):
        logging.info(f"Current roll is {current_roll} and user is {current_player.name} UPDATE SCORE.")
        current_player.update_current_roll_total(current_player, current_roll)
        new_game.is_winner(current_player)

    def user_held(self, current_player, new_game):
        new_game.is_winner(current_player)
        current_player.update_score(current_player, current_player.update_current_roll_total)
        next_player = new_game.get_next_player(current_player)
        next_player.current_roll_total = 0
        print(f"Current roll total for {next_player.name} is {next_player.current_roll_total}")
        return next_player

def init():
    logging.info("Start Game:")
    parser = argparse.ArgumentParser()
    parser.add_argument("--player1", required=True, choices=['computer', 'human'])
    parser.add_argument("--player2", required=True, choices=['computer', 'human'])
    parser.add_argument("--timed", required=False, dest='timed', action='store_true')
    args = parser.parse_args()
    new_game = TimedGameProxy(args)
    return new_game, args

def main():
    new_game, args = init()
    current_player = random.choice(new_game.player_objects)
    turn = Turn()
    random.seed(0)

    while True:
        new_game.has_time_expired(current_player)
        if current_player.type == 'computer':
            if current_player.should_i_hold():
                current_roll = turn.roll_dice()
                if turn.is_roll_a_one(current_roll):
                    current_player = turn.user_rolled_1(current_player, new_game)
                else:
                    turn.user_scored_points(current_player, current_roll, new_game)
            else:
                current_player = turn.user_held(current_player, new_game)

        if current_player.type == 'human':
            if new_game.roll_or_hold(current_player, args):
                current_roll = turn.roll_dice()
                if turn.is_roll_a_one(current_roll):
                    current_player = turn.user_rolled_1(current_player, new_game)
                else:
                    turn.user_scored_points(current_player, current_roll, new_game)
            else:
                current_player = turn.user_held(current_player, new_game)

if __name__ == '__main__':
    logging.basicConfig(filename='pig.log',level=logging.INFO, filemode='w')
    main()
