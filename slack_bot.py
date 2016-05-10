
import time
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

def get_bot_user(sc):
    return [user for user in sc.server.users if user.name == sc.server.username][0]

def main():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-t', '--token',
        dest='api_token', required=True, help='Slack bot API token'
    )
    args = parser.parse_args()

    # Create the slackclient instance
    sc = SlackClient(args.api_token)

    game = battleship_game.BattleshipGame()

    # Connect to slack
    if sc.rtm_connect():
        print "bot is up"
        bot_user = get_bot_user(sc)
        users = {user.id: user for user in sc.server.users}

        while True:
            # Read latest messages
            for slack_message in sc.rtm_read():
                message = slack_message.get("text")
                user_id = slack_message.get("user")
                if not message or not user_id:
                    continue
                if user_id == bot_user.id:
                    continue
                user = users[user_id]
                print "message", user_id, message
                # message = " ".join(message.split(" ")[1:])
                bot_message = None
                if message == "start game":
                    bot_message = "start new game: {0} ({1}) vs {2} ({3})".format(user.name, user.id, bot_user.name, bot_user.id)
                    print bot_message
                    sc.rtm_send_message(CHANNEL_NAME, bot_message)
                    game.start_game(user.id, bot_user.id)
                    sc.rtm_send_message(CHANNEL_NAME, print_boards(game, users))
                    first_player_id = game._current_player._player_name
                    sc.rtm_send_message(CHANNEL_NAME, "first player: {0} ({1})".format(users[first_player_id].name, first_player_id))
                elif message.replace(" ", "").isdigit():
                    coords = [int(x) for x in message.replace(",", " ").split(" ")]
                    result = game.turn(coords[0], coords[1])
                    sc.rtm_send_message(CHANNEL_NAME, print_boards(game, users))
                    if result == battleship_game.SHIP:
                        sc.rtm_send_message(CHANNEL_NAME, "Good hit!")
                    elif result == battleship_game.WIN:
                        first_player_id = game._current_player._player_name
                        sc.rtm_send_message(CHANNEL_NAME, "<@{0}> won the game".format(users[first_player_id].name))

            if game._current_player and game._current_player._player_name == bot_user.id:
                rand_col = random.randint(0, battleship_game.BOARD_SIZE - 1)
                rand_row = random.randint(0, battleship_game.BOARD_SIZE - 1)
                result = game.turn(rand_col, rand_row)
                bot_message = "bot turn: {0}, {1}".format(rand_col, rand_row)
                print bot_message
                sc.rtm_send_message(CHANNEL_NAME, bot_message)
                sc.rtm_send_message(CHANNEL_NAME, print_boards(game, users))
                if result == battleship_game.SHIP:
                    sc.rtm_send_message(CHANNEL_NAME, "WOOOHOOOOOO!!!! IN YOUR FACE!!!")
                elif result == battleship_game.WIN:
                    first_player_id = game._current_player._player_name
                    sc.rtm_send_message(CHANNEL_NAME, "YES!!! BOT RULESSSS!")

            time.sleep(0.5)
    else:
        print("Couldn't connect to slack")

if __name__ == '__main__':
    main()

