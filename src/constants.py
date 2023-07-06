"""
Constants for Blokus
"""

# enable debugging (print to console)

ENABLE_INTRO = True

ENABLE_VERBOSE = 1

root = 'C:/Users/Admin/blockbattle'

# enable audio (false for mute)
ENABLE_AUDIO = False
MUSIC_MENU = root + '/static/assets/audio/music-game.mp3'
PIECES_CLICK = root + '/static/assets/audio/classic-click.wav'
SOUND_NEGATIVE = root + '/static/assets/audio/sound-negative.wav'
FIT_PIECES = root + '/static/assets/audio/fit-pieces.wav'
WRONG_FIT_PIECES = root + '/static/assets/audio/error-click.wav'
GAME_OVER = root + '/static/assets/audio/game-over.wav'


# colors that are used
COLORS = {
    "BLACK": [0, 0, 0],
    "WHITE": [255, 255, 255],
    "RED": [255, 0, 0],
    "GREEN": [0, 255, 0],
    "BLUE": [0, 0, 255],
    "PURPLE": [128, 0, 128],
    "ORANGE": [255, 128, 0],
    "NAVY": [0, 128, 128],
    "DONKER" : [9, 20, 100],
    "MAROON" : [128, 0, 0]
}

# board size (rows x columns)
ROW_COUNT = 14
COLUMN_COUNT = 14

# window properties
CLIENT_CAPTION = "Blockbattle Client"
SERVER_CAPTION = "Blockbattle Server"
WINDOW_ICON = root + "/static/assets/img/blockbattle-icon.png"
INTRO_LOGO = root + "/static/assets/img/blockbattle.png"

# total number of squares in all pieces
STARTING_SCORE = 89

# game window specification
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_SIZE = [WINDOW_WIDTH, WINDOW_HEIGHT]

# value for empty squares
BOARD_FILL_VALUE = 0

# value for player-populated squares
PLAYER1_VALUE = 1
PLAYER2_VALUE = 2
PLAYER3_VALUE = 3
PLAYER4_VALUE = 4

# starting points for players
STARTING_PTS = {"player1": [0, 0],
                "player2": [0, COLUMN_COUNT - 1],
                "player3": [ROW_COUNT - 1, 0],
                "player4": [ROW_COUNT - 1, COLUMN_COUNT - 1]}

# colors for players
HUMAN_PARAMS = {"default_p1": {"color": COLORS["PURPLE"]},
                "default_p2": {"color": COLORS["ORANGE"]},
                "default_p3": {"color": COLORS["RED"]},
                "default_p4": {"color": COLORS["GREEN"]}}

# pickle identifiers
BOARD_ID = "board-pickle"
PLAYER_ID = "player-pickle"


