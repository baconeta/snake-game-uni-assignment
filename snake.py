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
height = 600
width = 600

# Margin between each segment
segment_margin = 3

# Set the width and height of each snake segment
segment_width = min(height, width) / 40 - segment_margin
segment_height = min(height, width) / 40 - segment_margin
total_segments = int(width / (segment_width+segment_margin))


# Set initial speed
x_change = segment_width + segment_margin
y_change = 0


class Snake:
    """ Class to represent one snake. """

    # Constructor
    def __init__(self, starting_length):
        self.snake_length = starting_length
        self.segments = []
        self.sprites_list = pygame.sprite.Group()
        self.end_snake = None

        for i in range(0, self.snake_length):
            x = (segment_width + segment_margin) * 30 - (segment_width + segment_margin) * i
            y = (segment_height + segment_margin) * 2
            segment = Segment(x, y)
            self.segments.append(segment)
            self.sprites_list.add(segment)
            self.end_snake = segment

    def move(self):
        # Figure out where new segment will be
        x = self.segments[0].rect.x + x_change
        y = self.segments[0].rect.y + y_change
        # Don't move off the screen
        # At the moment a potential move off the screen means nothing happens, but it should end the game
        if check_snake_head_onscreen(x, y):
            # Insert new segment into the list
            segment = Segment(x, y)
            self.segments.insert(0, segment)
            self.sprites_list.add(segment)
        # Get rid of last segment of the snake
        # .pop() command removes last item in list
            old_segment = self.segments.pop()
            self.sprites_list.remove(old_segment)
        else:
            print("game would end here but now nothing happens")
            # game_end() function to run

    def grow(self):
        x = self.end_snake.rect.x
        y = self.end_snake.rect.y
        segment = Segment(x, y)
        self.segments.append(segment)
        self.sprites_list.add(segment)


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
        self.image = pygame.Surface([segment_width, segment_height])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.food_list = []
        self.food_items = pygame.sprite.Group()
        number_foods = 5
        for i in range(number_foods):
            self.create_food()

    def create_food(self):
        x = random.randint(1, total_segments)
        y = random.randint(1, total_segments)
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


# Static functions here
def check_food_spawn(food):
    # Checks if the food spawns on a snake
    food_spawn_collision = pygame.sprite.spritecollide(food, my_snake.segments, False)
    if not food_spawn_collision:
        return False
    else:
        print("there was a food spawn collision")
        return True


def check_snake_collisions():
    hit_list = pygame.sprite.spritecollide(my_snake.segments[0], food_onscreen.food_items, True)
    for x in range(len(hit_list)):
        my_snake.grow()
        food_onscreen.replenish()


def check_snake_head_onscreen(head_x, head_y):
    return 0 <= head_x <= width - segment_width and 0 <= head_y <= height - segment_height


def process_input():
    global game_done, x_change, y_change
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_done = True
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


def game_screen_drawing():
    screen.fill(BLACK)
    my_snake.sprites_list.draw(screen)
    food_onscreen.food_items.draw(screen)
    pygame.display.flip()


# Call this function so the Pygame library can initialize itself
pygame.init()

# Create a 600x600 sized screen
screen = pygame.display.set_mode([width, height])

# Set the title of the window
pygame.display.set_caption('Snake Game')

# Create an initial snake
my_snake = Snake(3)

# Build list of initial food spots
food_onscreen = Food()

clock = pygame.time.Clock()
game_done = False

while not game_done:
    # Game loop
    process_input()
    check_snake_collisions()
    my_snake.move()
    game_screen_drawing()
    clock.tick(10)

pygame.quit()
