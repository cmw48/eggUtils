import sys
import time
import logging
from Tkinter import *

class App:
    def __init__(self, master):
        frame = Frame(master, height="105", width="155", bg="blue")
        frame.pack()
        self.button = Button(frame,
                             text="QUIT", fg="red",
                             height=10, width=30,
                             command=self.end_program)
        self.button.pack(side=LEFT)
        self.mode_default = Button(frame,
                             text="Default Mode",
                             height=10, width=30,
                             command=self.run_program)
        self.mode_default.pack(side=LEFT)
        self.mode_rtctest = Button(frame,
                             text="RTC load",
                             height=10, width=30,
                             command=self.rtc_mode)
        self.mode_rtctest.pack(side=LEFT)

    def run_program(self):
        print("Running default mode!")
        self.opmode = 'default'
        if __name__ == "__main__":
            main()

    def rtc_mode(self):
        print("Running RTC mode!")
        self.opmode = 'RTC'
        if __name__ == "__main__":
            main()


    def end_program(self):
        print("Bye!")
        time.sleep(1)
        root.destroy()


def main():

    #logging.basicConfig(filename='eggtest.log', level=logging.INFO)
    logging.basicConfig(filename='tktest.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)

    logging.info('Started')
    print('Do something cool.')
    print('Do something else')
    logging.error('That was not cool.')
    print(app.opmode)
    print('holy cow this is taking a long time.')
    print('I know, right? Let\'s quit.')
    print('***CLICK START TO RUN AGAIN***')
    return



root = Tk()
app = App(root)
root.mainloop()
