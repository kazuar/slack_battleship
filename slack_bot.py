
import time
import random
from slackclient import SlackClient

import battleship_game

BOT_TOKEN = "<BOT_API_KEY>"
CHANNEL_NAME = "general"

def cell_to_str(cell):
    cell = int(cell)
    if cell == 0:
        return ":ocean:"
    elif cell == 1:
        return ":boat:"
    elif cell == -1:
        return ":fire:"
    elif cell == -2:
        return ":x:"

def format_row(row):
    return row.replace("-2", ":x:").replace("-1", ":fire:").replace("0", ":ocean:").replace("1", ":boat:")

def print_boards(game, users):
    board1, board2 = game.get_boards()
    message = ["{0} \t\t\t\t\t\t\t {1}\n".format(users[game._player1._player_name].name, users[game._player2._player_name].name)]
    for i in range(0, len(board1)):
        message.append("{0} \t\t {1}".format(format_row(board1[i]), format_row(board2[i])))
    return "\n".join(message)

def print_board(game, users):
    message = []
    for row in game._board:
        message.append(" ".join([cell_to_str(cell) for cell in row]))
    return "\n".join(message)

def get_bot_user(sc):
    return [user for user in sc.server.users if user.name == sc.server.username][0]

def main():
    # Create the slackclient instance
    sc = SlackClient(BOT_TOKEN)

    game = battleship_game.BattleshipGame()

    # Connect to slack
    if sc.rtm_connect():
        print "bot is up"
        bot_user = get_bot_user(sc)
        users = {user.id: user for user in sc.server.users}

        # Send first message
        # sc.rtm_send_message(CHANNEL_NAME, "I'm ALIVE!!!")
        # message = print_boards(game)
        # message = print_board(game)
        # print message
        # sc.rtm_send_message(CHANNEL_NAME, message)

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

                # sc.rtm_send_message(CHANNEL_NAME, "<@{}> wrote something...".format(user))
            # Sleep for half a second
            time.sleep(0.5)
    else:
        print("Couldn't connect to slack")

if __name__ == '__main__':
    main()

