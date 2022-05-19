from quest.game import QuestGame
from quest.map import Map, GridMapLayer, TiledMap
from quest.sprite import Background, Wall
from quest.engines import DiscretePhysicsEngine
import os
from pathlib import Path

class IslandAdventureDiscrete(QuestGame):
    """An alternate version of Island Adventure, using discrete movement.
    """
    player_sprite_image = "assets/sprites/boy.png"
    player_initial_x = 300
    player_initial_y = 300
    player_speed = 8

    def setup_maps(self):
        "Sets up the map."
        super().setup_maps()
        sprite_classes = {
            "Obstacles": Wall,
            "Background": Background,
        }
        self.add_map(TiledMap("assets/tilemaps/island.json", sprite_classes))
        layer = GridMapLayer("grid", 40, 40, 40*32, 40*32)
        self.get_current_map().add_layer(layer)

    def setup_walls(self):
        """Assigns sprites to `self.wall_list`. These sprites will function as walls, blocking
        the player from passing through them.
        """
        self.wall_list = self.get_current_map().get_layer_by_name("Obstacles").sprite_list

    def setup_physics_engine(self):
        """Uses DiscretePhysicsEngine instead of the standard ContinuousPhysicsEngine.
        The result is that the player snaps to a grid instead of moving smoothly to any position.

        A game's physics engine is responsible for enforcing the rules of the game's reality.
        In a fancy 3d game, the physics engine is full of intense math to keep track of objects
        flying around, bouncing off of walls, and breaking into pieces.

        Quest's physics engines are simpler. They just need to make sure nobody walks through walls,
        and to check when sprites collide. There are two physics engines built-in: A continuous (the
        default) and a discrete (used here).
        """
        grid = self.get_current_map().get_layer_by_name('grid')
        self.physics_engine = DiscretePhysicsEngine(self, grid)

if __name__ == '__main__':
    game = IslandAdventureDiscrete()
    game.run()
