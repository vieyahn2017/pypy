# -*- coding: utf-8 -*-

from datetime import date
from peewee import *
from peewee_test1 import Person, Pet

db = SqliteDatabase('people.db')

"""连接数据库"""
db.connect()


"""-------------------------------------------------------------------------------------------------------"""
uncle_bob = Person(name='Bob', birthday=date(1960, 1, 15), is_relative=True)
uncle_bob.save()

grandma = Person.create(name='Grandma', birthday=date(1935, 3, 1), is_relative=True)
herb = Person.create(name='Herb', birthday=date(1950, 5, 5), is_relative=False)
grandma.name = 'Grandma L.'
grandma.save()  #更新数据库中的grandma的名字

bob_kitty = Pet.create(owner=uncle_bob, name='Kitty', animal_type='cat')
herb_fido = Pet.create(owner=herb, name='Fido', animal_type='dog')
herb_mittens = Pet.create(owner=herb, name='Mittens', animal_type='cat')
herb_mittens_jr = Pet.create(owner=herb, name='Mittens Jr', animal_type='cat')
"""---------------------------------------------------"""
herb_mittens.delete_instance() #删除
""""""
herb_fido.owner = uncle_bob
herb_fido.save()
bob_fido = herb_fido


"""连接数据库关闭"""
db.close()
