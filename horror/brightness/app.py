import pyxel
import math

MAP_WIDTH = 16    # マップ横のタイル数
MAP_HEIGHT = 12   # マップ縦のタイル数
TILE_SIZE = 10    # タイルの1辺のピクセル数

class LightDemo:
    def __init__(self):
        # ウィンドウ初期化（幅×高さ, タイトル）
        pyxel.init(MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE, title="Light & Shadow Demo")

        # 1は壁、0は床（歩ける場所）
        self.map = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1],
            [1,0,1,1,0,1,1,0,1,0,1,1,1,0,0,1],
            [1,0,0,1,0,0,1,0,0,0,1,0,0,0,0,1],
            [1,0,0,1,1,0,1,1,1,0,1,0,1,1,0,1],
            [1,0,0,0,0,0,0,0,1,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,1,0,1,1,1,1,0,1,0,1],
            [1,0,1,0,0,0,1,0,0,0,0,1,0,1,0,1],
            [1,0,1,0,1,0,1,1,1,1,0,1,0,1,0,1],
            [1,0,0,0,1,0,0,0,0,1,0,0,0,1,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]

        # プレイヤー初期位置（中心を指定）
        self.player_x = 5 * TILE_SIZE + TILE_SIZE // 2
        self.player_y = 5 * TILE_SIZE + TILE_SIZE // 2

        self.light_radius = 60  # 光の届く最大距離（ピクセル）

        # ゲームループ開始
        pyxel.run(self.update, self.draw)

    def update(self):
        speed = 2  # 移動速度（ピクセル）
        # キー入力に応じて移動を試みる
        if pyxel.btn(pyxel.KEY_LEFT):
            self.try_move(-speed, 0)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.try_move(speed, 0)
        if pyxel.btn(pyxel.KEY_UP):
            self.try_move(0, -speed)
        if pyxel.btn(pyxel.KEY_DOWN):
            self.try_move(0, speed)

    def try_move(self, dx, dy):
        # 新しい位置候補
        new_x = self.player_x + dx
        new_y = self.player_y + dy

        # 候補位置がどのタイルか判定
        tile_x = new_x // TILE_SIZE
        tile_y = new_y // TILE_SIZE

        # マップ内かつ壁じゃなければ移動
        if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
            if self.map[tile_y][tile_x] == 0:
                self.player_x = new_x
                self.player_y = new_y

    def draw(self):
        pyxel.cls(0)  # 画面を黒でクリア

        # マップをタイル単位で描画（床は明るめ、壁は暗めの色）
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                color = 7 if self.map[y][x] == 0 else 1
                pyxel.rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, color)

        # プレイヤーを円で描画
        pyxel.circ(self.player_x, self.player_y, 4, 8)

        # 光の描画（影も含めて光が届く範囲を計算して描く）
        self.draw_light()

    def draw_light(self):
        rays = 180  # 光線の本数（多いほど滑らかな光になる）
        step = 2    # 光を伸ばす間隔（ピクセル単位）

        # 360度ぐるっと光線を飛ばす
        for i in range(rays):
            angle = (2 * math.pi) * i / rays  # 光線の角度（ラジアン）

            x = self.player_x  # 光源のX座標（プレイヤー位置）
            y = self.player_y  # 光源のY座標

            # 光線を光源からstepずつ伸ばしていく
            for r in range(0, self.light_radius, step):
                # 光線の現在位置（x,y）
                test_x = x + math.cos(angle) * r
                test_y = y + math.sin(angle) * r

                # 現在位置がどのタイルか判定
                tile_x = int(test_x) // TILE_SIZE
                tile_y = int(test_y) // TILE_SIZE

                # マップ外なら光線を中断
                if tile_x < 0 or tile_x >= MAP_WIDTH or tile_y < 0 or tile_y >= MAP_HEIGHT:
                    break

                # 壁にぶつかったら光線を中断
                if self.map[tile_y][tile_x] == 1:
                    break

                # 光の届く場所は明るい色で点を打つ
                pyxel.pset(int(test_x), int(test_y), 10)

if __name__ == "__main__":
    LightDemo()
