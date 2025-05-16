import random
import itertools

class MapGenerator:
    def __init__(self, cells_x, cells_y, cell_size=5):
        self.cells_x = cells_x
        self.cells_y = cells_y
        self.cell_size = cell_size
        self.tiles = {}
        self.stairs_up_pos = None
        self.stairs_down_pos = None

    def _astar(self, start, goal):
        def heuristic(a, b):
            ax, ay = a
            bx, by = b
            return abs(ax - bx) + abs(ay - by)

        def reconstruct_path(n):
            if n == start:
                return [n]
            return reconstruct_path(came_from[n]) + [n]

        def neighbors(n):
            x, y = n
            return (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)

        closed = set()
        open_set = set([start])
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        while open_set:
            current = min(open_set, key=lambda o: f_score.get(o, float('inf')))
            if current == goal:
                return reconstruct_path(goal)

            open_set.remove(current)
            closed.add(current)

            for neighbor in neighbors(current):
                if neighbor in closed:
                    continue
                tentative_g = g_score[current] + 1

                if neighbor not in open_set or tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    open_set.add(neighbor)

        return []

    def generate(self, use_numeric=False):
        # セルの定義
        class Cell:
            def __init__(self, x, y, id):
                self.x = x
                self.y = y
                self.id = id
                self.connected = False
                self.connected_to = []
                self.room = None

            def connect(self, other):
                if other not in self.connected_to:
                    self.connected_to.append(other)
                if self not in other.connected_to:
                    other.connected_to.append(self)
                self.connected = True
                other.connected = True

        # セル作成
        cells = {}
        for y in range(self.cells_y):
            for x in range(self.cells_x):
                c = Cell(x, y, len(cells))
                cells[(x, y)] = c

        # ランダムに最初のセルを選択
        current = last_cell = first_cell = random.choice(list(cells.values()))
        current.connected = True

        def get_neighbors(cell):
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                neighbor = cells.get((cell.x + dx, cell.y + dy))
                if neighbor:
                    yield neighbor

        # ステップ3: 現在のセルからつながっていない隣接セルへ繋げていく
        while True:
            unconnected = [n for n in get_neighbors(current) if not n.connected]
            if not unconnected:
                break
            neighbor = random.choice(unconnected)
            current.connect(neighbor)
            current = last_cell = neighbor

        # ステップ4: まだつながってないセルがあれば、つながってるセルと繋ぐ
        while True:
            unconnected = [c for c in cells.values() if not c.connected]
            if not unconnected:
                break
            candidates = []
            for c in [c for c in cells.values() if c.connected]:
                nbs = [n for n in get_neighbors(c) if not n.connected]
                if nbs:
                    candidates.append((c, nbs))
            if not candidates:
                break
            cell, neighbors = random.choice(candidates)
            cell.connect(random.choice(neighbors))

        # ステップ5: 余分な通路をランダムに作る
        extra_connections = random.randint(int((self.cells_x + self.cells_y) / 4), int((self.cells_x + self.cells_y) / 1.2))
        retries = 10
        while extra_connections > 0 and retries > 0:
            cell = random.choice(list(cells.values()))
            neighbor = random.choice(list(get_neighbors(cell)))
            if neighbor in cell.connected_to:
                retries -= 1
                continue
            cell.connect(neighbor)
            extra_connections -= 1

        # ステップ6: 各セルに部屋を作る
        rooms = []
        for cell in cells.values():
            w = random.randint(3, self.cell_size - 2)
            h = random.randint(3, self.cell_size - 2)
            x = cell.x * self.cell_size + random.randint(1, self.cell_size - w - 1)
            y = cell.y * self.cell_size + random.randint(1, self.cell_size - h - 1)
            floor_tiles = [(x + i, y + j) for i in range(w) for j in range(h)]
            cell.room = floor_tiles
            rooms.append(floor_tiles)

        # ステップ7: セル同士の通路をA*で作成
        connections = {}
        for c in cells.values():
            for other in c.connected_to:
                pair = tuple(sorted((c.id, other.id)))
                connections[pair] = (c.room, other.room)

        for room_a, room_b in connections.values():
            start = random.choice(room_a)
            goal = random.choice(room_b)
            corridor = []
            for tile in self._astar(start, goal):
                if tile not in room_a and tile not in room_b:
                    corridor.append(tile)
            rooms.append(corridor)

        # タイル初期化（0:空地 or ' '、1:壁 or '#', 2:床 or '.', 98:階段上, 99:階段下）
        width = self.cells_x * self.cell_size
        height = self.cells_y * self.cell_size

        if use_numeric:
            self.tiles = {(x, y): 0 for x in range(width) for y in range(height)}
        else:
            self.tiles = {(x, y): ' ' for x in range(width) for y in range(height)}

        # 床タイルをセット
        floor_tile_val = 2 if use_numeric else '.'
        for tile in itertools.chain.from_iterable(rooms):
            self.tiles[tile] = floor_tile_val

        # 壁タイル生成（床の隣接タイルを壁に）
        wall_tile_val = 1 if use_numeric else '#'
        for (x, y), tile in list(self.tiles.items()):
            if (tile == 0 and use_numeric) or (tile == ' ' and not use_numeric):
                for nx in range(x-1, x+2):
                    for ny in range(y-1, y+2):
                        neighbor_tile = self.tiles.get((nx, ny))
                        if neighbor_tile == floor_tile_val:
                            self.tiles[(x, y)] = wall_tile_val
                            break

        # 階段設置
        self.stairs_up_pos = random.choice(first_cell.room)
        self.stairs_down_pos = random.choice(last_cell.room)
        self.tiles[self.stairs_up_pos] = 98 if use_numeric else '<'
        self.tiles[self.stairs_down_pos] = 99 if use_numeric else '>'

        return self.tiles

    def get_stairs_positions(self):
        return self.stairs_up_pos, self.stairs_down_pos
