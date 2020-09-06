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

# Screen size
game_screen_height = 600
game_screen_width = 600
screen_height = 650
screen_width = 600

# Margin between each segment
segment_margin = 3

# Set the width and height of each snake segment
segment_width = min(game_screen_height, game_screen_width) / 40 - segment_margin
segment_height = min(game_screen_height, game_screen_width) / 40 - segment_margin
total_segments_w = int(game_screen_width / (segment_width + segment_margin))
total_segments_h = int(game_screen_width / (segment_width + segment_margin))

# Set initial speed
x_change = segment_width + segment_margin
y_change = 0

# Somewhere here, determine some random obstacles
possible_obstacles = [
    [[-1, 0], [0, 0], [1, 0], [1, 1], [2, 1], [3, 1], [3, 2], [3, 3]],
    [[0, 0], [0, 1], [0, 2], [0, 3], [1, 3], [2, 3], [3, 3], [4, 3], [4, 2], [4, 1], [4, 0]],
    [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [1, 1], [1, 2], [1, 3], [1, 4], [2, 2], [2, 3], [2, 4], [3, 3], [3, 4], [4, 4]],
    [[0, 0], [1, 1], [2, 2], [3, 3]]
]
number_of_obstacles = random.randint(4, 7)
# TODO add some way to make sure obstacles are placed not too closely
# TODO make sure original snake position can't be drawn on with obstacles


class Snake:
    """ Class to represent one snake. """
    def __init__(self, starting_length):
        self.snake_length = starting_length
        self.segments = []
        self.snake_pieces = pygame.sprite.Group()

        for i in range(0, self.snake_length):
            x = (segment_width + segment_margin) * 30 - (segment_width + segment_margin) * i
            y = (segment_height + segment_margin) * 2
            segment = Segment(x, y)
            self.segments.append(segment)
            self.snake_pieces.add(segment)

    def move(self):
        global game_lost
        # Figure out where new segment will be
        x = self.segments[0].rect.x + x_change
        y = self.segments[0].rect.y + y_change
        # Don't move off the screen
        # At the moment a potential move off the screen means nothing happens, but it should end the game
        if check_snake_head_onscreen(x, y):
            # Insert new segment into the list
            segment = Segment(x, y)
            self.segments.insert(0, segment)
            self.snake_pieces.add(segment)
        # Get rid of last segment of the snake
        # .pop() command removes last item in list
            old_segment = self.segments.pop()
            self.snake_pieces.remove(old_segment)
        else:  # else if not ai_snake TODO
            game_lost = True

    def grow(self):
        x = self.segments[-1].rect.x
        y = self.segments[-1].rect.y
        segment = Segment(x, y)
        self.segments.append(segment)
        self.snake_pieces.add(segment)


class Segment(pygame.sprite.Sprite):
    """ Class to represent one segment of a snake. """
    # Constructor
    def __init__(self, x, y):
        # Call the parent's constructor
        super().__init__()

        # Set height, width
        self.image = pygame.Surface([segment_width, segment_height])
        self.image.fill(WHITE)
        # Set top-left corner of the bounding rectangle to be the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Food:
    def __init__(self):
        self.food_list = []
        self.food_items = pygame.sprite.Group()
        number_foods = 5
        for i in range(number_foods):
            self.create_food()

    def create_food(self):
        x = random.randint(0, total_segments_w - 1)
        y = random.randint(0, total_segments_w - 1)
        x *= (segment_width + segment_margin)
        y *= (segment_height + segment_margin)
        # To add a check that ensures it doesn't spawn on the snakes
        new_food = FoodItem(x, y)
        if not check_food_spawn(new_food):
            self.food_list.append(new_food)
            self.food_items.add(new_food)
        else:
            self.create_food()

    def replenish(self):
        self.create_food()
        # can add complication here later if I want


class FoodItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Set height, width
        self.image = pygame.Surface([segment_width, segment_height])
        self.image.fill(RED)

        # Set top-left corner of the bounding rectangle to be the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


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
def check_food_spawn(food):
    # Checks if the food spawns on a snake or obstacle
    spawn_collision = False
    food_snake_coll = pygame.sprite.spritecollide(food, my_snake.segments, False)
    if food_snake_coll:
        spawn_collision = True
    food_obstacle_coll = pygame.sprite.spritecollide(food, obstacles, False)
    if food_obstacle_coll:
        spawn_collision = True
    return spawn_collision


def check_snake_collisions():
    global game_lost
    # Check if the snake gets food
    food_hit_list = pygame.sprite.spritecollide(my_snake.segments[0], food_onscreen.food_items, True)
    for x in range(len(food_hit_list)):
        my_snake.grow()
        food_onscreen.replenish()
    # Check if the snake collides with an obstacle or it's own tail
    obs_hit_list = pygame.sprite.spritecollide(my_snake.segments[0], obstacles, False)
    tail_hit_list = pygame.sprite.spritecollide(my_snake.segments[0], my_snake.segments[1:], False)
    if obs_hit_list or tail_hit_list:
        game_lost = True


def check_snake_head_onscreen(head_x, head_y):
    return 0 <= head_x <= game_screen_width - segment_width and 0 <= head_y <= game_screen_height - segment_height


def process_input():
    global game_quit, x_change, y_change
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_quit = True
        # Set the direction based on the key pressed
        # We want the speed to be enough that we move a full
        # segment, plus the margin.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                x_change = (segment_width + segment_margin) * -1
                y_change = 0
            if event.key == pygame.K_RIGHT:
                x_change = (segment_width + segment_margin)
                y_change = 0
            if event.key == pygame.K_UP:
                x_change = 0
                y_change = (segment_height + segment_margin) * -1
            if event.key == pygame.K_DOWN:
                x_change = 0
                y_change = (segment_height + segment_margin)


def game_play_drawing():
    screen.fill(BLACK)
    my_snake.snake_pieces.draw(screen)
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
    pygame.draw.line(screen, WHITE, (0, game_screen_height), (screen_width, game_screen_height), 1)
    screen.blit(score_text, score_text_rect)


# Call this function so the Pygame library can initialize itself
pygame.init()

# Create a 600x600 sized screen
screen = pygame.display.set_mode([screen_width, screen_height])

# Set the title of the window
pygame.display.set_caption('Snake Game')

# Create an initial snake
snake_starting_size = 3
my_snake = Snake(snake_starting_size)

# Build list of initial food spots and obstacles
obstacles = pygame.sprite.Group()
for obs in range(number_of_obstacles):
    Obstacle()
food_onscreen = Food()

# Game variables and setup
clock = pygame.time.Clock()
game_quit = False
game_lost = False
game_over_font = pygame.font.Font(None, 72)
score_font = pygame.font.SysFont("Courier", 48)
current_score = 0

while not game_quit:
    # Game loop
    process_input()
    if not game_lost:
        my_snake.move()
        check_snake_collisions()
    game_play_drawing()
    clock.tick(10)

pygame.quit()
