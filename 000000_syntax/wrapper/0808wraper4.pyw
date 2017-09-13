import datetime

class params:
    def __init__(self):
        print("init called")

    @staticmethod
    def released():
        print("release this class .")
              
def pre_date(cls):
    def date(func):
        def wraper():
            print("before %s ,we called (%s)."  %(func.__name__,cls))
            try:
                func()
                date1 = datetime.datetime.now()
                print(date1)
            finally:
                cls.released()
        return wraper
    return date


@pre_date(params)
def alan():
    print('alan speaking')

@pre_date(params)
def tom():
    print('tom speaking')

tom()
alan()

class foo:
    def __init__(self,func):
        print("init called")
        self.__func=func


    def __call__(self):
        print("be called")
        return self.__func

    @staticmethod
    def released():
        print("release this class .")
        
@foo
def bar():
    print('bar')

bar()

