import pyxel

class MyApp:
    def __init__(self):
        pyxel.init(640, 480, display_scale=1)
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit
    
    def draw_large_text(x, y, text, col):
        for i, c in enumerate(text):
            char_code = ord(c)
            font_x = (char_code % 16) * 8
            font_y = (char_code // 16) * 8

            for dx in range(2):
                for dy in range(2):
                    pyxel.blt(x + i*16 + dx*8, y + dy*8, 0, font_x, font_y, 8, 8, 0)

    def draw(self):
        pyxel.cls(0)

        # テキストボックスの背景
        pyxel.rect(0, 350, 640, 130, 11)
        pyxel.rect(5, 355, 120, 120, 7)
        pyxel.rect(130, 355, 505, 120, 7)

        # テキスト
        pyxel.text(135, 360, "testtesttest", col=1)
        pyxel.text(135, 370, "testtesttest", col=1)
        pyxel.text(135, 380, "testtesttest", col=1)
MyApp()
