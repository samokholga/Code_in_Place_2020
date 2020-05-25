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
        self.slingshot_back2_img = ImageTk.PhotoImage(file="pics/Rogatka_right2.png")
        self.slingshot_front_img = ImageTk.PhotoImage(file="pics/Rogatka_left.png")
        self.mouse_coordinates = {}
        self.v0 = None
        self.sin_alpha = None
        self.cos_alpha = None
        self.goals = 0
        self.ball_coords = {}
        self.canvas = self.make_canvas()
        self.aim = self.make_aim()
        self.slingshot_back = self.make_slingshot_back()
        self.strap_back = self.make_strap_back()
        self.ball = self.make_ball()
        self.slingshot_front = self.make_slingshot_front()
        self.strap = self.make_strap()
        self.text = self.meter()


    '''
    Defining mouse events that will be used in the program:
    -left button click
    -left button hold and move
    -left button release
    '''
    def mouse_events(self):
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<ButtonRelease-1>', self.on_click_release)
        self.canvas.bind('<Motion>', self.motion)

    '''
    Getting coordinates of mouse motion
    '''
    def motion(self, event):
        self.x_motion = event.x - BALL_SIZE / 2
        self.y_motion = event.y - BALL_SIZE / 2

    '''
    Defining program's response on left click:
    - getting x,y - coordinates of click
    - if the bird is on starting position, then follow mouse
    - if the bird's finished the flight (out of frame or in the target),
    then get it back to slingshot
    -  
    '''
    def on_click(self, event):
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
        self.is_clicked_on_ball = False


    '''
    On click release
     - the program updates the image of slingshot, strap cant't stretch any more to follow the bird
     - if the click was on the mouse then we add button release coordinates to the coordinates dictionary,
     use it to calculate the angle of throw and v0, then throe the bird     
    '''
    def on_click_release(self, event):
        self.mouse_pressed = False
        self.canvas.coords(self.strap, STARTING_X + 20, STARTING_Y + 18, STARTING_X + 5, STARTING_Y + 30)
        self.canvas.itemconfig(self.slingshot_back, image=self.slingshot_back_img)
        self.canvas.coords(self.strap_back, STARTING_X - 4000, STARTING_Y + 1200, STARTING_X - 4000, STARTING_Y + 1200)
        if self.is_clicked_on_ball:
            self.mouse_coordinates['x2'] = event.x
            self.mouse_coordinates['y2'] = event.y
            self.get_starting_coodrinates()
            self.throw_the_ball()

    '''
    Adds bird's coordinates to the dictionary
    '''
    def get_ball_coords(self):
        ball_coords_list = self.canvas.coords(self.ball)
        self.ball_coords['b_x1'] = ball_coords_list[0]
        self.ball_coords['b_x2'] = ball_coords_list[0] + BALL_SIZE
        self.ball_coords['b_y1'] = ball_coords_list[1]
        self.ball_coords['b_y2'] = ball_coords_list[1] + BALL_SIZE

    '''
    Checks if cursor is on the bird
    '''
    def mouse_is_on_the_ball(self):
        self.get_ball_coords()
        return self.mouse_coordinates['x1'] <= self.ball_coords['b_x2'] and \
               self.mouse_coordinates['x1'] >= self.ball_coords['b_x1'] and \
               self.mouse_coordinates['y1'] <= self.ball_coords['b_y2'] and \
               self.mouse_coordinates['y1'] >= self.ball_coords['b_y1']

    '''
    Calculates angle of the throw and the speed based on mouse release coodrinates
    '''
    def get_starting_coodrinates(self):
        x1 = STARTING_X
        x2 = self.mouse_coordinates['x2']
        y1 = STARTING_Y
        y2 = self.mouse_coordinates['y2']
        self.v0 = self.velocity(x1, y1, x2, y2)
        self.sin_alpha = self.sin_a(x1, y1, x2, y2)
        self.cos_alpha = self.cos_a(x1, y1, x2, y2)

    '''
    Animate the bird and slingshot strap to follow the cursor
    '''
    def follow_mouse(self):
        self.canvas.itemconfig(self.slingshot_back, image=self.slingshot_back2_img)
        if self.mouse_is_on_the_ball():
            while self.mouse_pressed:
                x = self.x_motion
                y = self.y_motion
                self.canvas.moveto(self.ball, x, y)
                self.canvas.coords(self.strap, STARTING_X+20, STARTING_Y+18, x+5, y+30)
                self.canvas.coords(self.strap_back, STARTING_X+40, STARTING_Y+12, x+45, y+20)
                self.canvas.update()
                time.sleep(1 / 50)

    '''
    Animate the bird's flight after being released from slingshot and change the score
    '''
    def throw_the_ball(self):
        len_of_flight = 0
        while self.in_frame():
            if self.hit_aim():
                self.goals += 1
                self.canvas.itemconfig(self.text, text=self.goals)
                self.get_ball_coords()
                break
            else:
                x = self.x_traectory(len_of_flight)
                y = self.y_traectory(len_of_flight)
                self.canvas.moveto(self.ball, x, y)
                len_of_flight += 1
            self.canvas.update()
            time.sleep(1 / 50)

    '''
    Calculate the starting velocity proportional to the strength of the throw, 
     we'll define it as root(x^2 + y^2) * coeffitient
    '''
    def velocity(self, x1, y1, x2, y2):
        return (((y2 - y1) ** 2 + (x1 - x2) ** 2) ** 0.5) * 0.07

    '''
      Calculate sin of throwing angle based on cursor released coordinates and starting position.
      Makes v0 equal to hypotenuse of our triangle and sin = opposite / hypotenuse
    '''
    def sin_a(self, x1, y1, x2, y2):
        return (y2 - y1) / ((y2 - y1) ** 2 + (x1 - x2) ** 2) ** 0.5

    '''
      Calculate the cos of throwing angle based on cursor released coordinates and starting position
    '''
    def cos_a(self, x1, y1, x2, y2):
        return (x1 - x2) / ((y2 - y1) ** 2 + (x1 - x2) ** 2) ** 0.5

    '''
    create the bird
    '''
    def make_ball(self):
        ball = self.canvas.create_image(STARTING_X, STARTING_Y, image=self.bird, anchor=tkinter.NW)
        return ball

    '''
    create the slingshot's back part (with a strap)
    '''
    def make_slingshot_back(self):
        slingshot1 = self.canvas.create_image(STARTING_X, STARTING_Y, image=self.slingshot_back_img, anchor=tkinter.NW)
        return slingshot1

    '''
    create the slingshot's front part (with a strap)
    '''
    def make_slingshot_front(self):
        slingshot2 = self.canvas.create_image(STARTING_X, STARTING_Y, image=self.slingshot_front_img, anchor=tkinter.NW)
        return slingshot2

    '''
    create the strap that is used in animation 
    '''
    def make_strap(self):
        self.get_ball_coords()
        strap = self.canvas.create_line(STARTING_X+20, STARTING_Y+18, self.ball_coords['b_x1']+5, self.ball_coords['b_y1']+30,
                                        fill = '#69402c', width=9)
        return strap

    def make_strap_back(self):
        #self.get_ball_coords()
        strap = self.canvas.create_line(STARTING_X+40, STARTING_Y+12, STARTING_X+40, STARTING_Y+12,
                                        fill='#69402c', width=6) #self.ball_coords['b_x1'] + 5, self.ball_coords['b_y1'] + 30
        return strap

    '''
    Makes canvas and adds a background image
    '''
    def make_canvas(self):
        self.top.minsize(WIDTH, HEIGH)
        self.top.title(TITLE)
        canvas = tkinter.Canvas(self.top, width=WIDTH, heigh=HEIGH, highlightthickness=1,
                                highlightbackground="black")
        canvas.pack()
        canvas.create_image(1, 1, image=self.background, anchor=tkinter.NW)
        return canvas

    '''
    Makes a target
    '''
    def make_aim(self):
        self.canvas.create_image(TARGET_X, TARGET_Y, image=self.target, anchor=tkinter.NW)
        return self.canvas.create_rectangle(AIM_X, AIM_Y, AIM_X + AIM_SIZE, AIM_Y + AIM_SIZE, outline="")

    '''
    Checks if the bird's hit the target
    '''
    def hit_aim(self):
        self.get_ball_coords()
        return (self.ball_coords['b_x1'] - 1325)**2 + (self.ball_coords['b_y1'] - 605) ** 2 <=(1325-1213)**2+(610 - 605)**2

    '''
    Checks if the bird's still on canvas
    '''
    def in_frame(self):
        (x1, y1) = self.canvas.coords(self.ball)
        return x1 <= WIDTH and x1 >= 0 - BALL_SIZE and y1  < HEIGH and y1 >= 0 - BALL_SIZE

    '''
    Return x - coordinate of the flight's trajectory
         x = starting position + (v0 * cos_alpha * time)
     '''
    def x_traectory(self, time):
         return self.mouse_coordinates['x2'] + (self.v0 * self.cos_alpha * time)

    '''
    Return x - coordinate of the flight's trajectory
        y = starting position - (v0 * sin_alpha * time - (G * time ^ 2) / 2)
    '''
    def y_traectory(self, time):
        return self.mouse_coordinates['y2'] - (self.v0 * self.sin_alpha * time - (G * time ** 2) / 2)

    '''
    Shows the score
    '''
    def meter(self):
        return self.canvas.create_text(800, 100, text=self.goals, fill = 'red', font= ("Purisa", 36, 'bold'))

    '''
    Runs the functions in the correct order
    '''
    def start(self):
        self.mouse_events()
        self.canvas.mainloop()



if __name__ == '__main__':
    bird = AngryBird()
    bird.start()

