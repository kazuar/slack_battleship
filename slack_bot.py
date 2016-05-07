
import time
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

def print_boards(game):
    board1, board2 = game.get_boards()
    message = ["player1 \t\t\t\t\t\t\t player2\n"]
    for i in range(0, len(board1)):
        message.append("{0} \t\t {1}".format(format_row(board1[i]), format_row(board2[i])))
    return "\n".join(message)

def print_board(game):
    message = []
    for row in game._board:
        message.append(" ".join([cell_to_str(cell) for cell in row]))
    return "\n".join(message)

def main():
    # Create the slackclient instance
    sc = SlackClient(BOT_TOKEN)

    game = battleship_game.BattleshipGame()

    game.start_game("first_player", "bot", is_ai = True)

    # Connect to slack
    if sc.rtm_connect():
        # Send first message
        # sc.rtm_send_message(CHANNEL_NAME, "I'm ALIVE!!!")
        message = print_boards(game)
        # message = print_board(game)
        print message
        sc.rtm_send_message(CHANNEL_NAME, message)

        while True:
            # Read latest messages
            for slack_message in sc.rtm_read():
                message = slack_message.get("text")
                user = slack_message.get("user")
                if not message or not user:
                    continue
                if user == "U0XHABXD1":
                    continue
                print "message", user, message
                coords = [int(x) for x in message.replace(",", " ").split(" ")]
                result = game.turn(coords[0], coords[1])
                sc.rtm_send_message(CHANNEL_NAME, print_boards(game))
                if result == battleship_game.HIT:
                    sc.rtm_send_message(CHANNEL_NAME, "GREAT HIT!")
                
                

                # sc.rtm_send_message(CHANNEL_NAME, "<@{}> wrote something...".format(user))
            # Sleep for half a second
            time.sleep(0.5)
    else:
        print("Couldn't connect to slack")

if __name__ == '__main__':
    main()

