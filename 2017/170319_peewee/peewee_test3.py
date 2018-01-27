# -*- coding: utf-8 -*-

from datetime import date
from peewee import *
from peewee_test1 import Person, Pet

db = SqliteDatabase('people.db')

"""连接数据库"""
db.connect()


"""-------------------------------------------------------------------------------------------------------"""

#获取单个数据记录
grandma = Person.select().where(Person.name == 'Grandma L.').get()
"""同上"""
grandma = Person.get(Person.name == 'Grandma L.')
print grandma

#获取数据列表
#"""
for person in Person.select():
    print("人名:",person.name, person.is_relative)

query = Pet.select().where(Pet.animal_type == 'cat')
for pet in query:
    print("宠物名:",pet.name, "主人名:",pet.owner.name)
#"""

#连接查询
"""
query = (Pet.select(Pet, Person)
         .join(Person)
         .where(Pet.animal_type == 'cat'))
for pet in query:
     print(pet.name, pet.owner.name)
"""


#让我们获取Bob拥有的所有宠物
for pet in Pet.select().join(Person).where(Person.name == 'Bob'):
      print(pet.name)

"""同上"""
uncle_bob = Person(name='Bob', birthday=date(1960, 1, 15), is_relative=True)
for pet in Pet.select().where(Pet.owner == uncle_bob).order_by(Pet.name):
      print(pet.name)

#日期排序
for person in Person.select().order_by(Person.birthday.desc()):
     print(person.name, person.birthday)
"""-------------------------------------------------------------------------------------------------------"""
for person in Person.select():
     print(person.name, person.pets.count(), 'pets')
     for pet in person.pets:
          print ('    ', pet.name, pet.animal_type)

"""-------------------------------------------------------------------------------------------------------"""
#日期条件查询
d1940 = date(1940, 1, 1)
d1960 = date(1960, 1, 1)

#查询生日大于1960年，小于1940年
query = (Person.select()
        .where((Person.birthday < d1940) | (Person.birthday > d1960)))
for person in query:
     print(person.name, person.birthday)
#查询生日在1940年与1960年 之间的人
query = (Person
         .select()
        .where((Person.birthday > d1940) & (Person.birthday < d1960)))
for person in query:
    print(person.name, person.birthday)
"""------------------------------------------------------"""
#查询人名,g开头的
expression = (fn.Lower(fn.Substr(Person.name, 1, 1)) == 'g')
for person in Person.select().where(expression):
     print(person.name)



"""连接数据库关闭"""
db.close()
