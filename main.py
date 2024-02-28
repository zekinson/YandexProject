import os
import sys
import pygame


pygame.init()
size = width, height = 550, 550
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    global screen, tile_width, tile_height, max_width, max_height
    filename = "data/" + filename
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
    except FileNotFoundError:
        print('уровень не найден')
        terminate()
    max_width = max(map(len, level_map))
    max_height = len(level_map)
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                borders_group.add(Tile('wall', x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


pygame.display.set_caption("Перемещение героя")
clock = pygame.time.Clock()
player = None

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
borders_group = pygame.sprite.Group()

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')

tile_width = tile_height = 50
FPS = 50

def terminate():
    pygame.quit()
    sys.exit()

def start_screen():
    screen.fill('white')
    intro_text = ["Перемещение героя. Дополнительные уровни", "",
                  "Правила игры",
                  "Просто ходите на стрелочки,",
                  "Через коробки ходить нельзя", "",
                  "Введите в консоль название файла с уровнем"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)

running = True
start_screen()
player, level_x, level_y = generate_level(load_level(input('Введите название файла с уровнем(он должен находиться в папке data): ')))
count_h = [0, max_height - 1]
count_w = [0, max_width - 1]
flag_x = True
flag_y = True
camera = Camera()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.dict['scancode'] == 82:
                player.rect = player.rect.move(0, -tile_height)
                if pygame.sprite.spritecollideany(player, borders_group):
                    player.rect = player.rect.move(0, tile_height)
                else:
                    player.rect = player.rect.move(0, tile_height)
                    for i in range(max_height):
                        if i == count_h[1]:
                            for sprite in list(tiles_group)[i * max_width: (i + 1) * max_width]:
                                sprite.rect.y -= tile_height * (max_height - 1)
                        else:
                            for sprite in list(tiles_group)[i * max_width: (i + 1) * max_width]:
                                sprite.rect.y += tile_height
                    count_h[0], count_h[1] = (count_h[0] - 1) % max_height, (count_h[1] - 1) % max_height
            if event.dict['scancode'] == 80:
                player.rect = player.rect.move(-tile_width, 0)
                if pygame.sprite.spritecollideany(player, borders_group):
                    player.rect = player.rect.move(tile_width, 0)
                else:
                    player.rect = player.rect.move(tile_width, 0)
                    for i in range(max_width):
                        if i == count_w[1]:
                            for sprite in list(tiles_group)[i:max_width * max_height:max_width]:
                                sprite.rect.x -= tile_width * (max_width - 1)
                        else:
                            for sprite in list(tiles_group)[i:max_width * max_height:max_width]:
                                sprite.rect.x += tile_width
                    count_w[0], count_w[1] = (count_w[0] - 1) % max_width, (count_w[1] - 1) % max_width
            if event.dict['scancode'] == 81:
                player.rect = player.rect.move(0, tile_height)
                if pygame.sprite.spritecollideany(player, borders_group):
                    player.rect = player.rect.move(0, -tile_height)
                else:
                    player.rect = player.rect.move(0, -tile_height)
                    for i in range(max_height):
                        if i == count_h[0]:
                            for sprite in list(tiles_group)[i * max_width: (i + 1) * max_width]:
                                sprite.rect.y += tile_height * (max_height - 1)
                        else:
                            for sprite in list(tiles_group)[i * max_width: (i + 1) * max_width]:
                                sprite.rect.y -= tile_height
                    count_h[0], count_h[1] = (count_h[0] + 1) % max_height, (count_h[1] + 1) % max_height
            if event.dict['scancode'] == 79:
                player.rect = player.rect.move(tile_width, 0)
                if pygame.sprite.spritecollideany(player, borders_group):
                    player.rect = player.rect.move(-tile_width, 0)
                else:
                    player.rect = player.rect.move(-tile_width, 0)
                    for i in range(max_width):
                        if i == count_w[0]:
                            for sprite in list(tiles_group)[i:max_width * max_height:max_width]:
                                sprite.rect.x += tile_width * (max_width - 1)
                        else:
                            for sprite in list(tiles_group)[i:max_width * max_height:max_width]:
                                sprite.rect.x -= tile_width
                    count_w[0], count_w[1] = (count_w[0] + 1) % (max_width), (count_w[1] + 1) % (max_width)
    screen.fill((0, 0, 0))
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    all_sprites.draw(screen)
    player_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
