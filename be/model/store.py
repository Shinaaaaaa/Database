import sqlite3 as sqlite
import logging
import os
import sqlalchemy
from sqlalchemy import Column, String, create_engine, Integer, Text, DateTime, LargeBinary
# from sqlalchemy.ext.declarative import declarative_base
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, session
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError



class Store:
    database: str

    def __init__(self):
        self.engine = create_engine("postgresql://postgres:737600@127.0.0.1:5432/testdb",
            echo=False,
            pool_size=8, 
            pool_recycle=60*30
        )
        self.DbSession = sessionmaker(bind = self.engine)
        self.session = self.DbSession()
        self.base = declarative_base()


    def get_db_conn(self):
        return self.session
    
    def get_db_engine(self):
        return self.engine

    def get_db_base(self):
        return self.base


database_instance: Store = Store()


Base = database_instance.get_db_base()

class user(Base):
    __tablename__ = 'user'
    user_id = Column(Text, primary_key = True, unique = True, nullable = False)
    password = Column(Text, nullable = False)
    balance = Column(Integer, nullable = False)
    token = Column(Text, nullable = False)
    terminal = Column(Text)

class user_store(Base):
    __tablename__ = 'user_store'
    user_id = Column(Text, primary_key = True, nullable = False)
    store_id = Column(Text, primary_key = True, nullable = False)

class store(Base):
    __tablename__ = 'store'
    store_id = Column(Text, primary_key = True, nullable = False)
    book_id = Column(Text, primary_key = True, nullable = False)
    book_info = Column(Text, nullable = False)
    stock_level = Column(Integer, nullable = False)

class new_order(Base):
    __tablename__ = 'new_order'
    order_id = Column(Text, primary_key = True, unique = True, nullable = False)
    user_id = Column(Text, nullable = False)
    store_id = Column(Text, nullable = False)
    status = Column(Integer, nullable = False)
    create_time = Column(DateTime, nullable = False)

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'user_id': self.user_id,
            'store_id': self.store_id,
            'status': self.status,
            'create_time': self.create_time
        }

class new_order_detail(Base):
    __tablename__ = 'new_order_detail'
    order_id = Column(Text, primary_key = True, nullable = False)
    book_id = Column(Text, primary_key = True, nullable = False)
    count = Column(Integer, nullable = False)
    price = Column(Integer, nullable = False)

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'book_id': self.book_id,
            'count': self.count,
            'price': self.price
        }

class books(Base):
    __tablename__ = 'book'

    id = Column(Text, primary_key=True, unique=True, nullable=False)
    title = Column(Text)
    author = Column(Text)
    publisher = Column(Text)
    original_title = Column(Text)
    translator = Column(Text)
    pub_year = Column(Text)
    pages = Column(Integer)
    price = Column(Integer)
    currency_unit = Column(Text)
    binding = Column(Text)
    isbn = Column(Text)
    author_intro = Column(Text)
    book_intro = Column(Text)
    content = Column(Text)
    tags = Column(Text)
    picture = Column(LargeBinary)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'original_title': self.original_title,
            'translator': self.translator,
            'pub_year': self.pub_year,
            'pages': self.pages,
            'price': self.price,
            'currency_unit': self.currency_unit,
            'binding': self.binding,
            'isbn': self.isbn,
            'author_intro': self.author_intro,
            'book_intro': self.book_intro,
            'content': self.content,
            'tags': self.tags,
            'picture': self.picture
        }

def init_database():
    global database_instance
    database_instance.get_db_base().metadata.drop_all(database_instance.get_db_engine())
    database_instance.get_db_base().metadata.create_all(database_instance.get_db_engine())


def get_db_conn() -> session:
    global database_instance
    return database_instance.get_db_conn()