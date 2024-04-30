import os
import sys
import pygame


FPS = 60
tile_width = tile_height = 100
pygame.init()
size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
font_button = pygame.font.Font(None, 30)
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
borders_group = pygame.sprite.Group()
doors_group = pygame.sprite.Group()
death_group = pygame.sprite.Group()
animated_group = pygame.sprite.Group()
ohran_group = pygame.sprite.Group()
diamond_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
safe_group = pygame.sprite.Group()
breack_group = pygame.sprite.Group()


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
            elif level[y][x] == 'F':
                Tile('wall', x, y)
            elif level[y][x] == 'S':
                safe_group.add(Tile('safe', x, y))
            elif level[y][x] == 'R':
                breack_group.add(Tile('breack_wall', x, y))
            elif level[y][x] == '#':
                borders_group.add(Tile('wall', x, y))
            elif level[y][x] == '0':
                doors_group.add(Tile('door', x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(load_image("player.png"), 2, 1, x * tile_width, y * tile_height)
            elif level[y][x] == '!':
                death_group.add(Tile('lazer_v', x, y))
            elif level[y][x] == '1':
                death_group.add(Tile('lazer_h', x, y))
            elif level[y][x] == 'L':
                death_group.add(Tile('lazer', x, y))
            elif level[y][x] == 'D':
                Tile('empty', x, y)
                diamond = AnimatedSprite(load_image('diamond.png'), 2, 1, x * tile_width, y * tile_height)
                diamond_group.add(diamond)
            elif level[y][x] == 'C':
                Tile('empty', x, y)
                Item(item_images['card'], 2, 1, x * tile_width, y * tile_height, 'card')
            elif level[y][x] == 'I':
                Tile('empty', x, y)
                Item(item_images['dynamite'], 2, 1, x * tile_width, y * tile_height, 'dynamite')
            elif level[y][x] == 'T':
                Tile('empty', x, y)
                Item(item_images['pickaxe'], 2, 1, x * tile_width, y * tile_height, 'pickaxe')
            elif level[y][x] == 'v':
                Tile('empty', x, y)
                ohran = Ohran(load_image("ohran.png"), 2, 1, x * tile_width,
                              y * tile_height, [x, y], [0, 50])
                death_group.add(ohran)
                ohran_group.add(ohran)
            elif level[y][x] == 'h':
                Tile('empty', x, y)
                ohran = Ohran(load_image("ohran.png"), 2, 1, x * tile_width,
                              y * tile_height, [x, y], [50, 0])
                death_group.add(ohran)
                ohran_group.add(ohran)
    return new_player, x, y


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, need=30, tile_width=100, tile_height=100):
        super().__init__(animated_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.tile_width, self.tile_height = tile_width, tile_height
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (self.tile_width, self.tile_height))
        self.x = x
        self.y = y
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.count = 0
        self.need = 30

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.count += 1
        if self.count == self.need:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.image = pygame.transform.scale(self.image, (self.tile_width, self.tile_height))
            self.count = 0


class Item(AnimatedSprite):
    def __init__(self, sheet, columns, rows, x, y, text):
        super().__init__(sheet, columns, rows, x, y)
        self.add(item_group)
        self.text = text
        self.x = x
        self.y = y


class Ohran(AnimatedSprite):
    def __init__(self, sheet, columns, rows, x, y, pos, speed, need=30):
        super().__init__(sheet, columns, rows, x, y, need)
        self.pos = pos
        self.v = speed

    def update(self):
        super().update()
        self.x += self.v[0] / FPS
        self.rect.x += self.v[0] / FPS
        if (pygame.sprite.spritecollideany(self, borders_group) or pygame.sprite.spritecollideany(self, safe_group) or
            pygame.sprite.spritecollideany(self, breack_group) or pygame.sprite.spritecollideany(self, doors_group)):
            self.v[0] *= -1
            self.x += self.v[0] / FPS
            self.rect.x += self.v[0] / FPS
        self.y += self.v[1] / FPS
        self.rect.y += self.v[1] / FPS
        if (pygame.sprite.spritecollideany(self, borders_group) or pygame.sprite.spritecollideany(self, safe_group) or
            pygame.sprite.spritecollideany(self, breack_group) or pygame.sprite.spritecollideany(self, doors_group)):
            self.v[1] *= -1
        if pygame.sprite.spritecollideany(self, player_group):
            return True


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, x, y):
        super().__init__(tiles_group, all_sprites)
        self.image = pygame.transform.scale(tile_images[tile_type], (tile_width, tile_height))
        self.rect = self.image.get_rect().move(
            tile_width * x, tile_height * y)
        self.pos = [x, y]


class Player(AnimatedSprite):
    def __init__(self, sheet, columns, rows, x, y, need=30):
        super().__init__(sheet, columns, rows, x, y, need)
        player_group.add(self)
        self.inventory = []
        self.inv = []
        screen.blit(self.image, (self.x, self.y))

    def update_inventory(self, cord=False):
        if cord:
            self.rect.x -= cord[0]
            self.rect.y -= cord[1]
        for i in range(len(self.inventory)):
            self.inventory[i].rect.x = self.rect.x - 450 + i * 100
            self.inventory[i].rect.y = self.rect.y + 450

    def shag(self, cord):
        global count_shag, count
        shag.play()
        self.rect.x += cord[0]
        self.rect.y += cord[1]
        if len(self.inv) != len(self.inventory):
            self.inv = list(map(lambda x: x.text, self.inventory))
        self.update_inventory()
        if pygame.sprite.spritecollideany(self, borders_group):
            self.update_inventory(cord)
            return False
        elif pygame.sprite.spritecollideany(self, breack_group):
            if 'pickaxe' in self.inv:
                for sprite in breack_group:
                    breack_sound.play()
                    if pygame.sprite.spritecollideany(sprite, player_group):
                        sprite.image = tile_images['empty']
                        breack_group.remove(sprite)
            self.update_inventory(cord)
            return False
        elif pygame.sprite.spritecollideany(self, safe_group):
            if 'dynamite' in self.inv:
                for sprite in safe_group:
                    if pygame.sprite.spritecollideany(sprite, player_group):
                        explosion_sound.play()
                        sprite.image = tile_images['empty']
                        diamond = AnimatedSprite(load_image('diamond.png'), 2, 1, sprite.rect.x, sprite.rect.y)
                        diamond_group.add(diamond)
                        safe_group.remove(sprite)
            self.update_inventory(cord)
            return False
        elif pygame.sprite.spritecollideany(self, doors_group):
            if 'card' in self.inv:
                count_shag += 1
                return 'exit'
            else:
                self.update_inventory(cord)
                return False
        elif pygame.sprite.spritecollideany(self, death_group):
            count_shag += 1
            return 'loss'
        elif pygame.sprite.spritecollideany(self, diamond_group):
            for diamond in diamond_group:
                if pygame.sprite.spritecollideany(diamond, player_group):
                    diamond_sound.play()
                    diamond.kill()
                    count += 1
        elif pygame.sprite.spritecollideany(self, item_group):
            collect_sound.play()
            for item in item_group:
                if pygame.sprite.spritecollideany(item, player_group):
                    self.inventory.append(Item(item_images[item.text], 2, 1,
                                               self.rect.x - 450, self.rect.y + 450, item.text))
                    item.kill()
        count_shag += 1


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        if type(obj) == AnimatedSprite:
            obj.x += self.dx
            obj.y += self.dy
            obj.rect.x += self.dx
            obj.rect.y += self.dy
        else:
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


def kill():
    for sprite in all_sprites:
        sprite.kill()


def win():
    win_sound.play()
    fon = pygame.transform.scale(load_image('fon_win.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 70)
    intro_text = [f"{count}", f"{count_shag}"]
    text = []
    intro_text[0], intro_text[1] = (font.render(intro_text[0], 1, pygame.Color('blue')),
                                    font.render(intro_text[1], 1, pygame.Color('blue')))
    text.append(intro_text[0])
    text.append(intro_text[1])
    intro_rect = intro_text[0].get_rect()
    intro_rect_ = intro_text[1].get_rect()
    intro_rect.top = 100
    intro_rect_.top = 170
    intro_rect.x = 730
    intro_rect_.x = 620
    screen.blit(intro_text[0], intro_rect)
    screen.blit(intro_text[1], intro_rect_)
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
        button_return.update()
        pygame.display.flip()
        clock.tick(FPS)



def loss():
    loss_sound.play()
    fon = pygame.transform.scale(load_image('fon_loss.png'), (width, height))
    screen.blit(fon, (0, 0))
    button_return = Button('button', 'button_active', 750, 900, 200, 50, "Назад")
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
        button_return.update()
        pygame.display.flip()
        clock.tick(FPS)


def author():
    fon = pygame.transform.scale(load_image('fon_author.png'), (width, height))
    screen.blit(fon, (0, 0))
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
        button_return.update()
        pygame.display.flip()
        clock.tick(FPS)


def rules():
    fon = pygame.transform.scale(load_image('fon_rule.png'), (width, height))
    screen.blit(fon, (0, 0))
    button_return = Button('button', 'button_active', 200, 900, 200, 50, "Назад")
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
        button_return.update()
        pygame.display.flip()
        clock.tick(FPS)


def start_screen():
    global button_group, level
    screen.fill('white')
    fon = AnimatedSprite(load_image('fon.png'), 6, 1, 0, 0, tile_width=1000, tile_height=1000)
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
        fon.update()
        screen.blit(fon.image, (0, 0))
        for button in button_group:
            button.draw(screen, font_button)
            button.update()
        pygame.display.flip()
        clock.tick(FPS)

#sdsd
pygame.display.set_caption("RoberryCat")
clock = pygame.time.Clock()
tile_images = {
    'wall': load_image('wall.png'),
    'breack_wall': load_image('breack_wall.png'),
    'empty': load_image('pol.png'),
    'door': load_image('door.png'),
    'lazer_v': load_image('lazer_v.png'),
    'lazer_h': load_image('lazer_h.png'),
    'lazer': load_image('lazer.png'),
    'safe': load_image('safe.png')
}
button_images = {
    'button': load_image('button.png'),
    'button_active': load_image('button_active.png')
}
item_images = {
    'card': load_image('card.png'),
    'dynamite': load_image('dynamite.png'),
    'pickaxe': load_image('pickaxe.png')
}
player_image = load_image('player.png')
click_sound = pygame.mixer.Sound("data/button_click.mp3")
ost = pygame.mixer.Sound("data/ost.mp3")
shag = pygame.mixer.Sound("data/shag.mp3")
loss_sound = pygame.mixer.Sound("data/loss.mp3")
win_sound = pygame.mixer.Sound("data/win.mp3")
diamond_sound = pygame.mixer.Sound("data/diamond_sound.mp3")
collect_sound = pygame.mixer.Sound("data/collect.mp3")
explosion_sound = pygame.mixer.Sound("data/explosion.mp3")
breack_sound = pygame.mixer.Sound("data/breack_sound.mp3")


def game(player, level_x, level_y):
    running = True
    ost.play(loops=True)
    camera = Camera()
    button = Button('button', 'button_active', 750, 900, 200, 50, "Меню")
    while running:
        for event in pygame.event.get():
            action = False
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
                if event.dict['scancode'] == 80:
                    action = player.shag([-tile_width, 0])
                if event.dict['scancode'] == 81:
                    action = player.shag([0, tile_height])
                if event.dict['scancode'] == 79:
                    action = player.shag([tile_width, 0])
                if action == 'exit':
                    return 'win'
                if action == 'loss':
                    return 'loss'

        screen.fill((0, 0, 0))
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.draw(screen)
        for sprite in animated_group:
            if type(sprite) != Ohran:
                sprite.update()
        for ohran in ohran_group:
            if ohran.update():
                return 'loss'
        animated_group.draw(screen)
        button.draw(screen, font_button)
        button.update()
        player_group.draw(screen)
        for i in range(len(player.inventory)):
            player.inventory[i].rect.x = player.rect.x - 450 + i * 100
            player.inventory[i].rect.y = player.rect.y + 450
        clock.tick(FPS)
        pygame.display.flip()


def start_game():
    global count, count_shag
    while True:
        count = 0
        count_shag = 0
        level = start_screen()
        kill()
        if level:
            player, level_x, level_y = generate_level(load_level(level))
        else:
            player, level_x, level_y = generate_level(load_level(input('Введите название файла с уровнем(он должен находиться в папке data): ')))
        result = game(player, level_x, level_y)
        ost.stop()
        kill()
        if result == 'loss':
            loss()
        elif result == 'win':
            win()
        kill()


start_game()
