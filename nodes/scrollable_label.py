from nodes import Label


class ScrollableLabel(Label):
    def __init__(self):
        super().__init__()

        self.lines_count = 0
        self.lines = []

        self.chars_per_line = 40

        self.update_render_data()

    def render(self):
        for i in range(self.lines_count):
            line_rendered = self.lines[i]
            self.window.blit(line_rendered, (self.position.x, self.position.y+(self.font_size*i)))

    def update_render_data(self):
        super().update_render_data()

        self.lines.clear()

        text = self.text

        text_per_lines = text.split("\n")
        for line in text_per_lines:
            text_rendered = self.font.render(line, True, self.color)
            self.lines.append(text_rendered)

        self.lines_count = len(self.lines)



    def update(self):
        super().update()
