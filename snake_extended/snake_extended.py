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

# Create obstacle designs
possible_obstacles = [
    [[-1, 0], [0, 0], [1, 0], [1, 1], [2, 1], [3, 1], [3, 2], [3, 3]],
    [[0, 0], [0, 1], [0, 2], [0, 3], [1, 3], [2, 3], [3, 3], [4, 3], [4, 2], [4, 1], [4, 0]],
    [[0, 0], [0, 1], [0, 2], [0, 3], [1, 1], [1, 2], [1, 3], [2, 2], [2, 3], [3, 3]],
    [[0, 0], [1, 1], [2, 2], [3, 3]],
    [[3, 0], [2, 1], [1, 2], [0, 3]]
]

# Set snake sizes
player_init_size = 3
enemy_init_size = 7


class Snake:
    """ Class to represent one snake. """
    def __init__(self, starting_length, is_player):
        self.snake_length = starting_length
        self.segments = []
        self.snake_pieces = pygame.sprite.Group()
        self.player = is_player
        self.create_snake()

        #  Set the initial direction and block movement
        self.x_change = segment_width + segment_margin
        self.y_change = 0

    def create_snake(self):
        for i in range(0, self.snake_length):
            if self.player:
                x = (segment_width + segment_margin) * 15 - (segment_width + segment_margin) * i
                y = (segment_height + segment_margin) * 2
            else:
                x = (segment_width + segment_margin) * 4 - (segment_width + segment_margin) * i
                y = (segment_height + segment_margin) * 30
            segment = Segment(x, y, self.player)
            self.segments.append(segment)
            self.snake_pieces.add(segment)

    def move(self, x_change, y_change):
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
            game.game_lost = True

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
        if random.randint(0, 7) == 0:  # Randomly move sometimes too
            change_enemy_direction()
        elif not safe_next_move():
            change_enemy_direction()
        else:
            self.move(self.x_change, self.y_change)


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
    def __init__(self, game_obj):
        self.food_items = pygame.sprite.Group()
        number_foods = 5
        for i in range(number_foods):
            self.create_food(game_obj)

    def create_food(self, game_obj):
        x = random.randint(0, total_segments_w - 1)
        y = random.randint(0, total_segments_w - 1)
        x *= (segment_width + segment_margin)
        y *= (segment_height + segment_margin)
        self.select_food(x, y, game_obj)

    def select_food(self, x, y, game_obj):
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
        if not check_food_spawn(new_food, game_obj):
            self.food_items.add(new_food)
        else:
            self.create_food(game_obj)

    def replenish(self, player_obtained, game_obj):
        # Adds a random chance for the food to disappear and not replenish (increase difficulty overtime)
        if random.randint(1, 3) == 1 and len(self.food_items) > 2 and not player_obtained:
            return
        self.create_food(game_obj)


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
    def __init__(self, obstacles):
        # Randomly choose which obstacle is drawn
        random_obstacle = random.randint(0, len(possible_obstacles)-1)
        #  Choose a block number to have the origin spot from (the numbers are based on obstacle shapes for now)
        origin_block_x = random.randint(2, total_segments_w - 4)
        origin_block_y = random.randint(3, total_segments_h - 4)
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


class Game:
    def __init__(self):
        self.enemy_snake = Snake(enemy_init_size, False)
        self.my_snake = Snake(player_init_size, True)
        self.enemy_move = "right"
        self.obstacles = pygame.sprite.Group()
        number_of_obstacles = random.randint(5, 10)
        for obs in range(number_of_obstacles):
            Obstacle(self.obstacles)
        self.food_onscreen = Food(self)
        self.score_text = None
        self.game_lost = False
        self.current_score = 0
        self.reset_game = False

    def game_play_drawing(self):
        if game_quit:
            return
        screen.fill(BLACK)
        self.my_snake.snake_pieces.draw(screen)
        self.enemy_snake.snake_pieces.draw(screen)
        self.food_onscreen.food_items.draw(screen)
        self.obstacles.draw(screen)
        self.draw_score()
        if self.game_lost:
            game_over_text = game_over_font.render("Game Over", True, WHITE, BLACK)
            text_rect = game_over_text.get_rect()
            text_x = screen.get_width() / 2 - text_rect.width / 2
            text_y = screen.get_height() / 5 - text_rect.height / 2
            screen.blit(game_over_text, [text_x, text_y])
            play_again_text = name_font.render("Press enter to play again!", True, WHITE, BLACK)
            play_rect = play_again_text.get_rect()
            text_x = screen.get_width() / 2 - play_rect.width / 2
            screen.blit(play_again_text, [text_x, text_y+50])
            # Draw high-scores over top of the high score screen
        pygame.display.flip()

    def draw_score(self):
        self.score_text = score_font.render("Score: " + str(self.current_score), True, WHITE)
        score_text_rect = self.score_text.get_rect()
        score_text_rect.center = (150, 630)
        pygame.draw.line(screen, WHITE, (0, game_screen_height), (game_screen_width, game_screen_height), 1)
        screen.blit(self.score_text, score_text_rect)

    def scoring(self, enemy_hit_list, food_hit_list):
        for x in food_hit_list:
            self.current_score += x.score_value
            self.my_snake.grow()
            self.food_onscreen.replenish(True, self)
        for x in enemy_hit_list:
            self.current_score -= x.score_value
            self.enemy_snake.grow()
            self.food_onscreen.replenish(False, self)

    def name_drawing(self):
        global name_entered
        process_input()
        if game_quit:
            name_entered = True
            return
        screen.fill(BLACK)
        enter_name_text = name_font.render("Enter your name: " + player_name, True, WHITE, BLACK)
        next_line_text = name_font.render("And press enter to play.", True, WHITE, BLACK)
        name_rect = enter_name_text.get_rect()
        next_line_rect = next_line_text.get_rect()
        text_x = screen.get_width() / 2 - name_rect.width / 2
        text_y = screen.get_height() / 2 - name_rect.height / 2
        next_x = screen.get_width() / 2 - next_line_rect.width / 2
        screen.blit(enter_name_text, [text_x, text_y])
        screen.blit(next_line_text, [next_x, text_y + 30])
        pygame.display.flip()


# Static functions here
def play_again():
    global game
    while not game.reset_game:
        process_input()
        if game_quit:
            return
    game = Game()


def check_food_spawn(food, game_objects):
    # Returns True if the food would spawn on a snake or obstacle
    spawn_collision = False
    food_player_coll = pygame.sprite.spritecollide(food, game_objects.my_snake.segments, False)
    food_enemy_coll = pygame.sprite.spritecollide(food, game_objects.enemy_snake.segments, False)
    if food_player_coll or food_enemy_coll:
        spawn_collision = True
    food_obstacle_coll = pygame.sprite.spritecollide(food, game_objects.obstacles, False)
    if food_obstacle_coll:
        spawn_collision = True
    return spawn_collision


def check_player_collisions():
    # Check if the snake gets food
    food_hit_list = pygame.sprite.spritecollide(game.my_snake.segments[0], game.food_onscreen.food_items, True)
    enemy_hit_list = pygame.sprite.spritecollide(game.enemy_snake.segments[0], game.food_onscreen.food_items, True)
    game.scoring(enemy_hit_list, food_hit_list)

    # Check if the player collides with an obstacle, the enemy or it's own tail
    obs_hit_list = pygame.sprite.spritecollide(game.my_snake.segments[0], game.obstacles, False)
    tail_hit_list = pygame.sprite.spritecollide(game.my_snake.segments[0], game.my_snake.segments[1:], False)
    enemy_hit_list = pygame.sprite.spritecollide(game.my_snake.segments[0], game.enemy_snake.snake_pieces, False)
    if obs_hit_list or tail_hit_list or enemy_hit_list:
        game.game_lost = True


def safe_next_move():
    # Checks if the enemies next move is safe or not
    if not game.enemy_snake.check_head_onscreen(game.enemy_snake.x_change, game.enemy_snake.y_change):
        return False
    game.enemy_snake.segments[0].rect.x += game.enemy_snake.x_change
    game.enemy_snake.segments[0].rect.y += game.enemy_snake.y_change
    obstacle_hit_list = pygame.sprite.spritecollide(game.enemy_snake.segments[0], game.obstacles, False)
    player_hit_list = pygame.sprite.spritecollide(game.enemy_snake.segments[0], game.my_snake.snake_pieces, False)
    game.enemy_snake.segments[0].rect.x -= game.enemy_snake.x_change
    game.enemy_snake.segments[0].rect.y -= game.enemy_snake.y_change
    if obstacle_hit_list or player_hit_list:
        return False
    return True


def change_enemy_direction():
    # Currently the snake cannot trap himself as he can walk through his own body if required
    options = {"up": direction_weighting("up"), "down": direction_weighting("down"),
               "left": direction_weighting("left"), "right": direction_weighting("right")}
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
        game.enemy_snake.move(game.enemy_snake.x_change, game.enemy_snake.y_change)
    else:
        options.pop(best_direction)  # Remove the best option and leave the second best option
        set_best_direction(options)  # Recursively process the second best option


def direction_weighting(direction):
    # Processes and returns the directional weighting given a direction
    if direction == "left":
        set_enemy_left()
    elif direction == "right":
        set_enemy_right()
    elif direction == "up":
        set_enemy_up()
    elif direction == "down":
        set_enemy_down()
    current_pos_x = game.enemy_snake.segments[0].rect.x
    current_pos_y = game.enemy_snake.segments[0].rect.y
    direction_weight = search_path()
    game.enemy_snake.segments[0].rect.x = current_pos_x
    game.enemy_snake.segments[0].rect.y = current_pos_y
    return direction_weight


def search_path():
    #  Path scanning ahead to calculate weighting in a certain direction
    weighted_score = 0
    weighted_multiplier = 1
    while True:  # Until the snake would hit an obstacle/go off screen
        game.enemy_snake.segments[0].rect.x += game.enemy_snake.x_change
        game.enemy_snake.segments[0].rect.y += game.enemy_snake.y_change
        if not game.enemy_snake.check_head_onscreen(game.enemy_snake.x_change, game.enemy_snake.y_change):
            break
        obstacle_hit_list = pygame.sprite.spritecollide(game.enemy_snake.segments[0], game.obstacles, False)
        if obstacle_hit_list:
            break
        food_hit_list = pygame.sprite.spritecollide(game.enemy_snake.segments[0], game.food_onscreen.food_items, False)
        if food_hit_list:
            weighted_multiplier += 5  # To give priority for the snake to move towards the food
        self_hit_list = pygame.sprite.spritecollide(game.enemy_snake.segments[0], game.enemy_snake.segments[1:], False)
        for x in range(len(self_hit_list)):
            weighted_score -= 5  # To try and stop the snake doubling back on itself unless absolutely necessary
        weighted_score += 1
        player_hit_list = pygame.sprite.spritecollide(game.enemy_snake.segments[0], game.my_snake.snake_pieces, False)
        if player_hit_list:
            weighted_multiplier += 3  # To give priority for the snake to move towards the player
    return weighted_multiplier * weighted_score


def set_enemy_left():
    game.enemy_snake.x_change = (segment_width + segment_margin) * -1
    game.enemy_snake.y_change = 0
    game.enemy_move = "left"


def set_enemy_right():
    game.enemy_snake.x_change = (segment_width + segment_margin)
    game.enemy_snake.y_change = 0
    game.enemy_move = "right"


def set_enemy_up():
    game.enemy_snake.x_change = 0
    game.enemy_snake.y_change = (segment_height + segment_margin) * -1
    game.enemy_move = "up"


def set_enemy_down():
    game.enemy_snake.x_change = 0
    game.enemy_snake.y_change = (segment_height + segment_margin)
    game.enemy_move = "down"


def process_input():
    global game_quit, name_entered, player_name
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_quit = True
        if event.type == pygame.KEYDOWN:
            if game.game_lost and event.key == pygame.K_RETURN:
                game.reset_game = True
            elif event.key == pygame.K_LEFT:
                game.my_snake.x_change = (segment_width + segment_margin) * -1
                game.my_snake.y_change = 0
            elif event.key == pygame.K_RIGHT:
                game.my_snake.x_change = (segment_width + segment_margin)
                game.my_snake.y_change = 0
            elif event.key == pygame.K_UP:
                game.my_snake.x_change = 0
                game.my_snake.y_change = (segment_height + segment_margin) * -1
            elif event.key == pygame.K_DOWN:
                game.my_snake.x_change = 0
                game.my_snake.y_change = (segment_height + segment_margin)
            elif not name_entered:
                if event.unicode.isalpha():
                    player_name += event.unicode
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_SPACE:
                    player_name += " "
                elif event.key == pygame.K_RETURN:
                    name_entered = True


# Call this function so the Pygame library can initialize itself
pygame.init()

# Create a 600x600 sized screen
screen = pygame.display.set_mode([game_screen_width, game_screen_height + hud_height])

# Set the title of the window
pygame.display.set_caption('Snake Game')

# Image loading
strawberry_sprite = pygame.image.load('strawberry.png').convert_alpha()
banana_sprite = pygame.image.load('banana.png').convert_alpha()
grape_sprite = pygame.image.load('grapes.png').convert_alpha()
strawberry_sprite = pygame.transform.scale(strawberry_sprite, (12, 12))
banana_sprite = pygame.transform.scale(banana_sprite, (12, 12))
grape_sprite = pygame.transform.scale(grape_sprite, (12, 12))

# Fonts
game_over_font = pygame.font.Font(None, 72)
score_font = pygame.font.SysFont("Courier", 48)
name_font = pygame.font.SysFont("Courier", 24)

# Build list of initial food spots and obstacles
game = Game()

# Game variables and setup
clock = pygame.time.Clock()
game_quit = False
player_name = ""
name_entered = False

while not game_quit:
    # Game loop
    process_input()
    while not name_entered:
        game.name_drawing()

    if not game.game_lost:
        game.my_snake.move(game.my_snake.x_change, game.my_snake.y_change)
        game.enemy_snake.ai_movement()
        check_player_collisions()
    else:
        play_again()

    game.game_play_drawing()
    clock.tick(12)

pygame.quit()
