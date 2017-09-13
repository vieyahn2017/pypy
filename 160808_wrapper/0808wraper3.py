import datetime

def pre_date(pre):
    def date(func):
        def w():
            func()
            date1 = datetime.datetime.now()
            print( pre +str(date1))
        return w
    return date



@pre_date('Today is')
def alan():
    print('alan speaking')

@pre_date('Now that,eh,,,')
def tom():
    print('tom speaking')



tom()

alan()
