from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfile
from PIL import Image as Img
from PIL import ImageGrab, ImageTk
import cv2
import io
import dream
import numpy as np


class Paint(object):





    def __init__(self):

        self.DEFAULT_PEN_SIZE = 5.0
        self.DREAM_COLOR = 'aquamarine'
        self.DREAM_RGB = (127, 255, 212)
        self.NIGHTMARE_COLOR = 'VioletRed'
        self.NIGHTMARE_RGB = (208, 32, 144)

        self.WIDTH = 600
        self.HEIGHT = 600

        self.root = Tk()
        self.root.title('Dream Painter')
        self.dreaming = False
        self.run_dream = False
        self.dream_button = Button(self.root, text='dream', command=self.use_dream)
        self.dream_button.grid(row=0, column=0)

        self.nightmare_button = Button(self.root, text='nightmare', command=self.use_nigthmare)
        self.nightmare_button.grid(row=0, column=1)

        self.choose_size_button = Scale(self.root, from_=1, to=100, orient=HORIZONTAL)
        self.choose_size_button.set(50)
        self.choose_size_button.grid(row=0, column=2)

        self.choose_img = Button(self.root, text='image',command=self.get_image)
        self.choose_img.grid(row=0,column=3)

        self.run_button = Button(self.root, text='run', command=self.dream)
        self.run_button.grid(row=0, column=4)

        self.save_button = Button(self.root,text='save',command=self.save)
        self.save_button.grid(row=0,column=5)

        self.c = Canvas(self.root, bg='white', width=self.WIDTH, height=self.HEIGHT)
        self.c.grid(row=1, columnspan=5)

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = self.choose_size_button.get()
        self.eraser_on = False
        self.active_button = self.dream_button
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)

    def save(self):
        self.activate_button(self.save_button)
        filename = asksaveasfile()
        ps = self.c.postscript(colormode='color')
        img = Img.open(io.BytesIO(ps.encode('utf-8')))
        print(img)

        img.save(filename.name)




    def use_dream(self):
        self.activate_button(self.dream_button)
        self.dreaming = True
    def use_nigthmare(self):
        self.activate_button(self.nightmare_button)
        self.dreaming = False

    def get_image(self):
        filename = askopenfilename()
        img = cv2.imread(filename)
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        img = cv2.resize(img,(self.WIDTH,self.HEIGHT))
        self.inverted_img = dream.deprocess(img)
        img = Img.fromarray(img)
        self.saved_img = img
        img = ImageTk.PhotoImage(img)
        self.c.delete('all')
        self.c.create_image(0, 0, anchor=NW, image=img)
        self.c.img = img


    def dream(self):

        ps = self.c.postscript(colormode='color')
        img = Img.open(io.BytesIO(ps.encode('utf-8')))
        img = np.array(img)
        final = np.zeros(img.shape)
        N, M, C = final.shape
        if self.run_dream:
            drm = dream.run(self.saved_img,['mixed3','mixed5'],100,0.01)
            drm = np.array(drm)
            for i in range(N):
                for j in range(M):
                    if self.is_color(img[i,j],True):
                        final[i,j] = drm[i,j]
                    elif self.is_color(img[i,j],False):
                        final[i,j] = self.inverted_img[i,j]
                    else:
                        final[i,j] = img[i,j]
        else:
            for i in range(N):
                for j in range(M):
                    if self.is_color(img[i, j],False):
                        final[i, j] = self.inverted_img[i, j]
                    else:
                        final[i, j] = img[i, j]

        final = ImageTk.PhotoImage(Img.fromarray(final.astype(np.uint8)))
        self.c.create_image(0, 0, anchor=NW, image=final)
        self.c.img = final

    def is_color(self,row,dream):
        if dream:
            return (row[0],row[1],row[2]) == self.DREAM_RGB
        else:
            return (row[0],row[1],row[2]) == self.NIGHTMARE_RGB

    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def paint(self, event):
        self.line_width = self.choose_size_button.get()
        paint_color = self.DREAM_COLOR if self.dreaming else self.NIGHTMARE_COLOR
        if paint_color == self.DREAM_COLOR:
            self.run_dream = True
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x, self.old_y = None, None


if __name__ == '__main__':
    Paint()