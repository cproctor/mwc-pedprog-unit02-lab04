from quest.game import QuestGame
from quest.map import TiledMap
from quest.dialogue import Dialogue
from quest.modal import Modal, DialogueModal
from quest.sprite import QuestSprite, Player, Wall, NPC
from quest.helpers import scale
from quest.strategy import RandomWalk
import arcade
import os
from pathlib import Path

class GrandmasSoupGame(QuestGame):
    """Help Grandma find all the ingredients for her soup.

    GrandmasSoupGame shows off the full range of features in the Quest
    framework, loading a map and letting the player explore it. Grandma and the Vegetables
    are subclasses of NPC. A DialogueModal is used for the conversations
    with Grandma.
    """

    player_sprite_image = "assets/sprites/boy.png"
    screen_width = 500
    screen_height = 500
    left_viewport_margin = 96
    right_viewport_margin = 96
    bottom_viewport_margin = 96
    top_viewport_margin = 96
    player_initial_x = 300
    player_initial_y = 300
    player_speed = 8

    def __init__(self):
        super().__init__()
        self.dialogue = Dialogue.from_ink("assets/ink/grandma.ink")
        self.modal = DialogueModal(self, self.dialogue)
        self.items = []

    def setup_maps(self):
        """Sets up the standard island map.
        """
        super().setup_maps()
        sprite_classes = {
            "Obstacles": Wall,
            "Background": QuestSprite,
        }
        self.add_map(TiledMap("assets/tilemaps/island.json", sprite_classes))

    def setup_walls(self):
        """As in other examples, assigns all sprites in the "Obstacles" layer to be walls.
        """
        self.wall_list = self.get_current_map().get_layer_by_name("Obstacles").sprite_list

    def setup_npcs(self):
        """Creates and places Grandma and the vegetables.
        """
        npc_data = [
            [Grandma, "assets/sprites/grandma.png", 3, 400, 400],
            [Carrots, "assets/sprites/carrots.png", 1, 220, 640],
            [Mushroom, "assets/sprites/mushroom.png", 1, 1028, 264],
            [Potatoes, "assets/sprites/potatoes.png", 1, 959, 991],
            [Tomatoes, "assets/sprites/tomatos.png", 1, 323, 1055],
        ]
        self.npc_list = arcade.SpriteList()
        for sprite_class, image_path, scale, x, y in npc_data:
            sprite = sprite_class(image_path, scale)
            sprite.center_x = x
            sprite.center_y = y
            self.npc_list.append(sprite)

        grandma = self.npc_list[0]
        walk = RandomWalk(0.05)
        grandma.strategy = walk

    def talk_with_grandma(self):
        """Opens the dialogue modal to show conversation with Grandma. This is called
        when the player collides with Grandma.
        """
        self.open_modal(self.modal)

    def got_item(self, description):
        """Adds the item's description to the items list. This is called when the
        player collides with a vegetable.
        """
        self.items.append(description.upper())
        if len(self.items) < 4:
            self.dialogue.run(self.items[-1])
        else:
            self.dialogue.run("SOUP")

class Grandma(NPC):
    """Grandma is an NPC.

    Attributes:
        repel_distance: How far back the player should be pushed after colliding
            with Grandma. This is necessary because otherwise when the dialogue modal
            closed, it would immediately reopen. Grandma is interesting, but not that
            interesting.
    """
    repel_distance = 20

    def on_collision(self, sprite, game):
        """When the player collides with Grandma, she repels the player and then
        :py:meth:`talk_with_grandma` is called to open the dialogue modal.
        """
        if isinstance(sprite, Player):
            self.repel(sprite)

            game.talk_with_grandma()

    def repel(self, sprite):
        "Backs the sprite away from self"
        away = (self.center_x - sprite.center_x, self.center_y - sprite.center_y)
        away_x, away_y = scale(away, self.repel_distance)
        sprite.center_x = sprite.center_x - away_x
        sprite.center_y = sprite.center_y - away_y
        sprite.stop()

class Vegetable(NPC):
    """A vegetable is an NPC that can be picked up.
    """
    description = "item"
    def on_collision(self, sprite, game):
        """When the player collides with a vegetable, it tells the game and then
        removes itself.
        """
        game.got_item(self.description)
        self.kill()

class Carrots(Vegetable):
    description = "carrots"

class Mushroom(Vegetable):
    description = "mushroom"

class Potatoes(Vegetable):
    description = "potatoes"

class Tomatoes(Vegetable):
    description = "tomatoes"

if __name__ == '__main__':
    game = GrandmasSoupGame()
    game.run()
