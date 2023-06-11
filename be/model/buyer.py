import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from be.model.store import *
import pymongo
import datetime
from be.model.user import User
import numpy as np
from sqlalchemy.exc import SQLAlchemyError

class Buyer(db_conn.DBConn):
    def __init__(self, limit = np.inf):
        db_conn.DBConn.__init__(self)
        # self.duration_limit = limit
        self.duration_limit = 10

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id, )
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id, )
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                # result = self.db['store'].find_one({'store_id': store_id, 'book_id': book_id}, {'book_id':1, 'stock_level':1, 'book_info':1})
                result = self.session.query(store).filter(store.store_id == store_id, store.book_id == book_id).first()
                if result is None:
                    return error.error_non_exist_book_id(book_id) + (order_id, )

                # stock_level = result['stock_level']
                # book_info = result['book_info']
                stock_level = result.stock_level
                book_info = result.book_info
                book_info_json = json.loads(book_info)
                price = book_info_json['price']

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # result = self.db['store'].update_many({'store_id': store_id, 'book_id': book_id, 'stock_level': {'$gte': count}}, {'$inc': {'stock_level': -count}})
                result =self.session.query(store).filter(store.store_id == store_id, store.book_id == book_id, store.stock_level >= count).first()

                if result:
                    result.stock_level -= count
                    self.session.add(result)
                    self.session.commit()
                else:
                    return error.error_stock_level_low(book_id) + (order_id, )

                # order_detail = {
                #     "order_id" : uid,
                #     "book_id" : book_id,
                #     "count" : count,
                #     "price" : price
                # }
                # self.db['new_order_detail'].insert_one(order_detail)
                order_detail = new_order_detail(order_id = uid, book_id = book_id, count = count, price = price)
                self.session.add(order_detail)
                self.session.commit()

            # order = {
            #     "order_id" : uid,
            #     "store_id" : store_id,
            #     "user_id" : user_id,
            #     "status" : 0,
            #     "create_time" : datetime.datetime.now()
            # }
            # self.db['new_order'].insert_one(order)
            order = new_order(order_id = uid, user_id = user_id, store_id = store_id, status = 0, create_time = datetime.datetime.now())
            self.session.add(order)
            self.session.commit()
            result = self.session.query(new_order).filter(new_order.order_id == uid).first()
            order_id = uid
        except SQLAlchemyError as e:
            self.session.rollback()
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            print(order_id)
            # result = self.db['new_order'].find_one({'order_id': order_id}, {'order_id':1, 'user_id':1, 'store_id':1, 'status':1, 'create_time':1})
            result = self.session.query(new_order).filter(new_order.order_id == order_id).first()
            if result is None:
                return error.error_invalid_order_id(order_id)

            if result.status != 0:
                return 534, "order process error"
            duration = (datetime.datetime.now() - result.create_time).total_seconds()
            if duration > self.duration_limit:
                store_id = result.store_id
                # booklist = self.db['new_order_detail'].find({'order_id': order_id}, {'book_id':1, 'count':1, 'price':1})
                booklist = self.session.query(new_order_detail).filter(new_order_detail.order_id == order_id)
                for row in booklist:
                    book_id = row.book_id
                    count = row.count
                    # bookresult = self.db['store'].update_one({'store_id': store_id, 'book_id': book_id}, {'$inc': {'stock_level': count}})
                    bookresult = self.session.query(store).filter(store.store_id == store_id, store.book_id == book_id).first()
                    if bookresult:
                        bookresult.stock_level += count
                        self.session.add(bookresult)
                        self.session.commit()
                    else:
                        return 536, "invalid store_id and book_id"
                # self.db['new_order'].update_one({'order_id': order_id}, {'$set': {'status': 4}})
                order = self.session.query(new_order).filter(new_order.order_id == order_id).fisrt()
                if order:
                    order.status = 4
                    self.session.add(order)
                    self.session.commit()
                return 534, "order process error"
            order_id = result.order_id
            buyer_id = result.user_id
            store_id = result.store_id

            if buyer_id != user_id:
                return error.error_authorization_fail()

            # result = self.db['user'].find_one({'user_id': buyer_id}, {'balance':1, 'password':1})
            result = self.session.query(user).filter(user.user_id == buyer_id).first()
            if result is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = result.balance
            if password != result.password:
                return error.error_authorization_fail()

            # result = self.db['user_store'].find_one({'store_id': store_id}, {'store_id':1, 'user_id':1})
            result = self.session.query(user_store).filter(user_store.store_id == store_id).first()
            if result is None:
                return error.error_non_exist_store_id(store_id)
            seller_id = result.user_id

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # result = self.db['new_order_detail'].find({'order_id': order_id}, {'book_id':1, 'count':1, 'price':1})
            result = self.session.query(new_order_detail).filter(new_order_detail.order_id == order_id)
            total_price = 0
            for row in result:
                count = row.count
                price = row.price
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            # result = self.db['user'].update_one({'user_id': buyer_id, 'balance': {'$gte': total_price}}, {'$inc': {'balance': -total_price}})
            result = self.session.query(user).filter(user.user_id == buyer_id, user.balance >= total_price).first()
            if result:
                result.balance -= total_price
                self.session.add(result)
                self.session.commit()
            else:
                return error.error_not_sufficient_funds(order_id)
            # result = self.db['user'].update_one({'user_id': seller_id}, {'$inc': {'balance': total_price}})
            result = self.session.query(user).filter(user.user_id == seller_id).first()
            if result:
                result.balance += total_price
                self.session.add(result)
                self.session.commit()
            else:
                return error.error_non_exist_user_id(seller_id)
            
            # result = self.db['new_order'].update_one({'order_id': order_id}, {'$set': {'status': 1}})
            result = self.session.query(new_order).filter(new_order.order_id == order_id).first()
            if result:
                result.status = 1
                self.session.add(result)
                self.session.commit()
            else:
                return error.error_invalid_order_id(order_id)

            # result = self.db['new_order'].delete_one({'order_id': order_id})
            # if result.deleted_count == 0:
            #     return error.error_invalid_order_id(order_id)

            # result = self.db['new_order_detail'].delete_many({'order_id': order_id})
            # if result.deleted_count == 0:
            #     return error.error_invalid_order_id(order_id)

        except SQLAlchemyError as e:
            self.session.rollback()
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            # result = self.db['user'].find_one({'user_id': user_id}, {'password':1})
            result = self.session.query(user).filter(user.user_id == user_id).first()
            if result is None:
                return error.error_authorization_fail()

            if result.password != password:
                return error.error_authorization_fail()

            # result = self.db['user'].update_one({'user_id': user_id}, {'$inc': {'balance': add_value}})
            result = self.session.query(user).filter(user.user_id == user_id).first()
            if result:
                result.balance += add_value
                self.session.add(result)
                self.session.commit()
            else:
                return error.error_non_exist_user_id(user_id)
        except SQLAlchemyError as e:
            self.session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def send_out_delivery(self, user_id, store_id, order_id) -> (int, str):
        try:
            # result = self.db['new_order'].find_one({'order_id': order_id}, {'store_id':1, 'status':1})
            result = self.session.query(new_order).filter(new_order.order_id == order_id).first()
            if result is None:
                return error.error_invalid_order_id(order_id)
            
            if store_id != result.store_id:
                return 531, "order mismatch(store)"
            if result.status != 1:
                return 534, "order process error"
            
            # result = self.db['user_store'].find_one({'user_id': user_id, 'store_id': store_id})
            result = self.session.query(user_store).filter(user_store.user_id == user_id, user_store.store_id == store_id).first()
            if result is None:
                return 532, "order mismatch(seller)"
            
            # result = self.db['new_order'].update_one({'order_id': order_id}, {'$set': {'status': 2}})
            result = self.session.query(new_order).filter(new_order.order_id == order_id).first()
            if result:
                result.status = 2
                self.session.add(result)
                self.session.commit()
            else:
                return error.error_invalid_order_id(order_id)
        except SQLAlchemyError as e:
            self.session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
    
    def take_delivery(self, user_id, token, order_id) -> (int, str):
        try:
            code, message = User().check_token(user_id, token)
            if code != 200:
                return code, message
            
            # result = self.db['new_order'].find_one({'order_id': order_id}, {'user_id':1, 'status':1})
            result = self.session.query(new_order).filter(new_order.order_id == order_id).first()
            if result is None:
                return error.error_invalid_order_id(order_id)
            
            if user_id != result.user_id:
                return 533, "order mismatch(buyer)"
            if result.status != 2:
                return 534, "order process error"
            
            # result = self.db['new_order'].update_one({'order_id': order_id}, {'$set': {'status': 3}})
            result = self.session.query(new_order).filter(new_order.order_id == order_id).first()
            if result:
                result.status = 3
                self.session.add(result)
                self.session.commit()
            else:
                return error.error_invalid_order_id(order_id)
        except SQLAlchemyError as e:
            self.session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def order_cancel(self, user_id, token, order_id) -> (int, str):
        try:
            code, message = User().check_token(user_id, token)
            if code != 200:
                return code, message
            
            # result = self.db['new_order'].find_one({'order_id': order_id}, {'user_id':1, 'store_id':1, 'status':1})
            result = self.session.query(new_order).filter(new_order.order_id == order_id).first()
            if result is None:
                return error.error_invalid_order_id(order_id)
            
            if user_id != result.user_id:
                return 533, "order mismatch(buyer)"
            if result.status > 1:
                return 535, "order cancellation failed"
            
            store_id = result.store_id
            total_price = 0
            # booklist = self.db['new_order_detail'].find({'order_id': order_id}, {'book_id':1, 'count':1, 'price':1})
            booklist = self.session.query(new_order_detail).filter(new_order_detail.order_id == order_id)
            for row in booklist:
                book_id = row.book_id
                count = row.count
                price = row.price
                # bookresult = self.db['store'].update_one({'store_id': store_id, 'book_id': book_id}, {'$inc': {'stock_level': count}})
                bookresult = self.session.query(store).filter(store.store_id == store_id, store.book_id == book_id).first()
                if bookresult:
                    bookresult.stock_level += count
                    self.session.add(bookresult)
                    self.session.commit()
                else:
                    return 536, "invalid store_id and book_id"
                total_price = total_price + count * price

            # storeresult = self.db['user_store'].find_one({'store_id': store_id}, {'user_id':1})
            storeresult = self.session.query(user_store).filter(user_store.store_id == store_id).first()
            if storeresult is None:
                return error.error_non_exist_store_id(store_id)
            
            seller_id = storeresult.user_id
            if result.status == 1:
                # userresult = self.db['user'].update_one({'user_id': user_id}, {'$inc': {'balance': total_price}})
                userresult = self.session.query(user).filter(user.user_id == user_id).first()
                if userresult:
                    userresult.balance += total_price
                    self.session.add(userresult)
                    self.session.commit()
                else:
                    return error.error_non_exist_user_id(user_id)
                # userresult = self.db['user'].update_one({'user_id': seller_id}, {'$inc': {'balance': -total_price}})
                userresult = self.session.query(user).filter(user.user_id == seller_id).first()
                if userresult:
                    userresult.balance -= total_price
                    self.session.add(userresult)
                    self.session.commit()
                else:
                    return error.error_non_exist_user_id(user_id)
            
            # self.db['new_order'].update_one({'order_id': order_id}, {'$set': {'status': 4}})
            result = self.session.query(new_order).filter(new_order.order_id == order_id).first()
            if result:
                result.status = 4
                self.session.add(result)
                self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
    
    def order_query(self, user_id, token) -> (int, str, list):
        try:
            code, message = User().check_token(user_id, token)
            if code != 200:
                return code, message, ""
            
            orders = []
            # result = self.db['new_order'].find({'user_id': user_id}, {'_id':0})
            result = self.session.query(new_order).filter(new_order.user_id == user_id)
            for order in result:
                order_details = []
                order_id = order.order_id
                store_id = order.store_id
                # booklist = self.db['new_order_detail'].find({'order_id': order_id}, {'_id':0})
                booklist = self.session.query(new_order_detail).filter(new_order_detail.order_id == order_id)
                duration = (datetime.datetime.now() - order.create_time).total_seconds()
                for row in booklist:
                    book_id = row.book_id
                    count = row.count
                    if order.status <= 1 and duration > self.duration_limit:
                        # bookresult = self.db['store'].update_one({'store_id': store_id, 'book_id': book_id}, {'$inc': {'stock_level': count}})
                        bookresult = self.session.query(store).filter(store.store_id == store_id, store.book_id == book_id).first()
                        if bookresult:
                            bookresult.stock_level += count
                            self.session.add(userresult)
                            self.session.commit()
                        else:
                            return 536, "invalid store_id and book_id", ""
                    order_details.append(row.to_dict())

                if order.status <= 1 and duration > self.duration_limit:
                    # self.db['new_order'].update_one({'order_id': order_id}, {'$set': {'status': 4}})
                    result = self.session.query(new_order).filter(new_order.order_id == order_id).first()
                    result.status = 4;
                    self.session.add(userresult)
                    self.session.commit()
                    order.status = 4
                order.order_details = order_details
                orders.append(order.to_dict())
        except SQLAlchemyError as e:
            self.session.rollback()
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", orders