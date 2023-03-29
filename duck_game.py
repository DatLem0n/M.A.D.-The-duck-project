"""
Mildly-Annoyed™ Ducks
Author: Ville Kujala
A weird game about ducks and foxes for some reason
Written on 10.12.2022

Game uses art from my friend Oskari Honkala
"""

import os
import sys
import math
from random import randint
import pyglet
import sweeperlib


GAME_VERSION = "Beta ver_1.4"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 600
GRAVITY = 1.5

game = {
    # General information about the game state, duck coordinates etc.
    "current_level": "levelname",
    "x": 40,
    "y": 40,
    "w": 35,
    "angle": 0,
    "force": 0,
    "x_velocity": 0,
    "y_velocity": 0,
    "flight": False,
    "landed": False,
    "sling_loose": True,
    "mouse_start_x": 0,
    "mouse_start_y": 0,
    "end": 0,
    "trails": [],
    "random_gen": False,
    "first_gen": False,
    "box_drop_done": False,
    "target_drop_done": False,
    "clicked": False
}
static_ducks = []
level = {
    "boxes": [],
    "targets": []
}
def load_level(levelname):
    """Loads the level in question into a dictionary called level

    Args:
        levelname (string): name of the level to be loaded (with .txt)
    """
    temp = {}
    game["current_level"] = levelname
    levelpath = "levels\\" + levelname
    with open(os.path.join(os.getcwd(),levelpath), "r", encoding="utf-8") as leveldata:
        next(leveldata)
        for line in leveldata:
            (dict_key, data) = line.strip().split("=")
            if data.startswith("["):
                data = data.strip("[]").split(",")
                data = {data[i]: data[i + 1] for i in range(0, len(data), 2)}
                for key in data:
                    data[key] = eval(data[key])
            else:
                try:
                    data = eval(data)
                except NameError:
                    data = str(data)
            if isinstance(data,dict):
                temp[dict_key] = data
                if dict_key.startswith("box"):
                    level["boxes"].append(temp[dict_key])
                elif dict_key.startswith("target"):
                    level["targets"].append(temp[dict_key])
                else:
                    level[dict_key] = data
                    
            else:                    
                level[dict_key] = data
            

def reset_duck():
    """
    Puts the duck back into its initial state: the duck is put back into the
    launch position, its speed to zero, and its flight state to False.
    """
    if level["duck_amount"] > 0:
        game["x"] = level["sling_pos"]["x"] + 25
        game["y"] = level["sling_pos"]["y"] + 120
        game["x_velocity"] = 0
        game["y_velocity"] = 0
        game["flight"] = False
        game["landed"] = False
        game["sling_loose"] = True
        game["end"] = 0

    
def reset_game():
    """Resets the by reloading the level. In random mode, it creates a new level
    """
    if game["random_gen"]:
        if not game["first_gen"]:
            sweeperlib.clear_window()
            static_ducks.clear()
            level["boxes"].clear()
            level["targets"].clear()
        game["trails"].clear()
        game["box_drop_done"] = False
        game["target_drop_done"] = False
        target_amount = randint(2,8)
        gen_boxes = create_boxes(randint(4,20),20)
        gen_targets = create_targets(target_amount, 20)
        for box in gen_boxes:
            level["boxes"].append(box)
        for target in gen_targets:
            level["targets"].append(target)
        while not game["box_drop_done"]:
            drop(level["boxes"])
        while not game["target_drop_done"]:
            drop(level["targets"])
        level["sling_pos"] = {"x": 80, "y": randint(50, WINDOW_HEIGHT - 200)}
        level["duck_amount"] = target_amount + 1
        level["next_level"] = "random"  
        reset_duck()
        game["random_gen"] = False
        game["first_gen"] = False
        
    else:
        static_ducks.clear()
        level["boxes"].clear()
        level["targets"].clear()
        sweeperlib.clear_window()
        load_level(game["current_level"])
        game["trails"].clear()
        reset_duck()
    
def convert_to_xy(angle, ray):
    """converts a given length and angle into x and y coordinates

    Args:
        angle (float): angle in degrees
        ray (float): length of ray

    Returns:
        x, y: x and y coordinates
    """
    x = float(round(math.cos(math.radians(angle)) * ray))
    y = float(round(math.sin(math.radians(angle)) * ray))
    return x, y
    
def create_boxes(box_amount, height_min):
    """
    Creates a speficied number of boxes with random positions inside the specified
    area. Boxes are represented as dictionaries with the following keys:
    x: x coordinate of the bottom left corner
    y: y coordinate of the bottom left corner
    w: box width
    h: box height
    vy: falling velocity of the box
    """
    box_list = []
    for _ in range(box_amount):
        x = randint(150, WINDOW_WIDTH - 40)
        y = randint(height_min, WINDOW_HEIGHT)
        width = 40
        height = 40
        delta_y = 0
        generated_box = {
            "x": x,
            "y": y,
            "w": width,
            "h": height,
            "vy": delta_y
        }
        box_list.append(generated_box)
    return box_list

def create_targets(target_amount, height_min):
    """
    Creates a speficied number of targets with random positions inside the specified
    area. Targets are represented as dictionaries with the following keys:
    x: x coordinate of the bottom left corner
    y: y coordinate of the bottom left corner
    w: target width
    h: target height
    vy: falling velocity of the target
    """
    target_list = []
    for _ in range(target_amount):
        x = randint(150, WINDOW_WIDTH - 40)
        y = randint(height_min, WINDOW_HEIGHT)
        width = 40
        height = 40
        delta_y = 0
        generated_target = {
            "x": x,
            "y": y,
            "w": width,
            "h": height,
            "vy": delta_y
        }
        target_list.append(generated_target)
    return target_list

def drop(box_list):
    """
    Drops rectangular objects that are given as a list. Each object is to be
    defined as a dictionary with x and y coordinates, width, height, and falling
    velocity. Drops boxes for one time unit.
    """
    box_copy = box_list.copy() 
    if game["box_drop_done"]:
        for box in level["boxes"]:
            box_copy.append(box)
    sorted_box_list = sorted(box_copy, key=lambda box_list: box_list["y"] + box_list["w"])
    boxes_moving = 0
    for i, box in enumerate(sorted_box_list):
        left_edge = box["x"]
        right_edge = box["x"] + box["w"]
        box["vy"] -= GRAVITY
        box["y"] += box["vy"]
        boxes_moving += 1
        if box["y"] < 0:
            box["y"] = 0
            box["vy"] = 0
            boxes_moving -= 1
            continue
        for box_below in sorted_box_list[:i]:
            if box_below["x"] >= right_edge or box_below["x"] + box_below["w"] <= left_edge:
                continue
            if box["y"] <= box_below["y"] + box_below["w"]:
                box["y"] = box_below["y"] + box_below["w"]
                box["vy"] = 0
                boxes_moving -= 1
        game["box_drop_done"] = True

    if boxes_moving <= 0 and not game["box_drop_done"]:
        game["box_drop_done"] = True
    elif boxes_moving <= 0:
        game["target_drop_done"] = True
            
def launch():
    """launches the duck in to motion with the power of math
    """
    game["clicked"] = False
    game["sling_loose"] = True
    game["trails"].clear()
    game["x_velocity"] = float(math.cos(math.radians(game["angle"])) * game["force"])
    game["y_velocity"] = float(math.sin(math.radians(game["angle"])) * game["force"])
    game["flight"] = True
    level["duck_amount"] -= 1

def mouse_handler(x, y, button, modifiers):
    """Will be called when a mouse button is pressed in game window.
    
    Possible values for button: MOUSE_LEFT, MOUSE_MIDDLE, and MOUSE_RIGHT
    Possible values for modifiers: MOD_SHIFT, MOD_CTRL, MOD_ALT
    Args:
        x (float): mouse x-coordinate
        y (float): mouse y-coordinate
        button (literal): mouse button pressed
        modifiers (flag): modifier key pressed
    """
    skip_launch = False
    if game["end"] == "win" and level["next_level"] != "final" and \
level["next_level"] != "random":
        load_level(level["next_level"])
        reset_game()
        skip_launch = True
    if game["landed"] and not game["flight"] and not skip_launch:
        duck = game.copy()
        static_ducks.append(duck)
        reset_duck()
    elif not game["flight"]:
        game["angle"] = 0
        game["force"] = 0
        game["mouse_start_x"] = x
        game["mouse_start_y"] = y
        game["clicked"] = True



def drag_handler(x, y, delta_x, delta_y, button, modifiers):
    """Will be called when mouse is moved while one of its buttons is pressed
    
    Possible literals for button: MOUSE_LEFT, MOUSE_MIDDLE, and MOUSE_RIGHT
    Possible literals for modifiers: MOD_SHIFT, MOD_CTRL, MOD_ALT
    Args:
        x (float): mouse x-coordinate
        y (float): mouse y-coordinate
        dx (float): x change from last position
        dy (float): y change from last position
        button (literal): mouse button pressed
        modifiers (flag): modifier key pressed
    """
    if not game["clicked"]:
        pass
    elif not game["flight"] or game["landed"] and level["duck_amount"] != 0:
        game["sling_loose"] = False
        pull_x = game["mouse_start_x"] - x
        pull_y = game["mouse_start_y"] - y
        game["angle"] = math.degrees(math.atan2(pull_y, pull_x))
        game["force"] = math.sqrt(pull_x ** 2 + pull_y ** 2) / 2
        if game["force"] > 40:
            game["force"] = 40
        pos_x, pos_y = convert_to_xy(game["angle"], game["force"])
        game["x"] = level["sling_pos"]["x"] + 25 - pos_x * 2
        game["y"] = level["sling_pos"]["y"] + 120 - pos_y * 2
        

def keyboard_handler(symbol, modifiers):
    """Called when a key is pressed on the keyboard with game window in focus
    modified from flight_template.py to give simple keyboard controls
    Possible literals for modifiers: MOD_SHIFT, MOD_CTRL, MOD_ALT
    Args:
        symbol (constant): constant of the key being pressed e.g. A or K
        modifiers (flag): modifier key pressed
    """
    
    key = pyglet.window.key
    pos_x, pos_y = convert_to_xy(game["angle"], game["force"])
    game["x"] = level["sling_pos"]["x"] + 25 - pos_x * 2
    game["y"] = level["sling_pos"]["y"] + 120 - pos_y * 2
    if symbol == key.Q:
        sweeperlib.close()
    if symbol == key.R:
        if level["next_level"] == "random":
            game["random_gen"] = True
        reset_game()
        
    if symbol == key.RIGHT:
        game["angle"] -= 10
        if game["angle"] < 0:
            game["angle"] = 350
    elif symbol == key.LEFT:
        game["angle"] += 10
        if game["angle"] > 350:
            game["angle"] = 0

    if symbol == key.UP:
        if not game["end"]:
            game["sling_loose"] = False
            if game["force"] < 40:
                game["force"] += 5
    elif symbol == key.DOWN:
        if game["force"] >= 5:
            game["force"] -= 5
        else:
            game["force"] = 0
            game["sling_loose"] = True

    if symbol == key.SPACE:
        skip_launch = False
        if game["end"] == "win" and level["next_level"] != "final":
            load_level(level["next_level"])
            reset_game()
            skip_launch = True
        if game["landed"]:
            duck = game.copy()
            static_ducks.append(duck)
            reset_duck()
        elif not game["flight"] and not skip_launch:
            launch()

def on_release(x, y, button, modifiers):
    """Called when a mouse button is released

    Args:
        x (float): mouse x-coodrinate
        y (float): mouse y-coodrinate
        button (literal): mouse button pressed
        modifiers (flag): modifier key pressed
    """
    if not game["sling_loose"] and not game["flight"] and not game["landed"]:
        launch()   
def draw_ropes():
    """draws the rope from the sling to the duck"""
    sweeperlib.graphics["sprites"].append(pyglet.shapes.Line(game["x"],
    game["y"], level["sling_pos"]["x"],
    level["sling_pos"]["y"] + 120, 10, color=(128, 71, 28),
    batch=sweeperlib.graphics["batch"]))
    
    sweeperlib.graphics["sprites"].append(pyglet.shapes.Line(game["x"],
    game["y"], level["sling_pos"]["x"] + 80,
    level["sling_pos"]["y"] + 120, 10, color=(128, 71, 28),
    batch=sweeperlib.graphics["batch"]))  
    
def draw():
    """Draws the next frame
    """
    sweeperlib.clear_window()
    sweeperlib.draw_background()
    sweeperlib.begin_sprite_draw()
    sweeperlib.prepare_sprite("sling",level["sling_pos"]["x"],level["sling_pos"]["y"])
    sweeperlib.prepare_sprite("duck",game["x"],game["y"])
    
    for box in level["boxes"]:
        sweeperlib.prepare_sprite(" ", box["x"], box["y"])
    for target in level["targets"]:
        sweeperlib.prepare_sprite("x", target["x"], target["y"])
    for i in range(1,level["duck_amount"] + 1):
        sweeperlib.prepare_sprite("duck", 0, 20 + i * 60)
    for duck in static_ducks:
        sweeperlib.prepare_sprite("duck", duck["x"], duck["y"])
    for trail in game["trails"]:
        sweeperlib.prepare_sprite("0", trail["x"], trail["y"])
        
    if not game["sling_loose"]:
        draw_ropes()
            
    sweeperlib.draw_sprites()
    sweeperlib.draw_text(f"""angle: {round(game['angle'])}°       targets left: {
        game["targets_left"]}   \tforce: {round(
        game['force'])}""", 50, 505, size=25)
    sweeperlib.draw_text("""Q: Quit  | R: Reset |  ←/→: Set angle |\
↑/↓: Set Force  |  Space: Launch""", 10, 560, size=20)
    if game["end"] != 0:
        if game["end"] == "win":
            if level["next_level"] == "final":
                sweeperlib.draw_text("Congratulations! You have beat the game, press Q to quit",
                                        100, 400, size= 20)
            elif level["next_level"] == "random":
                sweeperlib.draw_text("You win! press R to create a new level or press Q to quit",
                                        100, 400, size= 20)
            else:
                sweeperlib.draw_text("You win! press space to load next level or Q to quit", 100,
                                    400, size= 20)
        else:
            sweeperlib.draw_text("You lost :(   press R to restart or Q to quit", 100,
                                    400, size= 20)

def update(elapsed):
    """Will be called once every frame

    Args:
        elapsed (float): actual elapsed time between frames
    """
    
    game["targets_left"] = len(level["targets"])
    
    ducks_left = level["duck_amount"]
    if game["targets_left"] == 0:
        game["end"] = "win"
    if ducks_left <= 0 and game["landed"] and not game["end"]:
        game["end"] = "lose"
    
    box_copy = level["boxes"].copy()
    for box in box_copy:
        if game["y"] > box["y"] and game["y"] < box["y"] + box["w"]:
            if game["x"] + game["w"] > box["x"] and game["x"] < box["x"] + box["w"]:
                game["flight"] = False
                game["landed"] = True
    
    target_copy = level["targets"].copy()
    for target in target_copy:
        if game["y"] > target["y"] and game["y"] < target["y"] + target["w"]:
            if game["x"] + game["w"] > target["x"] and game["x"] < target["x"] + target["w"]:
                level["targets"].remove(target)
                
    if game["y"] <= 0:
        game["y"] = 0
        game["flight"] = False
        game["landed"] = True
    if  game["flight"]:
        trail_cube = {"x": game["x"],"y": game["y"], "size": 10}
        game["trails"].append(trail_cube)
        game["x"] += game["x_velocity"]
        game["y"] += game["y_velocity"]
        game["y_velocity"] -= GRAVITY
    
    
def load_sprites(sprite_location):
    """loads sprites from given sprite location

    Args:
        sprite_location (string): location folder of sprites
    """
    sweeperlib.load_sprites(sprite_location)
    sweeperlib.load_duck(sprite_location)
    
def create_window():
    """loads sprites and creates a game window
    """
    load_sprites("sprites")
    sweeperlib.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, (115, 215, 255, 255))

def menu_input():
    """Prompts player for a selection in the menu, returns a valid selection
    Returns:
        strint: either "l", "r", or "q" depending on the player choice
    """
    while True:
        userinput = (input("Make your selection: ")).lower().strip()
        if userinput in ("levels", "random", "quit"):
            userinput = userinput[0]
        if userinput not in ("l", "r", "q"):
            print("Not a valid selection")
        else:
            return userinput
    
def level_input(level_amount):
    """Prompts player for the number of the level they wish to play

    Args:
        level_amount (int): Amount of levels currently in the game

    Returns:
        int: integer of the level the player chose
    """
    while True:
        userinput = "null"
        try:
            userinput = int(input(f"Please choose a number between 1 and {level_amount}: ")) 
        except (ValueError, TypeError):
            print("Input just the level number")
        else: 
            if userinput in range(1, level_amount + 1):
                return userinput
            print("That level does not exist... yet")
        
def levels():
    """level selection 
    """
    level_amount = len(os.listdir("levels"))
    print("Level selection:")
    print(f"There are currently {level_amount} levels in the game")
    print("What level would you like to play?")
    selection = level_input(level_amount)
    load_level("level_" + str(selection) + ".txt")
    reset_duck()
    sweeperlib.start()

def random():
    """called when random is selected, sets up random generation
    """
    game["random_gen"] = True
    game["first_gen"] = True
    reset_game()
    sweeperlib.start()
    
def menu():
    """ This is the menu for the game, asks the player what they would like to play
    """
    print(f"Welcome to Mildly-Annoyed Ducks (M.A.D.) {GAME_VERSION}")
    print("""The ducks are mildly-annoyed™ at foxes (yes, they are foxes) \
no further explanation needed""")
    print("""To start, please select gamemode. Random mode creates a randomized map 
Warning! level might be unpassable""")
    print("Your options are: Levels (L), Random (R), Quit (Q)")
    choice = menu_input()
    if choice == "l":
        levels()
    elif choice == "r":
        random()
    elif choice == "q":
        sys.exit()
        
create_window()
sweeperlib.set_draw_handler(draw)
sweeperlib.set_drag_handler(drag_handler)
sweeperlib.set_mouse_handler(mouse_handler)
sweeperlib.set_keyboard_handler(keyboard_handler)
sweeperlib.set_release_handler(on_release)
sweeperlib.set_interval_handler(update, 1/60)
menu()
