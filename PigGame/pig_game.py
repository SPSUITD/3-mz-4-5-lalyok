import arcade

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Pig'em all!"
TILE_SCALING = 1

MOVEMENT_SPEED = 5

LAYER_NAME_WALLS = "Walls"
LAYER_NAME_APPLES = "Apples"
LAYER_NAME_EDGES = "Edges"
LAYER_NAME_GROUND = "Ground"

CHARACTER_SCALING = 1
ANIMATION_SPEED = 0.1



class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture("assets/start-screen.png")
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)
        self.window.set_mouse_visible(True)

    def on_draw(self):
        self.clear()
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)
        game_view.setup()


class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture("assets/game-over-screen.png")
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)
        self.window.set_mouse_visible(True)

    def on_draw(self):
        self.clear()
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)
        game_view.setup()


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.tile_map = None
        self.scene = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = None
        self.score = 0
        self.goal = 0

        self.player_sprite = None
        self.wall_list = None
        self.edge_list = None
        self.apple_list = None
        self.player_list = None

        self.map_width = 0
        self.map_height = 0

        self.player_textures = {
            "up": [],
            "down": [],
            "left": [],
            "right": []
        }
        self.current_texture = 0
        self.player_direction = "down"
        self.animation_timer = 0.0

        self.window.set_mouse_visible(False)

    def setup(self):

        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.gui_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        layer_options = {
            LAYER_NAME_WALLS: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "Detailed",
            },
            LAYER_NAME_APPLES: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "Detailed",
            },
            LAYER_NAME_EDGES: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "Detailed",
            },
            LAYER_NAME_GROUND: {
                "use_spatial_hash": True,
            },
        }

        self.tile_map = arcade.load_tilemap("map.json", TILE_SCALING, layer_options)

        self.wall_list = self.tile_map.sprite_lists[LAYER_NAME_WALLS]
        self.edge_list = self.tile_map.sprite_lists[LAYER_NAME_EDGES]
        self.apple_list = self.tile_map.sprite_lists[LAYER_NAME_APPLES]

        self.map_width = self.tile_map.width * self.tile_map.tile_width
        self.map_height = self.tile_map.height * self.tile_map.tile_height

        self.load_player_animations()

        self.player_sprite = arcade.Sprite()
        self.player_sprite.center_x = self.map_width / 2
        self.player_sprite.center_y = self.map_height / 2
        self.player_sprite.scale = CHARACTER_SCALING
        self.player_sprite.textures = self.player_textures["down"]
        self.player_sprite.texture = self.player_textures["down"][0]
        self.player_sprite.set_hit_box([(-20, -20), (-20, 20), (20, 20), (20, -20)])

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        self.goal = len(self.apple_list)

        self.adjust_edge_hitboxes()

    def adjust_edge_hitboxes(self):
        for edge_sprite in self.edge_list:
            half_width = edge_sprite.width * 0.25
            half_height = edge_sprite.height * 0.25
            points = [
                (-half_width, -half_height),
                (half_width, -half_height),
                (half_width, half_height),
                (-half_width, half_height)
            ]
            edge_sprite.set_hit_box(points)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.player_list.draw()

        self.gui_camera.use()

        score_text = f"Picked: {self.score}/{self.goal}"
        arcade.draw_text(
            score_text,
            10,
            SCREEN_HEIGHT - 30,
            arcade.csscolor.WHITE,
            18,
        )

    def load_player_animations(self):
        self.player_textures["down"] = arcade.load_spritesheet("assets/walking-down.png", 128, 128, 4, 4)
        self.player_textures["up"] = arcade.load_spritesheet("assets/walking-up.png", 128, 128, 4, 4)
        self.player_textures["left"] = arcade.load_spritesheet("assets/walking-left.png", 128, 128, 4, 4)
        self.player_textures["right"] = arcade.load_spritesheet("assets/walking-right.png", 128, 128, 4, 4)

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
                self.camera.viewport_height / 2
        )

        if screen_center_x < 0:
            screen_center_x = 0
        elif screen_center_x > self.map_width - self.camera.viewport_width:
            screen_center_x = self.map_width - self.camera.viewport_width

        if screen_center_y < 0:
            screen_center_y = 0
        elif screen_center_y > self.map_height - self.camera.viewport_height:
            screen_center_y = self.map_height - self.camera.viewport_height

        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def on_update(self, delta_time):
        self.physics_engine.update()

        self.animation_timer += delta_time

        if self.animation_timer >= ANIMATION_SPEED and (
                self.player_sprite.change_x != 0 or self.player_sprite.change_y != 0):
            self.current_texture += 1
            if self.current_texture >= len(self.player_textures[self.player_direction]):
                self.current_texture = 0
            self.player_sprite.texture = self.player_textures[self.player_direction][self.current_texture]
            self.animation_timer = 0.0

        apple_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.apple_list)
        for apple in apple_hit_list:
            apple.remove_from_sprite_lists()
            self.score += 1

        if arcade.check_for_collision_with_list(self.player_sprite, self.edge_list) or len(self.apple_list) == 0:
            view = GameOverView()
            self.window.show_view(view)

        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
        elif self.player_sprite.right > self.map_width:
            self.player_sprite.right = self.map_width

        if self.player_sprite.bottom < 0:
            self.player_sprite.bottom = 0
        elif self.player_sprite.top > self.map_height:
            self.player_sprite.top = self.map_height

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
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
