import pygame

import constants


def init_pygame(win_size=constants.WINDOW_SIZE, win_caption=constants.CLIENT_CAPTION,
                win_icon=constants.WINDOW_ICON):
    pygame.init()
    window = pygame.display.set_mode(win_size)
    background = pygame.Surface(win_size)
    pygame.Surface([50, 50]).set_alpha(180)
    clock = pygame.time.Clock()
    pygame.display.set_caption(win_caption)
    blokus_icon = pygame.image.load(win_icon)
    pygame.display.set_icon(blokus_icon)
    return window, background, clock


class PlayerEmail:

    def __init__(self):
        # for debugging
        if not constants.ENABLE_INTRO:
            return
        self.done = False
        # draw window
        self.window, self.background, self.clock = init_pygame(win_size=[x for x in constants.WINDOW_SIZE])

        # INPUT - font
        self.font = pygame.font.Font(None, 25)
        self.user_input = ''
        self.emailplayer = ''
        # INPUT - box and color
        self.input_box = pygame.Rect(560, 480, 150, 32)
        self.color_active = pygame.Color('lightskyblue3')
        self.color_passive = pygame.Color('dodgerblue2')
        self.active = False

        self.draw()

    def handle_event(self):
        for event in pygame.event.get():
            # quit
            if event.type == pygame.QUIT:
                self.done = True
                pygame.quit()
                quit()
            # fill and add logo
            self.window.fill(constants.COLORS["DONKER"])
            game_logo = pygame.image.load(constants.INTRO_LOGO).convert()
            logo_rect = game_logo.get_rect(center=self.window.get_rect().center)
            logo_rect.move_ip(0, -80)
            msg_key = "Please input your email : "
            font = pygame.font.SysFont("Trebuchet MS", 25)
            font_dict = font.render(msg_key, False, constants.COLORS["WHITE"])
            pos_rect_dict = pygame.Rect((0, 370, 1280, 100))
            pos_dict = pos_rect_dict.center
            self.window.blit(game_logo, logo_rect)
            self.window.blit(font_dict, font_dict.get_rect(center=pos_dict))

            # textbox event controls
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.input_box.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.user_input = self.user_input[:-1]
                # need further try-except to check ip
                elif event.key == pygame.K_RETURN:
                    if self.user_input != '':
                        temp = self.user_input
                        self.emailplayer = temp
                        self.done = True
                else:
                    self.user_input += event.unicode
            

    def draw(self):
        while not self.done:
            self.handle_event()
            # change colors based on activity
            color = self.color_active if self.active else self.color_passive
            # draw the rectangle
            pygame.draw.rect(self.window, color, self.input_box,2)
            text_surface = self.font.render(self.user_input, True, (255, 255, 255))
            self.window.blit(text_surface, (self.input_box.x + 5, self.input_box.y + 5))
            self.input_box.w = max(150, text_surface.get_width() + 10)
            pygame.display.flip()
            # the fps and update
            self.clock.tick(60)
            pygame.display.update()

if __name__ == "__main__":
    email = PlayerEmail()

