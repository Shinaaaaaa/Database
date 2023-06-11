import sqlite3 as sqlite
from be.model import error
from be.model import db_conn
from be.model.store import *
from sqlalchemy.exc import SQLAlchemyError


class Seller(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)
            ###
            if not self.is_my_store(user_id, store_id):
                return error.error_not_my_store(user_id, store_id)
            ###
            # new_book = {
            #     "store_id" : store_id,
            #     "book_id" : book_id,
            #     "book_info": book_json_str,
            #     "stock_level": stock_level
            # }
            # result = self.db['store'].insert_one(new_book)
            new_book = store(store_id = store_id, book_id = book_id, book_info = book_json_str, stock_level = stock_level)
            self.session.add(new_book)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)
            ###
            if not self.is_my_store(user_id, store_id):
                return error.error_not_my_store(user_id, store_id)
            ###
            # self.db['store'].update_one({'store_id': store_id, 'book_id': book_id}, {'$inc': {'stock_level': add_stock_level}})
            result = self.session.query(store).filter(store.store_id == store_id, store.book_id == book_id).first()
            if result:
                result.stock_level += add_stock_level
                self.session.add(result)
                self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            
            # new_store = {
            #     "store_id" : store_id,
            #     "user_id" : user_id
            # }
            # self.db['user_store'].insert_one(new_store)
            new_store = user_store(store_id = store_id, user_id = user_id)
            self.session.add(new_store)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
