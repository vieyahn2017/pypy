def addOne(func):
    def wapr(*args,**kwargs):
        saySth="result:"
        return saySth+ " "+str(func(*args,**kwargs))
    return wapr

@addOne
def func(a,b):
    return a+b


print(func(10,20))
