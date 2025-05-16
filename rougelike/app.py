import pyxel
from generator import MapGenerator

class MyApp:
    def __init__(self):
        self.mg = MapGenerator(8, 8, 10)
        self.tiles = self.mg.generate(use_numeric=True)
        self.width = self.mg.cells_x * self.mg.cell_size
        self.height = self.mg.cells_y * self.mg.cell_size

        # プレイヤー初期位置
        self.player_x, self.player_y = self.mg.get_stairs_positions()[0]

        # 1マスのサイズ（見やすく拡大）
        self.tile_size = 32

        # 表示マス数（カメラ範囲）
        self.camera_tiles_x = 10
        self.camera_tiles_y = 6

        # 実際のウィンドウサイズ（ここで display_scale ではなくピクセルで大きめに確保）
        self.screen_width = self.camera_tiles_x * self.tile_size
        self.screen_height = self.camera_tiles_y * self.tile_size

        # display_scaleを大きめに（例:4）
        pyxel.init(self.screen_width, self.screen_height, title="roguelike-zoom", display_scale=4)
        pyxel.run(self.update, self.draw)

    def update(self):
        dx, dy = 0, 0
        if pyxel.btnp(pyxel.KEY_UP):
            dy = -1
        elif pyxel.btnp(pyxel.KEY_DOWN):
            dy = 1
        elif pyxel.btnp(pyxel.KEY_LEFT):
            dx = -1
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            dx = 1

        next_tile = self.tiles.get((self.player_x + dx, self.player_y + dy), 1)
        if next_tile in (2, 98, 99):
            self.player_x += dx
            self.player_y += dy

        # Rキーでマップ再生成
        if pyxel.btnp(pyxel.KEY_R):
            self.tiles = self.mg.generate(use_numeric=True)
            self.player_x, self.player_y = self.mg.get_stairs_positions()[0]

    def draw(self):
        pyxel.cls(0)

        # カメラの左上タイル座標
        cam_left = self.player_x - self.camera_tiles_x // 2
        cam_top = self.player_y - self.camera_tiles_y // 2

        for y in range(self.camera_tiles_y):
            for x in range(self.camera_tiles_x):
                map_x = cam_left + x
                map_y = cam_top + y
                tile = self.tiles.get((map_x, map_y), 0)
                color = self.tile_color(tile)
                px = x * self.tile_size
                py = y * self.tile_size
                pyxel.rect(px, py, self.tile_size, self.tile_size, color)

        # プレイヤーを中央に表示
        px = (self.camera_tiles_x // 2) * self.tile_size
        py = (self.camera_tiles_y // 2) * self.tile_size
        pyxel.rect(px, py, self.tile_size, self.tile_size, 11)

    def tile_color(self, tile):
        return {
            0: 0,    # 空白
            1: 5,    # 壁
            2: 7,    # 床
            98: 10,  # 階段UP
            99: 8    # 階段DOWN
        }.get(tile, 13)

MyApp()
