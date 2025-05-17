import pyxel
import random

class Turn:
    def __init__(self, score):
        self.turn_score = score
        self.turn_subject = False

class TurnManager:
    def __init__(self):
        self.turn_list = []
        self.current_turn_index = 0
        self.turn_onoff = False
        self.turn_active = False  # 表示制御用

    def sort_by_turn_score(self):
        self.turn_list.sort(key=lambda x: x.turn.turn_score)
        print("=== Turn Order ===")
        for i, obj in enumerate(self.turn_list):
            name = obj.name if hasattr(obj, "name") else "Player"
            print(f"{i+1}: {name}")
        print("==================")

    def next_turn(self):
        self.turn_list[self.current_turn_index].turn.turn_subject = False
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_list)
        self.turn_list[self.current_turn_index].turn.turn_subject = True

    def reset(self):
        self.turn_list = []
        self.current_turn_index = 0
        self.turn_active = False

class Enemy:
    def __init__(self, name):
        self.name = name
        self.turn = Turn(random.randint(1, 5))
        self.point = [3, 3]
        self.frame_count = 0  # フレーム制御用

    def update(self, tm, command_mode, turn_flag):
        if self.turn.turn_subject:
            # ターン制モード：低速行動（待機10フレーム）
            self.frame_count += 1
            if self.frame_count < 10:
                return False
            self.frame_count = 0
        elif not tm.turn_onoff:
            # 通常モード：遅めの移動（待機50フレーム）
            self.frame_count += 1
            if self.frame_count < 50:
                return False
            self.frame_count = 0

        # プレイヤーがバトルエリア内なら敵も制限ありで動く
        if tm.turn_onoff:
            if self.turn.turn_subject:
                self.random_move(battle_area_only=True)
                return True
        else:
            self.random_move(battle_area_only=False)
        return False

    def random_move(self, battle_area_only):
        dx, dy = 0, 0
        move = random.randint(0, 3)
        if move == 0:
            dy = -1
        elif move == 1:
            dy = 1
        elif move == 2:
            dx = -1
        elif move == 3:
            dx = 1
        new_x = self.point[0] + dx
        new_y = self.point[1] + dy
        if 0 <= new_y < 12 and 0 <= new_x < 12:
            if not battle_area_only or MyApp.map_data[new_y][new_x] == 1:
                self.point = [new_x, new_y]

    def draw(self):
        pyxel.rect(self.point[0] * 40, self.point[1] * 40, 40, 40, 9)

class Player:
    def __init__(self):
        self.turn = Turn(random.randint(6, 10))
        self.player_point = [8, 8]
        self.name = "Player"

    def update(self, tm, command_mode, turn_flag):
        acted = False
        if self.turn.turn_subject:
            if pyxel.btnp(pyxel.KEY_UP):
                self.player_point[1] -= 1
                acted = True
            elif pyxel.btnp(pyxel.KEY_DOWN):
                self.player_point[1] += 1
                acted = True
            elif pyxel.btnp(pyxel.KEY_LEFT):
                self.player_point[0] -= 1
                acted = True
            elif pyxel.btnp(pyxel.KEY_RIGHT):
                self.player_point[0] += 1
                acted = True
        elif not tm.turn_onoff:
            # 通常移動
            if pyxel.btnp(pyxel.KEY_UP):
                self.player_point[1] -= 1
            elif pyxel.btnp(pyxel.KEY_DOWN):
                self.player_point[1] += 1
            elif pyxel.btnp(pyxel.KEY_LEFT):
                self.player_point[0] -= 1
            elif pyxel.btnp(pyxel.KEY_RIGHT):
                self.player_point[0] += 1
        return acted

    def draw(self):
        pyxel.rect(self.player_point[0] * 40, self.player_point[1] * 40, 40, 40, 11)

class MyApp:
    map_data = [
        [0]*12,
        [0]*12,
        [0,1,1,1,1,1,0,0,0,0,0,0],
        [0,1,1,1,1,1,0,0,0,0,0,0],
        [0,1,1,1,1,1,0,0,0,0,0,0],
        [0,1,1,1,1,1,0,0,0,0,0,0],
        [0,1,1,1,1,1,0,0,0,0,0,0],
        [0,1,1,1,1,1,0,0,0,0,0,0],
        [0,1,1,1,1,1,0,0,0,0,0,0],
        [0]*12,
        [0]*12,
        [0]*12
    ]

    def __init__(self):
        self.turnmanager = TurnManager()
        self.player = Player()
        self.enemy_list = [Enemy("1"), Enemy("2")]

        pyxel.init(480, 480)
        pyxel.run(self.update, self.draw)

    def update(self):
        px, py = self.player.player_point
        if MyApp.map_data[py][px] == 1:
            if not self.turnmanager.turn_onoff:
                # バトル突入時
                self.turnmanager.turn_onoff = True
                self.turnmanager.reset()
                self.turnmanager.turn_list.append(self.player)
                for enemy in self.enemy_list:
                    ex, ey = enemy.point
                    if MyApp.map_data[ey][ex] == 1:
                        self.turnmanager.turn_list.append(enemy)
                self.turnmanager.sort_by_turn_score()
                self.turnmanager.turn_list[0].turn.turn_subject = True
                self.turnmanager.turn_active = True

            # ターン制更新
            current = self.turnmanager.turn_list[self.turnmanager.current_turn_index]
            if current.update(self.turnmanager, True, True):
                self.turnmanager.next_turn()
        else:
            # バトル外行動
            self.turnmanager.turn_onoff = False
            self.turnmanager.turn_active = False
            self.player.update(self.turnmanager, False, False)
            for enemy in self.enemy_list:
                enemy.update(self.turnmanager, False, False)

    def draw_turn_order(self):
        if self.turnmanager.turn_active:
            x = pyxel.width - 80
            y = 5
            # 背景用に黒い矩形
            pyxel.rect(x - 5, y - 5, 75, 80, 0)

            pyxel.text(x, y, "Turn Order:", pyxel.COLOR_WHITE)
            for i, obj in enumerate(self.turnmanager.turn_list):
                y_pos = y + 12 + i * 14
                is_current = (i == self.turnmanager.current_turn_index)
                name = obj.name if hasattr(obj, "name") else "Player"
                display_text = f"{'▶' if is_current else '  '} {name}"
                color = pyxel.COLOR_YELLOW if is_current else pyxel.COLOR_WHITE
                pyxel.text(x, y_pos, display_text, color)

    def draw(self):
        pyxel.cls(0)
        for y, row in enumerate(MyApp.map_data):
            for x, tile in enumerate(row):
                color = 5 if tile == 1 else 7
                pyxel.rect(x * 40, y * 40, 40, 40, color)

        for enemy in self.enemy_list:
            enemy.draw()
        self.player.draw()

        self.draw_turn_order()

MyApp()
