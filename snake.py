"""
Snake Game template, using classes.

Derived from:
Sample Python/Pygame Programs
Simpson College Computer Science
http://programarcadegames.com/
http://simpson.edu/computer-science/
"""

import pygame
import random

# --- Globals ---
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Screen size
game_screen_height = 600
game_screen_width = 600
hud_height = 50

# Margin between each segment
segment_margin = 3

# Set the width and height of each snake segment
segment_width = min(game_screen_height, game_screen_width) / 40 - segment_margin
segment_height = min(game_screen_height, game_screen_width) / 40 - segment_margin
total_segments_w = int(game_screen_width / (segment_width + segment_margin))
total_segments_h = int(game_screen_width / (segment_width + segment_margin))

# Set initial directions TODO maybe I could build this into the snake objects??
player_x_change = segment_width + segment_margin
player_y_change = 0

# Create obstacle designs
possible_obstacles = [
    [[-1, 0], [0, 0], [1, 0], [1, 1], [2, 1], [3, 1], [3, 2], [3, 3]],
    [[0, 0], [0, 1], [0, 2], [0, 3], [1, 3], [2, 3], [3, 3], [4, 3], [4, 2], [4, 1], [4, 0]],
    [[0, 0], [0, 1], [0, 2], [0, 3], [1, 1], [1, 2], [1, 3], [2, 2], [2, 3], [3, 3]],
    [[0, 0], [1, 1], [2, 2], [3, 3]]
]
# TODO add some way to make sure obstacles are placed not too closely OPTIONAL
# TODO make sure original snake position can't be drawn on with obstacles IMPORTANT (never happened yet)
# TODO add obstacle rotations? OPTIONAL


class Snake:
    """ Class to represent one snake. """
    def __init__(self, starting_length, is_player):
        self.snake_length = starting_length
        self.segments = []
        self.snake_pieces = pygame.sprite.Group()
        self.player = is_player
        self.x_change = segment_width + segment_margin
        self.y_change = 0
        self.create_snake()

    def create_snake(self):
        for i in range(0, self.snake_length):
            if self.player:
                x = (segment_width + segment_margin) * 30 - (segment_width + segment_margin) * i
                y = (segment_height + segment_margin) * 2
            else:
                x = (segment_width + segment_margin) * 4 - (segment_width + segment_margin) * i
                y = (segment_height + segment_margin) * 30
            segment = Segment(x, y, self.player)
            self.segments.append(segment)
            self.snake_pieces.add(segment)

    def move(self, x_change, y_change):
        global game_lost
        # Figure out where new segment will be
        x = self.segments[0].rect.x + x_change
        y = self.segments[0].rect.y + y_change

        if self.check_head_onscreen(x_change, y_change):
            # Insert new segment into the list
            segment = Segment(x, y, self.player)
            self.segments.insert(0, segment)
            self.snake_pieces.add(segment)
            # Get rid of last segment of the snake
            old_segment = self.segments.pop()
            self.snake_pieces.remove(old_segment)
        elif self.player:
            game_lost = True

    def grow(self):
        x = self.segments[-1].rect.x
        y = self.segments[-1].rect.y
        segment = Segment(x, y, self.player)
        self.segments.append(segment)
        self.snake_pieces.add(segment)

    def check_head_onscreen(self, x_change, y_change):
        x = self.segments[0].rect.x + x_change
        y = self.segments[0].rect.y + y_change
        return 0 <= x <= game_screen_width - segment_width and 0 <= y <= game_screen_height - segment_height

    def ai_movement(self):
        #  Chooses whether to continue on it's path or change direction
        if not safe_next_move() or random.randint(0, 7) == 0:  # Randomly move sometimes too
            change_enemy_direction()
        else:
            move_enemy_snake()


class Segment(pygame.sprite.Sprite):
    """ Class to represent one segment of a snake. """
    # Constructor
    def __init__(self, x, y, player):
        # Call the parent's constructor
        super().__init__()
        if player:
            segment_colour = WHITE
        else:
            segment_colour = BLUE
        # Set height, width
        self.image = pygame.Surface([segment_width, segment_height])
        self.image.fill(segment_colour)
        # Set top-left corner of the bounding rectangle to be the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Food:
    def __init__(self):
        self.food_items = pygame.sprite.Group()
        number_foods = 5
        for i in range(number_foods):
            self.create_food()

    def create_food(self):
        x = random.randint(0, total_segments_w - 1)
        y = random.randint(0, total_segments_w - 1)
        x *= (segment_width + segment_margin)
        y *= (segment_height + segment_margin)
        self.select_food(x, y)

    def select_food(self, x, y):
        choice = random.randint(1, 10)
        if choice <= 6:
            fruit = strawberry_sprite
            score = 10
        elif choice <= 9:
            fruit = banana_sprite
            score = 25
        else:
            fruit = grape_sprite
            score = 70
        new_food = FoodItem(x, y, fruit, score)
        if not self.check_food_spawn(new_food):
            self.food_items.add(new_food)
        else:
            self.create_food()

    def replenish(self, player_obtained):
        # Adds a random chance for the food to disappear and not replenish (increase difficulty overtime)
        if random.randint(1, 3) == 1 and len(self.food_items) > 2 and not player_obtained:
            return
        self.create_food()

    def check_food_spawn(self, food):
        # Returns True if the food would spawn on a snake or obstacle
        spawn_collision = False
        food_snake_coll = pygame.sprite.spritecollide(food, my_snake.segments, False)
        if food_snake_coll:
            spawn_collision = True
        food_obstacle_coll = pygame.sprite.spritecollide(food, obstacles, False)
        if food_obstacle_coll:
            spawn_collision = True
        return spawn_collision


class FoodItem(pygame.sprite.Sprite):
    def __init__(self, x, y, fruit, value):
        super().__init__()
        self.image = fruit
        # Set top-left corner of the bounding rectangle to be the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.score_value = value


class Obstacle:
    def __init__(self):
        # Randomly choose which obstacle is drawn
        random_obstacle = random.randint(0, len(possible_obstacles)-1)
        #  Choose a block number to have the origin spot from (the numbers are based on obstacle shapes for now)
        origin_block_x = random.randint(1, total_segments_w - 4)
        origin_block_y = random.randint(4, total_segments_h - 4)
        for x in possible_obstacles[random_obstacle]:
            rel_x = (origin_block_x + x[0]) * (segment_width + segment_margin)
            rel_y = (origin_block_y + x[1]) * (segment_height + segment_margin)
            new_obst_piece = ObstaclePiece(rel_x, rel_y)
            obstacles.add(new_obst_piece)


class ObstaclePiece(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([segment_width, segment_height])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Static functions here
def check_player_collisions():
    global game_lost
    # Check if the snake gets food
    food_hit_list = pygame.sprite.spritecollide(my_snake.segments[0], food_onscreen.food_items, True)
    enemy_hit_list = pygame.sprite.spritecollide(enemy_snake.segments[0], food_onscreen.food_items, True)
    scoring(enemy_hit_list, food_hit_list)

    # Check if the player collides with an obstacle, the enemy or it's own tail
    obs_hit_list = pygame.sprite.spritecollide(my_snake.segments[0], obstacles, False)
    tail_hit_list = pygame.sprite.spritecollide(my_snake.segments[0], my_snake.segments[1:], False)
    enemy_hit_list = pygame.sprite.spritecollide(my_snake.segments[0], enemy_snake.snake_pieces, False)
    if obs_hit_list or tail_hit_list or enemy_hit_list:
        game_lost = True


def scoring(enemy_hit_list, food_hit_list):
    global current_score
    for x in food_hit_list:
        current_score += x.score_value
        my_snake.grow()
        food_onscreen.replenish(True)
    for x in enemy_hit_list:
        current_score -= x.score_value
        enemy_snake.grow()
        food_onscreen.replenish(False)


def safe_next_move():
    # Checks if the enemies next move is safe or not
    if not enemy_snake.check_head_onscreen(enemy_snake.x_change, enemy_snake.y_change):
        return False
    enemy_snake.segments[0].rect.x += enemy_snake.x_change
    enemy_snake.segments[0].rect.y += enemy_snake.y_change
    obstacle_hit_list = pygame.sprite.spritecollide(enemy_snake.segments[0], obstacles, False)
    player_hit_list = pygame.sprite.spritecollide(enemy_snake.segments[0], my_snake.snake_pieces, False)
    enemy_snake.segments[0].rect.x -= enemy_snake.x_change
    enemy_snake.segments[0].rect.y -= enemy_snake.y_change
    if obstacle_hit_list or player_hit_list:
        return False
    return True


def move_enemy_snake():
    # To account for the new movement not being legal, try it again
    if safe_next_move():
        enemy_snake.move(enemy_snake.x_change, enemy_snake.y_change)
    else:
        change_enemy_direction()


def change_enemy_direction():
    # Currently the snake cannot trap himself as he can walk through his own body if required
    options = {"up": setup_direction_weighting("up"), "down": setup_direction_weighting("down"),
               "left": setup_direction_weighting("left"), "right": setup_direction_weighting("right")}
    set_best_direction(options)


def set_best_direction(options):
    # Set the best direction for the enemy ai snake
    best_direction = max(options, key=lambda key: options[key])
    if best_direction == "up":
        set_enemy_up()
    if best_direction == "down":
        set_enemy_down()
    if best_direction == "left":
        set_enemy_left()
    if best_direction == "right":
        set_enemy_right()
    if safe_next_move():
        move_enemy_snake()
    else:
        options.pop(best_direction)  # Remove the best option and leave the second best option
        set_best_direction(options)  # Recursively process the second best option


def setup_direction_weighting(direction):
    # Processes and returns the directional weighting given a direction
    if direction == "left":
        set_enemy_left()
    elif direction == "right":
        set_enemy_right()
    elif direction == "up":
        set_enemy_up()
    elif direction == "down":
        set_enemy_down()
    current_pos_x = enemy_snake.segments[0].rect.x
    current_pos_y = enemy_snake.segments[0].rect.y
    direction_weight = search_path()
    enemy_snake.segments[0].rect.x = current_pos_x
    enemy_snake.segments[0].rect.y = current_pos_y
    return direction_weight


def search_path():
    #  Path scanning ahead to calculate weighting in a certain direction
    weighted_score = 0
    weighted_multiplier = 1
    while True:  # Until the snake would hit an obstacle/go off screen
        enemy_snake.segments[0].rect.x += enemy_snake.x_change
        enemy_snake.segments[0].rect.y += enemy_snake.y_change
        if not enemy_snake.check_head_onscreen(enemy_snake.x_change, enemy_snake.y_change):
            break
        obstacle_hit_list = pygame.sprite.spritecollide(enemy_snake.segments[0], obstacles, False)
        if obstacle_hit_list:
            break
        food_hit_list = pygame.sprite.spritecollide(enemy_snake.segments[0], food_onscreen.food_items, False)
        if food_hit_list:
            weighted_multiplier += 5  # To give priority for the snake to move towards the food
        self_hit_list = pygame.sprite.spritecollide(enemy_snake.segments[0], enemy_snake.segments[1:], False)
        for x in range(len(self_hit_list)):
            weighted_score -= 5  # To try and stop the snake doubling back on itself unless absolutely necessary
        weighted_score += 1
        player_hit_list = pygame.sprite.spritecollide(enemy_snake.segments[0], my_snake.snake_pieces, False)
        if player_hit_list:
            weighted_multiplier += 3  # To give priority for the snake to move towards the player
    return weighted_multiplier * weighted_score


def set_enemy_left():
    global enemy_move
    enemy_snake.x_change = (segment_width + segment_margin) * -1
    enemy_snake.y_change = 0
    enemy_move = "left"


def set_enemy_right():
    global enemy_move
    enemy_snake.x_change = (segment_width + segment_margin)
    enemy_snake.y_change = 0
    enemy_move = "right"


def set_enemy_up():
    global enemy_move
    enemy_snake.x_change = 0
    enemy_snake.y_change = (segment_height + segment_margin) * -1
    enemy_move = "up"


def set_enemy_down():
    global enemy_move
    enemy_snake.x_change = 0
    enemy_snake.y_change = (segment_height + segment_margin)
    enemy_move = "down"


def process_input():
    global game_quit, player_x_change, player_y_change
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_quit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x_change = (segment_width + segment_margin) * -1
                player_y_change = 0
            if event.key == pygame.K_RIGHT:
                player_x_change = (segment_width + segment_margin)
                player_y_change = 0
            if event.key == pygame.K_UP:
                player_x_change = 0
                player_y_change = (segment_height + segment_margin) * -1
            if event.key == pygame.K_DOWN:
                player_x_change = 0
                player_y_change = (segment_height + segment_margin)


def game_play_drawing():
    screen.fill(BLACK)
    my_snake.snake_pieces.draw(screen)
    enemy_snake.snake_pieces.draw(screen)
    food_onscreen.food_items.draw(screen)
    obstacles.draw(screen)
    draw_score()
    if game_lost:
        game_over_text = game_over_font.render("Game Over", True, WHITE, BLACK)
        text_rect = game_over_text.get_rect()
        text_x = screen.get_width() / 2 - text_rect.width / 2
        text_y = screen.get_height() / 2 - text_rect.height / 2
        screen.blit(game_over_text, [text_x, text_y])
    pygame.display.flip()


def draw_score():
    score_text = score_font.render("Score: " + str(current_score), True, WHITE)
    score_text_rect = score_text.get_rect()
    score_text_rect.center = (150, 630)
    pygame.draw.line(screen, WHITE, (0, game_screen_height), (game_screen_width, game_screen_height), 1)
    screen.blit(score_text, score_text_rect)


# Call this function so the Pygame library can initialize itself
pygame.init()

# Create a 600x600 sized screen
screen = pygame.display.set_mode([game_screen_width, game_screen_height + hud_height])

# Set the title of the window
pygame.display.set_caption('Snake Game')

# Image loading
strawberry_sprite = pygame.image.load('strawberry.png').convert().convert_alpha()
banana_sprite = pygame.image.load('banana.png').convert().convert_alpha()
grape_sprite = pygame.image.load('grapes.png').convert().convert_alpha()
strawberry_sprite = pygame.transform.scale(strawberry_sprite, (12, 12))
banana_sprite = pygame.transform.scale(banana_sprite, (12, 12))
grape_sprite = pygame.transform.scale(grape_sprite, (12, 12))

# Fonts
game_over_font = pygame.font.Font(None, 72)
score_font = pygame.font.SysFont("Courier", 48)

# Create an initial snake
player_init_size = 3
my_snake = Snake(player_init_size, True)

# Add an AI snake
enemy_init_size = 8
enemy_snake = Snake(enemy_init_size, False)
enemy_move = "right"

# Build list of initial food spots and obstacles
obstacles = pygame.sprite.Group()
number_of_obstacles = random.randint(4, 7)
for obs in range(number_of_obstacles):
    Obstacle()
food_onscreen = Food()

# Game variables and setup
clock = pygame.time.Clock()
game_quit = False
game_lost = False
current_score = 0

while not game_quit:
    # Game loop
    process_input()
    if not game_lost:
        my_snake.move(player_x_change, player_y_change)
        enemy_snake.ai_movement()
        check_player_collisions()
    game_play_drawing()
    clock.tick(10)

pygame.quit()
