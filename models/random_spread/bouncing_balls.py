"""
Bounce balls on the screen.
Spawn a new ball for each mouse-click.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.bouncing_balls
"""

import arcade
import random

# --- Set up the constants

# Size of the screen
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
# Size of popultion window
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
SCREEN_TITLE = "Bouncing Balls Example"

from enum import Enum

class Status(Enum):
    VULNERABLE = 0
    INFECTIOUS = 1
    IMMUNE = 2

class Ball:
    """
    Class to keep track of a ball's location and vector.
    """
    def __init__(self):
        self.id = -1
        self.status = Status.VULNERABLE
        self.hit = False
        self.x = 0
        self.y = 0
        self.change_x = 0
        self.change_y = 0
        self.size = 0
        self.color = None

    def infect(self):
        if self.status == Status.VULNERABLE:
            self.status = Status.INFECTIOUS
            self.infectious = 130
            self.color = (random.randrange(128,256),0,0)

    def immune(self):
        self.status = Status.IMMUNE
        self.color = (0,random.randrange(128,256),0)


def make_ball(id):
    """
    Function to make a new, random ball.
    """
    ball = Ball()

    ball.id = id

    # Size of the ball
    # ball.size = random.randrange(10, 30)
    ball.size = 10

    # Starting position of the ball.
    # Take into account the ball size so we don't spawn on the edge.
    ball.x = random.randrange(ball.size, WINDOW_WIDTH - ball.size)
    ball.y = random.randrange(ball.size, WINDOW_HEIGHT - ball.size)

    # Speed and direction of rectangle
    #ball.change_x = random.randrange(-2, 3)
    #ball.change_y = random.randrange(-2, 3)

    ball.change_x = random.choice([-2, -0.5, 0.5, 2])
    ball.change_y = random.choice([-2, -0.5, 0.5, 2])

    # Color
    ball.color = (0, 0, random.randrange(128,256))

    return ball


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.ball_list = []
        self.totals = []
        ball = make_ball(0)
        ball.infect()
        self.ball_list.append(ball)
        for i in range(1,100):
            ball = make_ball(i)
            self.ball_list.append(ball)
        self.blue_points = [(5+WINDOW_WIDTH,WINDOW_HEIGHT),(5+WINDOW_WIDTH,WINDOW_HEIGHT)]
        self.red_points = [(5+WINDOW_WIDTH,0),(5+WINDOW_WIDTH,0)]
        
    def on_draw(self):
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        arcade.start_render()

        for ball in self.ball_list:
            arcade.draw_circle_filled(ball.x, ball.y, ball.size, ball.color)

        


        self.red_line_strip.draw()
        self.blue_line_strip.draw()

        # Put the text on the screen.
        output = "Balls: {}".format(len(self.ball_list))
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)


    def on_update(self, delta_time):
        """ Movement and game logic """
        # Reset collision data        
        total = 0
        for ball in self.ball_list:
            ball.hit = False
            if ball.status != Status.VULNERABLE:
                total += 1
        self.totals.append(total)
        n = len(self.totals)
        self.red_points.append((5+WINDOW_WIDTH + n*0.4, (total*6)))
        self.blue_points.append((5+WINDOW_WIDTH + n*0.4, ((100-total)*6)))


        self.red_line_strip = arcade.create_line_strip(self.red_points, arcade.color.RED, 2)
        self.blue_line_strip = arcade.create_line_strip(self.blue_points, arcade.color.BLUE, 2)

        for ball in self.ball_list:
            ball.x += ball.change_x
            ball.y += ball.change_y
            if ball.status == Status.INFECTIOUS:
                ball.infectious -= 1
                if ball.infectious == 0:
                    ball.immune()

            # Collision with walls
            if ball.x < ball.size:
                ball.change_x *= -1

            if ball.y < ball.size:
                ball.change_y *= -1

            if ball.x > WINDOW_WIDTH - ball.size:
                ball.change_x *= -1

            if ball.y > WINDOW_HEIGHT - ball.size:
                ball.change_y *= -1

            # Collision with another ball
            for other in self.ball_list:
                if other.id == ball.id:
                    continue
                if other.hit:
                    continue
                if (-ball.size < (ball.x - other.x) < ball.size) and (-ball.size < (ball.y - other.y) < ball.size):
                    (ball.change_x,other.change_x) = (other.change_x,ball.change_x)
                    (ball.change_y,other.change_y) = (other.change_y,ball.change_y)
                    other.hit = True
                    if ball.status == Status.INFECTIOUS:
                        other.infect()
                    if other.status == Status.INFECTIOUS:
                        ball.infect()
                    ball.hit = True
                    break




    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called whenever the mouse button is clicked.
        """
        ball = make_ball(100)
        ball.infect()
        self.ball_list.append(ball)


def main():
    MyGame()
    arcade.run()


if __name__ == "__main__":
    main()