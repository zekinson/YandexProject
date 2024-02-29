import os
import sys

import pygame


FPS = 50
tile_width = tile_height = 50
pygame.init()
size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
font_button = pygame.font.Font(None, 30)
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
borders_group = pygame.sprite.Group()
doors_group = pygame.sprite.Group()


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
            elif level[y][x] == '0':
                doors_group.add(Tile('door', x, y))
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
        self.image = pygame.transform.scale(player_image, (50, 50))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def shag(self, cord):
        global count
        shag.play()
        count += 1
        self.rect = self.rect.move(cord)
        if pygame.sprite.spritecollideany(self, borders_group):
            self.rect = self.rect.move(cord[0] * -1, cord[1] * -1)
            return False
        elif pygame.sprite.spritecollideany(self, doors_group):
            return 'exit'
        else:
            return 'go'


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


class Button(pygame.sprite.Sprite):
    def __init__(self, image, image_active, x, y, width_, height_, text, action=None):
        super().__init__(button_group)
        self.image = pygame.transform.scale(button_images[image], (width_, height_))
        self.rect = self.image.get_rect().move(x, y)
        self.text = text
        self.action = action
        self.image_active = pygame.transform.scale(button_images[image_active], (width_, height_))
        self.active = False

    def draw(self, screen, font):
        if self.active:
            screen.blit(self.image, self.rect)
        else:
            screen.blit(self.image_active, self.rect)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def action_active(self):
        global level
        click_sound.play()
        if self.action == 'map1.txt' or self.action == 'map2.txt' or self.action == 'map3.txt':
            level = self.action
        elif self.action == '.txt':
            level = False
        elif self.action:
            return self.action()

    def update(self):
        pos = pygame.mouse.get_pos()
        self.active = self.rect.collidepoint(pos)


def action1():
    return 'начать'


def terminate():
    pygame.quit()
    sys.exit()


def loss():
    loss_sound.play()
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = 50
    intro_text = ["Game over", f"Вы сделали {count} шагов", "Но это ещё не конец", "Игрок, сохраняй решимость"]
    text = []
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('purple'))
        text.append(string_rendered)
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = (width - intro_rect.width) // 2
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    button_return = Button('button', 'button_active', 50, 900, 200, 50, "Назад")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.dict['scancode'] == 41:
                    button_return.action_active()
                    button_return.kill()
                    screen.blit(fon, (0, 0))
                    return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.dict['button'] == 1:
                    if button_return.rect.collidepoint(event.pos):
                        button_return.action_active()
                        button_return.kill()
                        screen.blit(fon, (0, 0))
                        return None
        button_return.draw(screen, font_button)
        pygame.display.flip()
        clock.tick(FPS)


def author():
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = 50
    intro_text = ["Вы проиграли", "", "Денег"]
    text = []
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('purple'))
        text.append(string_rendered)
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = (width - intro_rect.width) // 2
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    button_return = Button('button', 'button_active', 50, 900, 200, 50, "Назад")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.dict['scancode'] == 41:
                    button_return.action_active()
                    button_return.kill()
                    screen.blit(fon, (0, 0))
                    return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.dict['button'] == 1:
                    if button_return.rect.collidepoint(event.pos):
                        button_return.action_active()
                        button_return.kill()
                        screen.blit(fon, (0, 0))
                        return None
        button_return.draw(screen, font_button)
        pygame.display.flip()
        clock.tick(FPS)


def rules():
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = 50
    intro_text = ["RobberyCat", "", ""
                  "Правила игры",
                  "Просто ходите на стрелочки,",
                  "Через коробки ходить нельзя", "",
                  "Введите в консоль название файла с уровнем"]
    text = []
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('purple'))
        text.append(string_rendered)
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = (width - intro_rect.width) // 2
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    button_return = Button('button', 'button_active', 50, 900, 200, 50, "Назад")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.dict['scancode'] == 41:
                    button_return.action_active()
                    button_return.kill()
                    screen.blit(fon, (0, 0))
                    return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.dict['button'] == 1:
                    if button_return.rect.collidepoint(event.pos):
                        button_return.action_active()
                        button_return.kill()
                        screen.blit(fon, (0, 0))
                        return None
        button_return.draw(screen, font_button)
        pygame.display.flip()
        clock.tick(FPS)


def start_screen():
    global button_group, level
    screen.fill('white')
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    button_group = pygame.sprite.Group()
    level = 'map1.txt'
    Button('button', 'button_active', 750, 50, 200, 50, "Начать", action1)
    Button('button', 'button_active', 750, 150, 200, 50, "Правила", rules)
    Button('button', 'button_active', 750, 250, 200, 50, "Поддержать автора", author)
    Button('button', 'button_active', 750, 400, 200, 50, "Карта 1", 'map1.txt')
    Button('button', 'button_active', 750, 500, 200, 50, "Kaрта 2", 'map2.txt')
    Button('button', 'button_active', 750, 600, 200, 50, "Kaрта 3", 'map3.txt')
    Button('button', 'button_active', 750, 700, 200, 50, "Своя карта", '.txt')
    Button('button', 'button_active', 750, 900, 200, 50, "Выход", terminate)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.dict['button'] == 1:
                    for button in button_group:
                        if button.rect.collidepoint(event.pos):
                            if button.action_active() == 'начать':
                                return level
        for button in button_group:
            button.draw(screen, font_button)
            button.update()
        pygame.display.flip()
        clock.tick(FPS)


pygame.display.set_caption("Перемещение героя")
clock = pygame.time.Clock()
tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'door': load_image('door.png')
}
button_images = {
    'button': load_image('button.png'),
    'button_active': load_image('button_active.png')
}
player_image = load_image('player.png')
click_sound = pygame.mixer.Sound("data/button_click.mp3")
ost = pygame.mixer.Sound("data/ost.mp3")
shag = pygame.mixer.Sound("data/shag.mp3")
loss_sound = pygame.mixer.Sound("data/loss.mp3")


def game(player, level_x, level_y):
    running = True
    count_h = [0, max_height - 1]
    count_w = [0, max_width - 1]
    ost.play(loops=True)
    camera = Camera()
    button = Button('button', 'button_active', 750, 900, 200, 50, "Меню")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.rect.collidepoint(event.pos):
                    button.action_active()
                    return
            if event.type == pygame.KEYDOWN:
                if event.dict['scancode'] == 41:
                    click_sound.play()
                    return
                if event.dict['scancode'] == 82:
                    action = player.shag([0, -tile_height])
                    if action == 'go':
                        player.rect = player.rect.move(0, tile_height)
                        for i in range(max_height):
                            if i == count_h[1]:
                                for sprite in list(tiles_group)[i * max_width: (i + 1) * max_width]:
                                    sprite.rect.y -= tile_height * (max_height - 1)
                            else:
                                for sprite in list(tiles_group)[i * max_width: (i + 1) * max_width]:
                                    sprite.rect.y += tile_height
                        count_h[0], count_h[1] = (count_h[0] - 1) % max_height, (count_h[1] - 1) % max_height
                    if action == 'exit':
                        return
                if event.dict['scancode'] == 80:
                    action = player.shag([-tile_width, 0])
                    if action == 'go':
                        player.rect = player.rect.move(tile_width, 0)
                        for i in range(max_width):
                            if i == count_w[1]:
                                for sprite in list(tiles_group)[i:max_width * max_height:max_width]:
                                    sprite.rect.x -= tile_width * (max_width - 1)
                            else:
                                for sprite in list(tiles_group)[i:max_width * max_height:max_width]:
                                    sprite.rect.x += tile_width
                        count_w[0], count_w[1] = (count_w[0] - 1) % max_width, (count_w[1] - 1) % max_width
                    if action == 'exit':
                        return
                if event.dict['scancode'] == 81:
                    action = player.shag([0, tile_height])
                    if action == 'go':
                        player.rect = player.rect.move(0, -tile_height)
                        for i in range(max_height):
                            if i == count_h[0]:
                                for sprite in list(tiles_group)[i * max_width: (i + 1) * max_width]:
                                    sprite.rect.y += tile_height * (max_height - 1)
                            else:
                                for sprite in list(tiles_group)[i * max_width: (i + 1) * max_width]:
                                    sprite.rect.y -= tile_height
                        count_h[0], count_h[1] = (count_h[0] + 1) % max_height, (count_h[1] + 1) % max_height
                    if action == 'exit':
                        return
                if event.dict['scancode'] == 79:
                    action = player.shag([tile_width, 0])
                    if action == 'go':
                        player.rect = player.rect.move(-tile_width, 0)
                        for i in range(max_width):
                            if i == count_w[0]:
                                for sprite in list(tiles_group)[i:max_width * max_height:max_width]:
                                    sprite.rect.x += tile_width * (max_width - 1)
                            else:
                                for sprite in list(tiles_group)[i:max_width * max_height:max_width]:
                                    sprite.rect.x -= tile_width
                        count_w[0], count_w[1] = (count_w[0] + 1) % (max_width), (count_w[1] + 1) % (max_width)
                    if action == 'exit':
                        return
        screen.fill((0, 0, 0))
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.draw(screen)
        button.draw(screen, font_button)
        player_group.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()


def start_game():
    global count
    while True:
        count = 0
        level = start_screen()
        if level:
            player, level_x, level_y = generate_level(load_level(level))
        else:
            player, level_x, level_y = generate_level(load_level(input('Введите название файла с уровнем(он должен находиться в папке data): ')))
        result = game(player, level_x, level_y)
        ost.stop()
        if result == None:
            loss()
        for sprite in all_sprites:
            sprite.kill()


start_game()