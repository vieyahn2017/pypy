import datetime

def date(func):
    def w():
        func()
        date1 = datetime.datetime.now()
        print(date1)
    return w

"""
def alan():
    print('alan speaking')

def tom():
    print('tom speaking')


tom=date(tom)
tom()

alan=date(alan)
alan()
"""

@date
def alan():
    print('alan speaking')

@date
def tom():
    print('tom speaking')



tom()

alan()
