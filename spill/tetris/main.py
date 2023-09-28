import pygame
import random
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.joystick.init()


# VAR GLOBAL
skjerm_bredde = 700
skjerm_hoyde = 700
Skjerm_bredde = 300
spill_hoyde = 600
blokk_storrelse = 30
x_top_venstre = (skjerm_bredde - Skjerm_bredde) // 2
y_top_venstre = skjerm_hoyde - spill_hoyde

# tetris former
L_form = [['.....', '...0.', '.000.', '.....', '.....'],
          ['.....', '..0..', '..0..', '..00.', '.....'],
          ['.....', '.....', '.000.', '.0...', '.....'],
          ['.....', '.00..', '..0..', '..0..', '.....']]
O_form = [['.....', '.....', '.00..', '.00..', '.....']]
I_form = [['..0..', '..0..', '..0..', '..0..', '.....'],
          ['.....', '0000.', '.....', '.....', '.....']]
S_form = [['.....', '.....', '..00.', '.00..', '.....'],
          ['.....', '..0..', '..00.', '...0.', '.....']]
Z_form = [['.....', '.....', '.00..', '..00.', '.....'],
          ['.....', '..0..', '.00..', '.0...', '.....']]
J_form = [['.....', '.0...', '.000.', '.....', '.....'],
          ['.....', '..00.', '..0..', '..0..', '.....'],
          ['.....', '.....', '.000.', '...0.', '.....'],
          ['.....', '..0..', '..0..', '.00..', '.....']]
T_form = [['.....', '..0..', '.000.', '.....', '.....'],
          ['.....', '..0..', '..00.', '..0..', '.....'],
          ['.....', '.....', '.000.', '..0..', '.....'],
          ['.....', '..0..', '.00..', '..0..', '.....']]

# form og form_farge indikserer hvert form fra 0-6 og gir hvert enkelt farger.
former = [L_form, O_form, I_form, S_form, Z_form, J_form, T_form]
form_farge = [(137, 129, 108),
              (84, 105, 109),
              (49, 100, 107),
              (252, 248, 22),
              (52, 66, 48),
              (231, 237, 130),
              (99, 13, 58)]


def skap_rutenett(locked_positions=None):
    if locked_positions is None:
        locked_positions = {}
    grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid


class Figur(object):
    rows = 20
    columns = 10

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = form_farge[former.index(shape)]
        self.rotation = 0


def figur_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def reel_plass(shape, grid):
    acc_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    acc_pos = [j for sub in acc_pos for j in sub]
    formatted = figur_format(shape)

    for pos in formatted:
        if pos not in acc_pos:
            if pos[1] > -1:
                return False

    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def faa_figur():
    global former, form_farge
    return Figur(5, 0, random.choice(former))


def tekts_midten(text, size, color, surface):
    font = pygame.font.SysFont('font/Roboto-Black.ttf', 50)
    label = font.render(text, True, color)

    surface.blit(label, (x_top_venstre + Skjerm_bredde / 2 - (label.get_width() / 2),
                         y_top_venstre + spill_hoyde / 2 - label.get_height() / 2))


def tegn_rutenett(surface, row, col):
    sx = x_top_venstre
    sy = y_top_venstre
    for i in range(row):
        # horisontale linjer
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * 30),
                         (sx + Skjerm_bredde, sy + i * 30))
        # vertikale linjer
        for j in range(col):
            pygame.draw.line(surface, (128, 128, 128), (sx + j * 30, sy),
                             (sx + j * 30, sy + spill_hoyde))


def full_linje(grid, locked):

    # sjekker om linje er klarert og flytter ned linje ned.

    global fjern
    klarert = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            klarert += 1
            # spiller av musikk når klarert.
            cleared_song = pygame.mixer.Sound('musikk/clear.wav')
            cleared_song.play()

            fjern = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if klarert > 0:
        for tast in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = tast
            if y < fjern:
                nytt_tast = (x, y + klarert)
                locked[nytt_tast] = locked.pop(tast)
    return klarert


def faa_neste_figur(shape, surface):
    skjermy = y_top_venstre + spill_hoyde / 2 - 100
    skjermx = x_top_venstre + Skjerm_bredde + 50
    format = shape.shape[shape.rotation % len(shape.shape)]

    skrift_type = pygame.font.SysFont('font/Roboto-Black.ttf', 35)
    neste_figur = skrift_type.render('Neste Figur', True, (255, 255, 255))

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (skjermx + j * 30, skjermy + i * 30, 30, 30), 0)

    surface.blit(neste_figur, (skjermx + 0, skjermy - 30))

def draw_window(surface, poeng=0):
    surface.fill((0, 0, 0))
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (x_top_venstre + j * 30, y_top_venstre + i * 30, 30, 30), 0)

    tegn_rutenett(surface, 20, 10)
    pygame.draw.rect(surface, (255, 0, 0), (x_top_venstre, y_top_venstre, Skjerm_bredde, spill_hoyde), 5)

    skjermy = y_top_venstre + spill_hoyde / 2 - 100
    skjermx = x_top_venstre + Skjerm_bredde + 50

    skrift_type = pygame.font.SysFont('font/Roboto-Black.ttf', 60)
    poeng = skrift_type.render('Poeng: ' + str(poeng), True, (255, 255, 255))

    surface.blit(poeng, (skjermx -280, skjermy - 260))


def main():
    global grid
    laast_pos = {}
    grid = skap_rutenett(laast_pos)
    change_piece = False
    run = True
    Fall_tid = 0
    naa_fig = faa_figur()
    clock = pygame.time.Clock()
    neste_figur = faa_figur()
    poeng = 0
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for joystick in joysticks:
        print(joystick.get_name())

    while run:
        fall_speed = 0.24
        grid = skap_rutenett(laast_pos)
        Fall_tid += clock.get_rawtime()
        clock.tick()

        # får tetris formene til å falle nedover.
        if Fall_tid / 1000 >= fall_speed:
            Fall_tid = 0
            naa_fig.y += 1
            if not (reel_plass(naa_fig, grid)) and naa_fig.y > 0:
                naa_fig.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            # KONTROLLER.           ### funker ikke.
            ''''
            if event.type == pygame.JOYHATMOTION:
                print(event)

                # får formene til å gå til venstre.
                if event.value == pygame.CONTROLLER_BUTTON_DPAD_LEFT:
                    naa_fig.x -= 1
                    if not reel_plass(naa_fig, grid):
                        naa_fig.x += 1

                # flytter brikkene til høyre
                elif event.value == pygame.CONTROLLER_BUTTON_DPAD_RIGHT:
                    naa_fig.x += 1
                    if not reel_plass(naa_fig, grid):
                        naa_fig.x -= 1

                # roterer formene.
                elif event.value == pygame.CONTROLLER_BUTTON_DPAD_UP:
                    naa_fig.rotation = naa_fig.rotation + 1 % len(naa_fig.shape)
                    if not reel_plass(naa_fig, grid):
                        naa_fig.rotation = naa_fig.rotation - 1 % len(naa_fig.shape)

                #  får formene til å falle fortere ned.
                if event.value == pygame.CONTROLLER_BUTTON_DPAD_DOWN:
                    naa_fig.y += 1
                    if not reel_plass(naa_fig, grid):
                        naa_fig.y -= 1
                '''''

            # sjekker om en tast har blitt trykket inn. # KEYBOARD
            if event.type == pygame.KEYDOWN:

                # får formene til å gå til venstre.
                if event.key == pygame.K_LEFT:
                    naa_fig.x -= 1
                    if not reel_plass(naa_fig, grid):
                        naa_fig.x += 1

                # flytter brikkene til høyre
                elif event.key == pygame.K_RIGHT:
                    naa_fig.x += 1
                    if not reel_plass(naa_fig, grid):
                        naa_fig.x -= 1

                # roterer formene.
                elif event.key == pygame.K_UP:
                    naa_fig.rotation = naa_fig.rotation + 1 % len(naa_fig.shape)
                    if not reel_plass(naa_fig, grid):
                        naa_fig.rotation = naa_fig.rotation - 1 % len(naa_fig.shape)

                #  får formene til å falle fortere ned.
                if event.key == pygame.K_DOWN:
                    naa_fig.y += 1
                    if not reel_plass(naa_fig, grid):
                        naa_fig.y -= 1

        shape_pos = figur_format(naa_fig)

        # legger til formen i gridden
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = naa_fig.color

        # hvis formen faller på bakken.
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                laast_pos[p] = naa_fig.color
            naa_fig = neste_figur
            neste_figur = faa_figur()
            change_piece = False
            poeng += full_linje(grid, laast_pos) * 1

            # call four times to check for multiple clear rows
            full_linje(grid, laast_pos)

        draw_window(programm, poeng)
        faa_neste_figur(neste_figur, programm)
        pygame.display.update()

        # Check if user lost
        if check_lost(laast_pos):
            run = False

    tekts_midten('Du Tapte', 40, (255, 255, 255), programm)
    taps_musikk = pygame.mixer.Sound('musikk/gameover.wav')
    taps_musikk.play()
    pygame.display.update()
    pygame.time.delay(1500)


def main_menu():
    run = True
    while run:
        programm.fill((0, 0, 0))
        tekts_midten('trykk på en tast for å begynne.', 80, (255, 255, 255), programm)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main()
            if event.type == pygame.JOYHATMOTION:
                main()
    pygame.quit()


# spiller av tetris theme i loop.
bakgrunnsmusikk = pygame.mixer.Sound('musikk/Tetris_theme_song.wav')
bakgrunnsmusikk.play(loops=-1)
bakgrunnsmusikk.set_volume(0.01)

# gir navn
programm = pygame.display.set_mode((skjerm_bredde, skjerm_hoyde))
pygame.display.set_caption('Tetris')

# starter spillet
main_menu()
