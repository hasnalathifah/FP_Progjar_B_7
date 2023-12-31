"""
Main Blokus program
"""

from email.mime import audio
import os
import pygame
from threading import Thread  # for threading

import constants
import drawElements
import player
import board
# from audio import AudioController
from networkManager import NetworkManager
from chatBox import ChatBox
from board import Board
from gameIntro import GameIntro
from addemail import PlayerEmail

# game window will be drawn in the center of the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'


def init_pygame():
    pygame.init()
    window = pygame.display.set_mode(constants.WINDOW_SIZE)
    background = pygame.Surface(constants.WINDOW_SIZE)
    pygame.Surface([50, 50]).set_alpha(180)
    clock = pygame.time.Clock()
    pygame.display.set_caption(constants.CLIENT_CAPTION)
    blokus_icon = pygame.image.load(constants.WINDOW_ICON)
    pygame.display.set_icon(blokus_icon)
    return window, background, clock


def init_players(player_init_params):
    player1 = player.Player(constants.PLAYER1_VALUE, player_init_params["p1"]["color"])
    player2 = player.Player(constants.PLAYER2_VALUE, player_init_params["p2"]["color"])
    player3 = player.Player(constants.PLAYER3_VALUE, player_init_params["p3"]["color"])
    player4 = player.Player(constants.PLAYER4_VALUE, player_init_params["p4"]["color"])
    return player1, player2, player3, player4


class Blokus:
    def __init__(self, ip, port, email, player_init_params=None, render=True):
        if render:
            self.screen, self.background, self.clock = init_pygame()
        self.nm = NetworkManager(ip, port)
        # self.audio = AudioController()
        # self.audio.play_music(constants.MUSIC_MENU)
        self.player_symbol = self.nm.recv_data()
        self.offset_list = []
        self.game_over = False
        self.selected = None
        self.gameboard = Board()
        self.board_rects = drawElements.init_gameboard(self.gameboard.board)
        self.infobox_msg_time_start = None
        self.infobox_msg_timeout = 4000
        self.infobox_msg = None
        self.game_check = True
        self.chatbox = ChatBox(960, 670, 300, 30)
        self.win_status = None
        self.email = email

        if player_init_params is None:
            player_init_params = {"p1": constants.HUMAN_PARAMS["default_p1"],
                                  "p2": constants.HUMAN_PARAMS["default_p2"],
                                  "p3": constants.HUMAN_PARAMS["default_p3"],
                                  "p4": constants.HUMAN_PARAMS["default_p4"]}
        self.player1, self.player2, self.player3, self.player4 = init_players(player_init_params)
        self.player_now = str(self.player1.number)

    # handle the events for Blokus
    def event_handler(self, active_player, opponent, opponent2, opponent3):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
                IS_QUIT = True
                self.nm.close_connection()
            elif active_player.is_1st_move is False and self.game_check is False:  # checking if game over | after opponent's move
                self.game_check = True
                active_player.cant_move = self.cant_i_move(active_player)
                active_player.truly_cant_move = active_player.cant_move
            elif active_player.cant_move is True:  # if active player have no more move available
                if opponent.cant_move is True:  # if opponent have no more move available
                    updated_statistics = [self.gameboard.board,
                                          self.player1.score, self.player2.score, self.player3.score,self.player4.score,
                                          self.player1.cant_move, self.player2.cant_move, self.player3.cant_move, self.player4.cant_move,
                                          self.chatbox.chats,
                                          self.win_status, self.player_now]
                    self.nm.send_to_server(updated_statistics)
                    self.game_over = True
                    IS_QUIT = True
                    self.nm.close_connection()
                elif active_player.truly_cant_move is True:  # if this is active player turn
                    active_player.truly_cant_move = False
                    print(f"\nI have no more move..")
                    self.win_status = True
                    updated_statistics = [self.gameboard.board,
                                          self.player1.score, self.player2.score, self.player3.score,self.player4.score,
                                          self.player1.cant_move, self.player2.cant_move, self.player3.cant_move, self.player4.cant_move,
                                          self.chatbox.chats,
                                          self.win_status, self.player_now]
                    self.nm.send_to_server(updated_statistics)
                    # active_player.update_turn()
                # do nothing if this is not active player turn
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if constants.ENABLE_VERBOSE > 1:
                    print("Mouse pos:", pygame.mouse.get_pos())
                # if a piece is selected by the player, check if it can be placed
                if self.selected is not None:
                    if drawElements.are_squares_within_board(active_player.current_piece, self.board_rects):
                        rect_coords = [active_player.current_piece["rects"][0].centerx,
                                       active_player.current_piece["rects"][0].centery]
                        board_arr_coords = drawElements.grid_to_array_coords(rect_coords)
                        # adjusts the coordinates so the piece's arr coord is chosen at [0,0]
                        j = 0
                        while not active_player.current_piece["arr"][0][j] == 1:
                            j += 1
                        board_arr_coords[1] -= j
                        active_player.current_piece["place_on_board_at"] = board_arr_coords

                        # fitting the piece
                        if self.gameboard.fit_piece(active_player.current_piece, active_player, opponent, "player"):
                            # self.audio.play_fit_pieces()
                            self.player_now = str(active_player.number)
                            self.selected = None
                            # send updated board
                            print(f"\nSend updated statistics...")
                            updated_statistics = [self.gameboard.board,
                                                self.player1.score, self.player2.score, self.player3.score,self.player4.score,
                                                self.player1.cant_move, self.player2.cant_move, self.player3.cant_move, self.player4.cant_move,
                                                self.chatbox.chats,
                                                self.win_status, self.player_now]
                            self.nm.send_to_server(updated_statistics)
                            active_player.update_turn()
                            self.game_check = False
                        # display error message if it doesn't fit
                        else:
                            # self.audio.play_wrong_fit_pieces()
                            self.display_infobox_msg_start("not_valid_move")
                    # clear the selection if clicking outside the board
                    else:
                        self.selected = None
                # else check if there's a need to pick up a piece
                else:
                    # self.audio.play_pickup_pieces()
                    self.offset_list, self.selected = drawElements.generate_element_offsets(
                        active_player.remaining_pieces, event)
                    if self.selected is not None:
                        active_player.current_piece["piece"] = self.selected
                        active_player.current_piece["arr"] = active_player.remaining_pieces[self.selected]["arr"]
                        active_player.current_piece["rects"] = active_player.remaining_pieces[self.selected]["rects"]
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.player_symbol == 'p1':
                    drawElements.init_piece_rects(self.player1.remaining_pieces)
                elif self.player_symbol == 'p2':
                    drawElements.init_piece_rects(self.player2.remaining_pieces)
                elif self.player_symbol == 'p3':
                    drawElements.init_piece_rects(self.player3.remaining_pieces)
                else:
                    drawElements.init_piece_rects(self.player4.remaining_pieces)
            elif event.type == pygame.KEYDOWN:
                if self.selected is not None:
                    self.key_controls(event, active_player)
            # handle chatbox event
            updated_chatbox = self.chatbox.handle_event(event, self.player_symbol)
            if updated_chatbox:
                updated_statistics = [self.gameboard.board,
                                    self.player1.score, self.player2.score, self.player3.score,self.player4.score,
                                    self.player1.cant_move, self.player2.cant_move, self.player3.cant_move, self.player4.cant_move,
                                    self.chatbox.chats,
                                    self.win_status, self.player_now]
                self.nm.send_to_server(updated_statistics)
        return active_player, opponent, opponent2, opponent3

    def cant_i_move(self, player):
        return self.gameboard.is_no_more_move(player)

    def key_controls(self, event, active_player):
        # rotate left
        if event.key == pygame.K_LEFT:
            active_player.rotate_current_piece()
            self.offset_list = drawElements.draw_rotated_flipped_selected_piece(active_player.current_piece)
        # rotate right
        elif event.key == pygame.K_RIGHT:
            active_player.rotate_current_piece(False)
            self.offset_list = drawElements.draw_rotated_flipped_selected_piece(active_player.current_piece)
        # flip diagonally
        elif event.key == pygame.K_UP:
            active_player.flip_current_piece()
            self.offset_list = drawElements.draw_rotated_flipped_selected_piece(active_player.current_piece)

    def display_infobox_msg_start(self, msg_key):
        self.infobox_msg_time_start = pygame.time.get_ticks()
        self.infobox_msg = msg_key

    def display_infobox_msg_end(self, end_now=False):
        if end_now:
            self.infobox_msg_time_start = None
        elif pygame.time.get_ticks() - self.infobox_msg_time_start > self.infobox_msg_timeout:
            self.infobox_msg_time_start = None

    def recv_msg(self):
        # receive the statistics and update it
        while not self.game_over:
            try:
                updated_statistics = self.nm.recv_pickle()
                if self.chatbox.chats != updated_statistics[9]:
                    self.chatbox.chats = updated_statistics[9]
                    continue
                self.gameboard.board = updated_statistics[0]
                self.player1.score = updated_statistics[1]
                self.player2.score = updated_statistics[2]
                self.player3.score = updated_statistics[3]
                self.player4.score = updated_statistics[4]
                self.win_status = updated_statistics[10]
                self.player_now = updated_statistics[11]
                if self.player_symbol == 'p1' and self.player_now == str(self.player4.number):
                    self.player1.update_turn()
                    self.player2.cant_move = updated_statistics[6]
                    self.player3.cant_move = updated_statistics[7]
                    self.player4.cant_move = updated_statistics[8]
                    self.player1.truly_cant_move = True
                elif self.player_symbol == 'p2' and self.player_now == str(self.player1.number):
                    self.player2.update_turn()
                    self.player1.cant_move = updated_statistics[5]
                    self.player3.cant_move = updated_statistics[7]
                    self.player4.cant_move = updated_statistics[8]
                    self.player2.truly_cant_move = True
                elif self.player_symbol == 'p3' and self.player_now == str(self.player2.number):
                    self.player3.update_turn()
                    self.player1.cant_move = updated_statistics[5]
                    self.player2.cant_move = updated_statistics[6]
                    self.player4.cant_move = updated_statistics[8]
                    self.player3.truly_cant_move = True
                elif self.player_symbol == 'p4' and self.player_now == str(self.player3.number):
                    self.player4.update_turn()
                    self.player1.cant_move = updated_statistics[5]
                    self.player2.cant_move = updated_statistics[6]
                    self.player3.cant_move = updated_statistics[7]
                    self.player4.truly_cant_move = True
            except:
                break


def game_loop():
    intro = GameIntro()
    email = PlayerEmail()
    blokus = Blokus(intro.server_ip, intro.server_port, email.emailplayer)

    if blokus.player_symbol == 'p1':
        active_player, opponent, opponent2, opponent3 = blokus.player1, blokus.player2, blokus.player3, blokus.player4
        drawElements.init_piece_rects(blokus.player1.remaining_pieces)
    elif blokus.player_symbol == 'p2':
        active_player, opponent, opponent2, opponent3 = blokus.player2, blokus.player3, blokus.player4, blokus.player1
        drawElements.init_piece_rects(blokus.player2.remaining_pieces)
    elif blokus.player_symbol == 'p3':
        active_player, opponent, opponent2, opponent3 = blokus.player3, blokus.player4, blokus.player1, blokus.player2
        drawElements.init_piece_rects(blokus.player3.remaining_pieces)
    else:
        active_player, opponent, opponent2, opponent3 = blokus.player4, blokus.player1, blokus.player2, blokus.player3
        drawElements.init_piece_rects(blokus.player4.remaining_pieces)

    Thread(target=blokus.recv_msg, ).start()

    is_over = 0
    while not blokus.game_over:
        # listening to player's input
        active_player, opponent, opponent2, opponent3 = blokus.event_handler(active_player, opponent, opponent2, opponent3 )
        # set the background
        blokus.background.fill(constants.COLORS["NAVY"])

        """
        Draw the UI components
        """
        #text boxes
        drawElements.draw_infobox(blokus.background, blokus.player1, blokus.player2, blokus.player3, blokus.player4, active_player,
                                  blokus.gameboard.turn_number)
        if blokus.infobox_msg_time_start is not None:
            drawElements.draw_infobox_msg(blokus.background, blokus.player1, blokus.player2, blokus.player3, blokus.player4, blokus.infobox_msg)
            blokus.display_infobox_msg_end()

        # draw game board and selected pieces
        drawElements.draw_gameboard(blokus.background, blokus.board_rects, blokus.gameboard,
                                    active_player.current_piece, active_player)
        drawElements.draw_pieces(blokus.background, blokus.player1, blokus.player2, blokus.player3, blokus.player4, active_player, blokus.selected)
        if blokus.selected is not None:
            drawElements.draw_selected_piece(blokus.background, blokus.offset_list, pygame.mouse.get_pos(),
                                             active_player.current_piece, active_player.color)

        if blokus.win_status is not None:
            # pgc.game_over = True
            # blokus.audio.play_game_over()
            blokus.display_infobox_msg_start("game_over")
            blokus.game_over = True
            is_over = is_over+1

        if is_over == 1 :
            board.send_score(blokus.player1.score, blokus.player2.score,blokus.player3.score,blokus.player4.score, email.emailplayer)
            
        # draw chat box
        blokus.chatbox.update()
        blokus.chatbox.draw(blokus.background)

        # blit the screen
        blokus.screen.blit(blokus.background, (0, 0))

        # limit the fps to 60
        blokus.clock.tick(60)

        # update the screen
        pygame.display.update()

    # board.send_score(blokus.player1.score, blokus.player2.score,blokus.player3.score,blokus.player4.score, email.emailplayer)


if __name__ == "__main__":
    IS_QUIT = False
    game_loop()

    if IS_QUIT:
        pygame.quit()
