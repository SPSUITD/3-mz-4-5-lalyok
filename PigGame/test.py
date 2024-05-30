import arcade

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "PigGame"
TILE_SCALING = 1

MOVEMENT_SPEED = 5

LAYER_NAME_WALLS = "Walls"
LAYER_NAME_APPLES = "Apples"
LAYER_NAME_EDGES = "Edges"
LAYER_NAME_GROUND = "Ground"

CHARACTER_SCALING = 1
ANIMATION_SPEED = 0.1  # The speed of the animation

class PigGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.tile_map = None
        self.scene = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = None
        self.score = 0

        self.player_sprite = None
        self.wall_list = None
        self.edge_list = None
        self.apple_list = None
        self.player_list = None

        self.player_textures = {
            "up": [],
            "down": [],
            "left": [],
            "right": []
        }
        self.current_texture = 0
        self.player_direction = "down"

    def setup(self):
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        layer_options = {
            LAYER_NAME_WALLS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_APPLES: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_EDGES: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_GROUND: {
                "use_spatial_hash": True,
            },
        }

        self.tile_map = arcade.load_tilemap("map.json", TILE_SCALING, layer_options)

        self.wall_list = self.tile_map.sprite_lists[LAYER_NAME_WALLS]
        self.edge_list = self.tile_map.sprite_lists[LAYER_NAME_EDGES]
        self.apple_list = self.tile_map.sprite_lists[LAYER_NAME_APPLES]

        # Load player animations
        self.load_player_animations()

        # Set up the player
        self.player_sprite = arcade.Sprite()
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.player_sprite.scale = CHARACTER_SCALING
        self.player_sprite.textures = self.player_textures["down"]
        self.player_sprite.texture = self.player_textures["down"][0]
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        self.score = 0

    def load_player_animations(self):
        self.player_textures["down"] = arcade.load_spritesheet("assets/walking-down.png", 128, 128, 4, 4)
        self.player_textures["up"] = arcade.load_spritesheet("assets/walking-up.png", 128, 128, 4, 4)
        self.player_textures["left"] = arcade.load_spritesheet("assets/walking-left.png", 128, 128, 4, 4)
        self.player_textures["right"] = arcade.load_spritesheet("assets/walking-right.png", 128, 128, 4, 4)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.player_list.draw()
        self.gui_camera.use()

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Prevent the camera from scrolling past the edges of the map
        map_width = self.tile_map.width * self.tile_map.tile_width
        map_height = self.tile_map.height * self.tile_map.tile_height

        if screen_center_x < 0:
            screen_center_x = 0
        elif screen_center_x > map_width - self.camera.viewport_width:
            screen_center_x = map_width - self.camera.viewport_width

        if screen_center_y < 0:
            screen_center_y = 0
        elif screen_center_y > map_height - self.camera.viewport_height:
            screen_center_y = map_height - self.camera.viewport_height

        self.camera.move_to((screen_center_x, screen_center_y))

    def on_update(self, delta_time):
        self.physics_engine.update()

        # Update animation
        self.current_texture += 1
        if self.current_texture >= len(self.player_textures[self.player_direction]):
            self.current_texture = 0
        self.player_sprite.texture = self.player_textures[self.player_direction][self.current_texture]

        # Check for collisions with apples
        apple_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.apple_list)
        for apple in apple_hit_list:
            apple.remove_from_sprite_lists()
            self.score += 1

        # Check for collisions with edges
        if arcade.check_for_collision_with_list(self.player_sprite, self.edge_list):
            arcade.close_window()
            print("Game Over!")

        # Check if all apples are collected
        if len(self.apple_list) == 0:
            arcade.close_window()
            print("You Win!")

        # Prevent the player from moving out of the map bounds
        map_width = self.tile_map.width * self.tile_map.tile_width
        map_height = self.tile_map.height * self.tile_map.tile_height

        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
        elif self.player_sprite.right > map_width:
            self.player_sprite.right = map_width

        if self.player_sprite.bottom < 0:
            self.player_sprite.bottom = 0
        elif self.player_sprite.top > map_height:
            self.player_sprite.top = map_height

        self.center_camera_to_player()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
            self.player_direction = "up"
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
            self.player_direction = "down"
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
            self.player_direction = "left"
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED
            self.player_direction = "right"

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

def main():
    game = PigGame()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
