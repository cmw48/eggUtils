class Egg:

    def __init__(self, serial):
        self.serial = serial

    def introduce(self):
        print('Hello, I am {0}, and my name is {1}'.format(self, self.serial))


myegg = Egg("egg0080huey")
otheregg = Egg("egg0080louie")
myegg.introduce()
otheregg.introduce()
