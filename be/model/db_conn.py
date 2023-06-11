# from be.model import store
from be.model.store import *

class DBConn:
    def __init__(self):
        self.session = get_db_conn()

    def user_id_exist(self, user_id):
        # result = self.db['user'].find_one({'user_id': user_id})
        result = self.session.query(user).filter(user.user_id == user_id).first()
        if result:
            return True
        else:
            return False

    def is_my_store(self, user_id, store_id):
        # result = self.db['user_store'].find_one({'user_id': user_id, 'store_id': store_id})
        result = self.session.query(user_store).filter(user_store.user_id == user_id, user_store.store_id == store_id).first()
        if result:
            return True
        else:
            return False

    def book_id_exist(self, store_id, book_id):
        # result = self.db['store'].find_one({'store_id': store_id, 'book_id': book_id})
        result = self.session.query(store).filter(store.store_id == store_id, store.book_id == book_id).first()
        if result:
            return True
        else:
            return False
    
    def store_id_exist(self, store_id):
        # result = self.db['user_store'].find_one({'store_id': store_id})
        result = self.session.query(user_store).filter(user_store.store_id == store_id).first()
        if result:
            return True
        else:
            return False
