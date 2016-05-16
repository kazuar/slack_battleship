
import re
import time
import datetime
import random
import argparse
from slackclient import SlackClient

import battleship_game

CHANNEL_NAME = "general"

BATTLESHIP_TO_EMOJI = {
    battleship_game.SEA: ":ocean:",
    battleship_game.SHIP: ":boat:",
    battleship_game.HIT: ":fire:",
    battleship_game.MISS: ":x:"
}

BOT_SLEEP_TIME = 0.5

class SlackBot(object):

    def __init__(self, token_api):
        self._token_api = token_api
        self._sc = SlackClient(token_api)
        self._game = battleship_game.BattleshipGame()

        if self._sc.rtm_connect():
            self._users = {user.id: user for user in self._sc.server.users}
            self._bot_user_name = self._sc.server.username
            self._bot_user = [user for user in self._users.values() if user.name == self._bot_user_name][0]
        else:
            raise Exception("Failed to connect to slack")

    def _get_user_name_from_message(self, message):
        user_regex = re.compile("<@([A-Za-z0-9]*)>")
        res = user_regex.search(message)
        if not res:
            return None
        return res.groups()[0]

    def _process_message(self, message):
        text = message.get("text")
        user_id = message.get("user")
        if not text or not user_id or user_id == self._bot_user.id:
            return
        user = self._users[user_id]
        print "message from {0} ({1}): {2}".format(user.name, user.id, text)
        if text.startswith("start game"):
            user_name = self._get_user_name_from_message(message)
            if user_name:
                self._send_new_message("Hello", user_name)

            bot_message = "start new game: {0} ({1}) vs {2} ({3})".format(user.name, user.id, bot_user.name, bot_user.id)
            print bot_message
            self._send_new_message(bot_message)
            self._game.start_game(user.id, bot_user.id)
            self._send_new_message(print_boards(game, users))
            first_player_id = self._game._current_player._player_name
            self._send_new_message("first player: {0} ({1})".format(users[first_player_id].name, first_player_id))
        elif text.replace(" ", "").isdigit():
            coords = [int(x) for x in text.replace(",", " ").split(" ")]
            result = self._game.turn(coords[0], coords[1])
            self._send_new_message(print_boards(self._game, users))
            if result == battleship_game.SHIP:
                self._send_new_message("Good hit!")
            elif result == battleship_game.WIN:
                first_player_id = self._game._current_player._player_name
                self._send_new_message("<@{0}> won the game".format(users[first_player_id].name))

    def _get_new_messages(self):
        return self._sc.rtm_read()

    def _send_new_message(self, text, channel_name = CHANNEL_NAME):
        self._sc.rtm_send_message(CHANNEL_NAME, text)

    def _bot_loop(self):
        for slack_message in self._get_new_messages():
            self._process_message(slack_message)

        if self._game._current_player and self._game._current_player._player_name == bot_user.id:
            rand_col = random.randint(0, battleship_game.BOARD_SIZE - 1)
            rand_row = random.randint(0, battleship_game.BOARD_SIZE - 1)
            result = self._game.turn(rand_col, rand_row)
            bot_message = "bot turn: {0}, {1}".format(rand_col, rand_row)
            print bot_message
            self._send_new_message(bot_message)
            self._send_new_message(print_boards(self._game, users))
            if result == battleship_game.SHIP:
                self._send_new_message("WOOOHOOOOOO!!!! IN YOUR FACE!!!")
            elif result == battleship_game.WIN:
                self._send_new_message("YES!!! BOT RULESSSS!")
        return

    def run(self):
        print datetime.datetime.now(), "bot is up"
        while True:
            self._bot_loop()
            time.sleep(BOT_SLEEP_TIME)

def format_row(row):
    for key, emoji in BATTLESHIP_TO_EMOJI.items():
        row = row.replace(str(key), emoji)
    return row

def print_boards(game, users):
    player1_details, player2_details = game.get_players_boards()
    message = ["{0} \t\t\t\t\t\t\t {1}\n".format(users[player1_details["player_id"]].name, users[player2_details["player_id"]].name)]
    for i in range(0, len(player1_details["board"])):
        board1_row = format_row(player1_details["board"][i])
        board2_row = format_row(player2_details["board"][i])
        message.append("{0} \t\t {1}".format(board1_row, board2_row))
    return "\n".join(message)

def main():
    # Read slack api token from arguments
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-t', '--token',
        dest='api_token', required=True, help='Slack bot API token'
    )
    args = parser.parse_args()

    # Run the bot
    bot = SlackBot(args.api_token)
    bot.run()

if __name__ == '__main__':
    main()
