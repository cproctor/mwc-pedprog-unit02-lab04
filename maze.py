from quest.game import QuestGame
from quest.map import Map, GridMapLayer
from quest.maze import Maze
from quest.sprite import Wall, NPC
from quest.helpers import resolve_resource_path
from itertools import product
import arcade
import random
from datetime import datetime
import os
from pathlib import Path

class MazeGame(QuestGame):
    """Get all the stars as fast as you can! My record is 45 seconds.

    MazeGame is an example of how you can make a fairly complex 
    game without making too many changes. Because MazeGame is a 
    subclass of QuestGame, we just need to change the parts we 
    want to work differently. We need to set some of the MazeGame 
    properties and override a few of the class methods. 

    Attributes:
        tile_size=32: Each square tile in the map is 32 pixels across.
        grid_columns=33: The map will have 33 columns of tiles.
        grid_rows=33: The map will have 33 rows of tiles.
        player_sprite_image="images/boy_simple.png": The sprite's image file.
        player_scaling=0.5: The image is too big, so we scale it down. (We could
            also just resize the image itself.)
        player_initial_x=1.5 * tile_size: By starting the player at 1.5 times `tile_size`, 
            the player will initially be positioned at the center of tile (1, 1).
            The outer edge of the map is walls.
        player_initial_y=1.5 * tile_size: Again, centering the player at (1, 1)
        score=0: Keeps track of how much loot has been collected.
        max_score=25: Total amount of loot to be distributed through the maze.
        game_over=False: Keeps track of whether the game has ended.
    """
    tile_size = 32
    grid_columns = 33
    grid_rows = 33
    player_sprite_image = "assets/sprites/boy.png"
    player_scaling = 0.5
    player_speed = 5
    player_initial_x = 1.5 * tile_size
    player_initial_y = 1.5 * tile_size
    score = 0
    max_score = 25
    game_over = False

    def __init__(self):
        super().__init__()
        self.level_start = datetime.now()

    def setup_maps(self):
        """Creates a MazeMap (see below) and adds it to game's list of maps.
        """
        super().setup_maps()
        maze_map = MazeMap(self.grid_columns, self.grid_rows, self.tile_size, self.max_score)
        self.add_map(maze_map)

    def setup_walls(self):
        """Assigns self.wall_list to be all the sprites in the map's "walls" layer.
        """
        self.wall_list = self.get_current_map().get_layer_by_name("walls").sprite_list

    def setup_npcs(self):
        """Assigns self.npc_list to be all the sprites in the map's "loot" layer.
        """
        self.npc_list = self.get_current_map().get_layer_by_name("loot").sprite_list

    def on_loot_collected(self, collector):
        """A method to be called whenever loot is collected.
        See the Loot NPC sprite below. It calls this method whenever there is
        a collision with the player.
        """
        self.score += 1
        if self.score == self.max_score:
            self.game_over = True
            self.final_elapsed_time = (datetime.now() - self.level_start).seconds

    def message(self):
        """Returns a string like "Time 12 (12/25)"
        """
        if self.game_over:
            return "You won in {} seconds!".format(self.final_elapsed_time)
        else:
            elapsed_time = datetime.now() - self.level_start
            return "Time {} ({}/{})".format(elapsed_time.seconds, self.score, self.max_score)

class Loot(NPC):
    """Loot is a NPC which shows up in the game as a star. Its only job is to
    get collected by the player.
    """
    def on_collision(self, sprite, game):
        """When the player collides with a Loot, it calls quest.maze.MazeGame.on_loot_collected to tell
        the game to make needed updates. Then the Loot removes itself.
        """
        game.on_loot_collected(sprite)
        print("Got a star!")
        self.kill()

class MazeMap(Map):
    """A Map which creates a wall layer using a Maze.

    MazeMap is a subclass of Map which automatically generates a 
    maze. It uses a Maze to figure out where to put walls, 
    and adds wall sprites to a map layer in a corresponding pattern.
    Args:
        columns: The number of columns of tiles in the map
        rows: The number of rows of tiles in the map
        tile_size: The size (in pixels) of each square tile
        num_loot: The number of loot sprites to add to the map
        
    """
    def __init__(self, columns, rows, tile_size, num_loot):
        super().__init__()
        self.columns = columns
        self.rows = rows
        self.tile_size = tile_size
        self.num_loot = num_loot
        self.maze = Maze(self.columns, self.rows)

        self.background_color = (20,80,20)
        self.add_layer(self.get_wall_map_layer())
        self.add_layer(self.get_loot_map_layer())
        self.generate_maze()

    def generate_maze(self, seed=None):
        """Generates (or re-generates) the map. The Maze class does most of the work.

        Regenerates the maze, clears the wall map layer and the loot map layer (in case
        there was a previous maze), and then populates these layers with new wall sprites
        and loot sprites.
        
        Args:
            seed: Random seed to pass to the maze (see Maze.generate)
        """
        self.maze.generate(seed)
        wall_map_layer = self.get_layer_by_name("walls")
        wall_map_layer.clear()
        for x, y in self.maze.get_walls():
            wall_map_layer.add_sprite(x, y)
        loot_map_layer = self.get_layer_by_name("loot")
        loot_map_layer.clear()
        for x, y in random.sample(self.possible_loot_locations(), self.num_loot):
            loot_map_layer.add_sprite(x, y)

    def get_wall_map_layer(self):
        """Creates a new :py:class:`GridMapLayer` to hold walls.
        """
        return GridMapLayer(
            name="walls",
            columns=self.columns,
            rows=self.rows,
            pixel_width=self.columns * self.tile_size,
            pixel_height=self.rows * self.tile_size,
            sprite_filename="assets/sprites/box.png",
            sprite_class=Wall,
        )

    def get_loot_map_layer(self):
        """Creates a new :py:class:`GridMapLayer` to hold loot.
        """
        return GridMapLayer(
            name="loot",
            columns=self.columns,
            rows=self.rows,
            pixel_width=self.columns * self.tile_size,
            pixel_height=self.rows * self.tile_size,
            sprite_filename="assets/sprites/star.png",
            sprite_class=Loot
        )

    def possible_loot_locations(self):
        """Returns a list of points where loot could be placed. 
        """
        X = range(1, self.columns, 2)
        Y = range(1, self.rows, 2)
        return list(product(X, Y))

if __name__ == '__main__':
    game = MazeGame()
    game.run()
