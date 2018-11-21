import tkinter, time

# BIG TOGO: move to pygame from my hacky Tkinter implementation

# TODO: make height, width a variable r open to change
class Display:

    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=1024, height=512)
        self.canvas.pack()
        self.pixels = list()
        self.framebuffer = [0] * 2048
        pixel_size = 16
        for i in range(32):
            for j in range(64):
                pixel = self.canvas.create_rectangle(j * pixel_size,
                                                     i * pixel_size,
                                                     (j + 1) * pixel_size,
                                                     (i + 1) * pixel_size,
                                                     fill="black",
                                                     outline="")
                self.pixels.append(pixel)

    # Note: clearing the screen is just setting the frame buffer to all 0
    def render(self):
        for i in range(2048):
            pixel = self.pixels[i]
            value = self.framebuffer[i]
            color = "black"
            if value == 1:
                color = "white"
            self.canvas.itemconfig(pixel, fill=color)
        # self.print_frame()

    def print_frame(self):
        buf = self.framebuffer
        print("--------------------------------------------------------------------")
        for i in range(32):
            s = ''
            for j in range(64):
                s += str(buf[i * 64 + j])
            print(s)


    def draw_sprite(self, x, y, sprite):
        flag = 0
        for byte in sprite:
            for bit in range(8):
                value = (byte >> (7 - bit)) & 1
                index = (y % 32) * 64 + ((x + bit) % 64)
                previous = self.framebuffer[index]
                if previous == 1 and value == 1:
                    flag = 1
                self.framebuffer[index] = previous ^ value
            y += 1
        self.render()
        return flag


    def clear_screen(self):
        # TODO: check if the below is acceptable / has ok performance compared
        # to manual clearing
        self.framebuffer = [0] * 2048
        self.render()
