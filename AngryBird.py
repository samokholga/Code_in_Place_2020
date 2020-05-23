import tkinter
from PIL import ImageTk
import time

WIDTH = 1600
HEIGH = 1000
TITLE = 'Angry Ball'
STARTING_X = 250
STARTING_Y = 650
BALL_SIZE = 50
TARGET_X = 1200
TARGET_Y = 500
AIM_X = 1240
AIM_Y = 550
AIM_SIZE = 135
G = 0.07


class AngryBird(object):

    def __init__(self):
        self.top = tkinter.Tk()
        self.background = ImageTk.PhotoImage(file="pics/Background.png")
        self.bird = ImageTk.PhotoImage(file="pics/Bird.png")
        self.target = ImageTk.PhotoImage(file="pics/Target.png")
        self.slingshot_back_img = ImageTk.PhotoImage(file="pics/Rogatka_right.png")
        self.slingshot_front_img = ImageTk.PhotoImage(file="pics/Rogatka_left.png")
        self.mouse_coordinates = {}
        self.v0 = None
        self.sin_alpha = None
        self.cos_alpha = None
        self.goals = 0
        self.ball_coords = {}
        self.canvas = self.make_canvas()
        self.aim = self.make_aim()
        self.slingshot_front = self.make_slingshot_back()
        self.ball = self.make_ball()
        self.slingshot_front = self.make_slingshot_front()
        self.strap = self.make_strap()
        self.text = self.meter()
        # self.meter()

    def mouse_events(self):
        print('mouse events')
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<ButtonRelease-1>', self.on_click_release)
        self.canvas.bind('<Motion>', self.motion)


    def motion(self, event):
        self.x_motion = event.x - BALL_SIZE / 2
        self.y_motion = event.y - BALL_SIZE / 2

    def on_click(self, event):
        print('on click')
        self.mouse_pressed = True
        # self.mouse_released = False
        self.mouse_coordinates['x1'] = event.x
        self.mouse_coordinates['y1'] = event.y
        self.get_ball_coords()
        if (self.ball_coords['b_x1'] <= STARTING_X + 1 or self.ball_coords['b_x1'] >= STARTING_X - 1) and self.mouse_is_on_the_ball():
            self.is_clicked_on_ball = True
            self.follow_mouse()
        elif not self.in_frame() or self.hit_aim():
            self.canvas.moveto(self.ball, STARTING_X, STARTING_Y)
            self.get_ball_coords()
            print(self.ball_coords)
        self.is_clicked_on_ball = False

    def on_click_release(self, event):
        print('on click release')
        self.mouse_pressed = False
        self.canvas.coords(self.strap, STARTING_X + 20, STARTING_Y + 18, STARTING_X + 5, STARTING_Y + 30)
        # self.mouse_released = True

        #print(self.mouse_coordinates, self.is_clicked_on_ball)
        if self.is_clicked_on_ball:
            self.mouse_coordinates['x2'] = event.x
            self.mouse_coordinates['y2'] = event.y
            self.get_starting_coodrinates()
            self.throw_the_ball()
        #else:
        #    self.canvas.moveto(self.ball, STARTING_X, STARTING_Y)

    def get_ball_coords(self):
        print('get ball coords')
        ball_coords_list = self.canvas.coords(self.ball)
        self.ball_coords['b_x1'] = ball_coords_list[0]
        self.ball_coords['b_x2'] = ball_coords_list[0] + BALL_SIZE
        self.ball_coords['b_y1'] = ball_coords_list[1]
        self.ball_coords['b_y2'] = ball_coords_list[1] + BALL_SIZE

    def mouse_is_on_the_ball(self):
        print('mouse is on ball')
        self.get_ball_coords()
        return self.mouse_coordinates['x1'] <= self.ball_coords['b_x2'] and \
               self.mouse_coordinates['x1'] >= self.ball_coords['b_x1'] and \
               self.mouse_coordinates['y1'] <= self.ball_coords['b_y2'] and \
               self.mouse_coordinates['y1'] >= self.ball_coords['b_y1']

    def get_starting_coodrinates(self):
        print('get start coord')
        x1 = STARTING_X
        x2 = self.mouse_coordinates['x2']
        y1 = STARTING_Y
        y2 = self.mouse_coordinates['y2']
        self.v0 = self.velocity(x1, y1, x2, y2)
        self.sin_alpha = self.sin_a(x1, y1, x2, y2)
        self.cos_alpha = self.cos_a(x1, y1, x2, y2)
        print(self.mouse_coordinates)

    def follow_mouse(self):
        print('follow mouse')
        if self.mouse_is_on_the_ball():
            while self.mouse_pressed:
                x = self.x_motion
                y = self.y_motion
                self.canvas.moveto(self.ball, x, y)
                self.canvas.coords(self.strap, STARTING_X+20, STARTING_Y+18, x+5, y+30)
                #self.canvas.itemconfig(self.strap) #------------------------------!!!!!!
                self.canvas.update()
                time.sleep(1 / 50)

    def throw_the_ball(self):
        print('throw thw ball')
        len_of_flight = 0
        # if self.mouse_is_on_the_ball():
        while self.in_frame():
            if self.hit_aim():
                self.goals += 1
                self.canvas.itemconfig(self.text, text=self.goals)
                self.get_ball_coords()
                print(self.ball_coords)
                # while self.ball_coords['b_y1'] < 950:
                #
                #     x = self.x_traectory_back(len_of_flight)
                #     y = self.y_traectory(len_of_flight)
                #     self.canvas.moveto(self.ball, x, y)
                #     self.get_ball_coords()
                #     len_of_flight += 1


                break
            else:
                x = self.x_traectory(len_of_flight)
                y = self.y_traectory(len_of_flight)
                self.canvas.moveto(self.ball, x, y)
                len_of_flight += 1

                # self.text = 'Oooops....try again!'
            self.canvas.update()
            time.sleep(1 / 50)
        # self.finish_canvas()

    def velocity(self, x1, y1, x2, y2):
        print('velosity')
        # v0 should be propotional to the 'strenth' of user's throw,
        # so we'll define it as root(x^2 + y^2) * coeffitient
        return (((y2 - y1) ** 2 + (x1 - x2) ** 2) ** 0.5) * 0.07

    def sin_a(self, x1, y1, x2, y2):
        print('sin')
        # v0 is equal to hypotenuse of our triangle
        # and sin = opposite / hypotenuse
        return (y2 - y1) / ((y2 - y1) ** 2 + (x1 - x2) ** 2) ** 0.5

    def cos_a(self, x1, y1, x2, y2):
        print('cos')
        return (x1 - x2) / ((y2 - y1) ** 2 + (x1 - x2) ** 2) ** 0.5

    def make_ball(self):
        # ball = self.canvas.create_oval(STARTING_X, STARTING_Y, STARTING_X + BALL_SIZE, STARTING_Y - BALL_SIZE,
        #                               fill='magenta')
        ball = self.canvas.create_image(STARTING_X, STARTING_Y, image=self.bird, anchor=tkinter.NW)

        return ball


    def make_slingshot_back(self):
        slingshot1 = self.canvas.create_image(STARTING_X, STARTING_Y, image=self.slingshot_back_img, anchor=tkinter.NW)
        return slingshot1


    def make_slingshot_front(self):
        slingshot2 = self.canvas.create_image(STARTING_X, STARTING_Y, image=self.slingshot_front_img, anchor=tkinter.NW)
        return slingshot2

    def make_strap(self):
        self.get_ball_coords()
        strap = self.canvas.create_line(STARTING_X+20, STARTING_Y+18, self.ball_coords['b_x1']+5, self.ball_coords['b_y1']+30,
                                        fill = 'brown', width=10)
        return strap

    def make_canvas(self):
        self.top.minsize(WIDTH, HEIGH)
        self.top.title(TITLE)
        canvas = tkinter.Canvas(self.top, width=WIDTH, heigh=HEIGH, highlightthickness=1,
                                highlightbackground="black")
        canvas.pack()
        canvas.create_image(1, 1, image=self.background, anchor=tkinter.NW)
        return canvas

    def make_aim(self):
        self.canvas.create_image(TARGET_X, TARGET_Y, image=self.target, anchor=tkinter.NW)
        return self.canvas.create_rectangle(AIM_X, AIM_Y, AIM_X + AIM_SIZE, AIM_Y + AIM_SIZE, outline="")

    def hit_aim(self):
        print('hit aim')
       # print('ball:', self.ball_coords, 'aim x', AIM_X , 'aim y', AIM_Y)
        self.get_ball_coords()
        # return self.ball_coords['b_x1'] >= AIM_X + 30 \
        #         and self.ball_coords['b_x2'] <= AIM_X + 95 \
        #         and self.ball_coords['b_y1'] >= AIM_Y - 50\
        #         and self.ball_coords['b_y2'] <= AIM_Y +170

        return (self.ball_coords['b_x1'] - 1325)**2 + (self.ball_coords['b_y1'] - 605) ** 2 <=(1325-1213)**2+(610 - 605)**2
        # return self.ball_coords['b_x1'] >= AIM_X - 20 \
        #        and self.ball_coords['b_x2'] <= AIM_X + AIM_SIZE + 20 \
        #        and self.ball_coords['b_y1'] >= AIM_Y - 20 \
        #        and self.ball_coords['b_y2'] <= AIM_Y + AIM_SIZE + 20

    def in_frame(self):
        print('in frame')
        (x1, y1) = self.canvas.coords(self.ball)
        # print(x1, y1, x2, y2)
        return x1 <= WIDTH and x1 >= 0 - BALL_SIZE and y1  < HEIGH and y1 >= 0 - BALL_SIZE

    def x_traectory(self, time):
        '''
            X  = V0 * cos(alpha) * t
            x = STARTING_X + (self.v0 * self.cos_alpha * time)
        '''
        return self.mouse_coordinates['x2'] + (self.v0 * self.cos_alpha * time)


    def x_traectory_back(self, time):
        return self.mouse_coordinates['x2'] - (self.v0 * self.cos_alpha * time)


    def y_traectory(self, time):
        '''
            Y = V0 * sin(alpha) * t - (g * t^2) / 2
            y = (STARTING_Y#-ball size# - BALL_SIZE) - (self.v0 * self.sin_alpha * time - (G * time ** 2) / 2)
        '''
        return self.mouse_coordinates['y2'] - (self.v0 * self.sin_alpha * time - (G * time ** 2) / 2)

    '''
    def finish_canvas(self):
        top = tkinter.Toplevel()
        top.minsize(WIDTH - 200, HEIGH - 100)
        top.title('Score')
        canvas = tkinter.Canvas(top, width = WIDTH - 199, heigh = HEIGH - 99, highlightthickness=1,
                                highlightbackground="black")
        canvas.pack()
        return canvas

    def finish_message(self):
        self.finish_canvas()
        message = self.finish_canvas.create_text(100, 100, text = self.text)
        return message



        def meter(self):
        text = self.canvas.create_text(800, 100, text = self.goals)
        return self.canvas.itemconfig(text, text=self.goals)

    '''

    def meter(self):
        return self.canvas.create_text(800, 100, text=self.goals, fill = 'red', font= ("Purisa", 36, 'bold'))


    def start(self):
        self.mouse_events()
        self.canvas.mainloop()



if __name__ == '__main__':
    bird = AngryBird()
    bird.start()

