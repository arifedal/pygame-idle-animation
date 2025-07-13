import pgzero
import pgzrun
import random
import pygame

WIDTH = 700
HEIGHT = 406
FPS = 30

pygame.mixer.init()

def load_sound(path, volume=0.7):
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        print(f"Loaded sound: {path}")
        return sound
    except Exception as e:
        print(f"Failed to load {path}: {e}")
        return None

#musics
try:
    pygame.mixer.music.load("music/arkaplan.wav")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Music error: {e}")

enemy_die_sound = load_sound("sounds/enemy_die.wav")
character_die_sound = load_sound("sounds/character_die.wav")
character2_die_sound = load_sound("sounds/character_die.wav")

# Globals
mod = "menü"
game_over = False
last_mode = "none"
is_moving = False
direction = "right"

idle_images_right = ["character", "character_idle1"]
idle_images_left = ["character_idle1", "character"]
idle_index = 0
idle_timer = 0
idle_delay = 0.5

# Characters
character = Actor("character")
character2 = Actor("character")
characters = [character, character2]

enemies_by_mode = {
    "mode1": [
        Actor("enemy", (74, 280)),
        Actor("enemy_left", (150, 33)),
        Actor("enemy", (330, 33)),
        Actor("enemy_left", (427, 140)),
        Actor("enemy", (638,140)),
        Actor("enemy", (510, 280))
    ],
    "mode2": [
        Actor("enemy", (70, 307)),
        Actor("enemy_left", (145, 103)),
        Actor("enemy", (335, 60)),
        Actor("enemy_left", (400, 206)),
        Actor("enemy", (565,275)),
        Actor("enemy", (550, 115))
    ]
}

for c in characters:
    c.attack = random.randint(5,10)
    c.health = 100

for enemy_list in enemies_by_mode.values():
    for e in enemy_list:
        e.health = 100
        e.attack = random.randint(1,5)

# Actors
bg = Actor("bg")
bgoyun = Actor("background0")
bg1 = Actor("bg1")
bg2 = Actor("bg2")
play = Actor("play_button", (350,150))
musicOn = Actor("music_on", (310,240))
musicOff = Actor("music_off", (390,240))
close = Actor("close_button", (350,310))
carpi = Actor("çarpı", (670,30))
mode1_btn = Actor("mode1", (230, 210))
mode2_btn = Actor("mode2", (500, 210))

GRAVITY = 4
JUMP_STRENGTH = 100

platforms = [Rect((0, 310), (700, 57)), Rect((45,60), (300, 60)), Rect((360,162), (400, 65))]
platforms2 = [
    Rect((0, 400), (700,0)), Rect((10,332), (120, 3)), Rect((146,254), (122, 3)),
    Rect((20,205), (70, 3)), Rect((100,127), (105, 3)), Rect((252,83), (105, 3)),
    Rect((362,230), (98, 3)), Rect((466,137), (154, 3)), Rect((545,295), (110, 3))
]

platforms_by_mode = {"mode1": platforms, "mode2": platforms2}
backgrounds_by_mode = {"mode1": bg1, "mode2": bg2}

def is_on_platform(actor, platform_list):
    return any(actor.colliderect(p) and actor.y + actor.height/2 <= p.top + 5 for p in platform_list)

def draw_enemies(enemies):
    for e in enemies:
        if e.health > 0:
            e.draw()

def draw_platforms(platforms):
    for p in platforms:
        screen.draw.rect(p, (0, 255, 0))

def draw_hud(character):
    can_renk = "green" if character.health >= 70 else "orange" if character.health >= 30 else "red"
    screen.draw.text(f"Can: {character.health}", topleft=(10, HEIGHT - 40), fontsize=16, color=can_renk)
    screen.draw.text(f"Saldırı Gücü: {character.attack}", topleft=(10, HEIGHT - 20), fontsize=16, color="white")

def draw_main_menu():
    bg.draw()
    play.draw()
    musicOn.draw()
    musicOff.draw()
    close.draw()

def draw_mode_select():
    bgoyun.draw()
    carpi.draw()
    screen.draw.text("Girmek istediğiniz modu seçiniz", center = (350,70), color = "white", fontsize = 36)
    mode1_btn.draw()
    mode2_btn.draw()

def draw_game_mode(mode):
    screen.clear()
    backgrounds_by_mode[mode].draw()
    carpi.draw()
    screen.draw.text("Düşmanların üzerine gidin ve onları yenin!", center = (350,390), color = "green", fontsize = 20)
    hero = character if mode == "mode1" else character2
    hero.draw()
    draw_enemies(enemies_by_mode[mode])
    draw_platforms(platforms_by_mode[mode])
    draw_hud(hero)
    if game_over:
        screen.draw.text("Düşman seni öldürdü, kaybettin!", center=(WIDTH // 2, HEIGHT // 2), fontsize=48, color="red")

def start_music():
    try:
        pygame.mixer.music.unpause()
        pygame.mixer.music.set_volume(0.7)
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
        print("Music started")
    except Exception as e:
        print(f"Error starting music: {e}")

def stop_music():
    try:
        pygame.mixer.music.pause()
        print("Music paused")
    except Exception as e:
        print(f"Error stopping music: {e}")

def on_mouse_down(button, pos):
    global mod
    
    if mod == "menü" and play.collidepoint(pos):
        mod = "oyunmode"
    elif mod == "menü" and musicOn.collidepoint(pos):
        start_music()
    elif mod == "menü" and musicOff.collidepoint(pos):
        stop_music()
    elif mod == "oyunmode" and mode1_btn.collidepoint(pos):
        mod = "mode1"
    elif mod == "oyunmode" and mode2_btn.collidepoint(pos):
        mod = "mode2"
    elif mod == "oyunmode" and carpi.collidepoint(pos):
        mod = "menü"
    elif (mod in ["mode1", "mode2"] or mod == "oyunsonu") and carpi.collidepoint(pos):
        reset_game()
    elif mod == "menü" and close.collidepoint(pos):
        exit()

def move_character(char, keys, platform_list):
    global is_moving, direction
    moved = False

    if (keys.left or keys.a) and char.x > 20:
        char.x -= 10
        char.image = "character_left"
        direction = "left"
        moved = True
    elif (keys.right or keys.d) and char.x < WIDTH - 20:
        char.x += 10
        char.image = "character"
        direction = "right"
        moved = True

    if keys.space and is_on_platform(char, platform_list):
        char.y -= JUMP_STRENGTH

    is_moving = moved
    return moved

def update_character(mode, char, enemies, platform_list):
    global game_over, last_mode, idle_index, idle_timer, is_moving, direction

    if not is_on_platform(char, platform_list):
        char.y += GRAVITY
    if char.y > HEIGHT:
        char.y = HEIGHT - 50

    for enemy in enemies:
        if enemy.health > 0 and char.colliderect(enemy):
            old_health = enemy.health
            enemy.health -= char.attack
            char.health -= enemy.attack
            if old_health > 0 and enemy.health <= 0 and enemy_die_sound:
                enemy_die_sound.play()

    if char.health <= 0:
        if mode == "mode1" and character_die_sound:
            character_die_sound.play()
        elif mode == "mode2" and character2_die_sound:
            character2_die_sound.play()
        game_over = True
        last_mode = mode
        mod = "oyunsonu"

    if not is_moving:
        idle_timer += 1/FPS
        if idle_timer >= idle_delay:
            idle_timer = 0
            idle_index = (idle_index + 1) % len(idle_images_right)
            if direction == "right":
                char.image = idle_images_right[idle_index]
            else:
                char.image = idle_images_left[idle_index]

def update(dt):
    global mod
    if mod == "mode1":
        move_character(character, keyboard, platforms)
        update_character("mode1", character, enemies_by_mode["mode1"], platforms)
    elif mod == "mode2":
        move_character(character2, keyboard, platforms2)
        update_character("mode2", character2, enemies_by_mode["mode2"], platforms2)

def reset_game():
    global game_over, mod, idle_index, idle_timer, is_moving, direction
    idle_index = 0
    idle_timer = 0
    is_moving = False
    direction = "right"
    
    character.pos = (30, 0)
    character.health = 100
    character.attack = random.randint(5,10)
    character.image = "character"

    character2.pos = (50, 0)
    character2.health = 100
    character2.attack = random.randint(5,10)
    character2.image = "character"

    for mode_key, enemy_list in enemies_by_mode.items():
        positions = {
            "mode1": [(74, 280), (150, 33), (330, 33), (427, 140), (638,140), (510, 280)],
            "mode2": [(70, 307), (145, 103), (335, 60), (400, 206), (565,275), (550, 115)]
        }
        for i, enemy in enumerate(enemy_list):
            enemy.pos = positions[mode_key][i]
            enemy.health = 100
            enemy.attack = random.randint(1,5)

    game_over = False
    last_mode = "none"
    mod = "oyunmode"

def draw():
    if mod == "menü":
        draw_main_menu()
    elif mod == "oyunmode":
        draw_mode_select()
    elif mod in ["mode1", "mode2"] or (mod == "oyunsonu" and last_mode in ["mode1", "mode2"]):
        draw_game_mode(last_mode if mod == "oyunsonu" else mod)

pgzrun.go()
