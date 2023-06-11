import datetime
from be.model.buyer import Buyer
from be.model.store import *

def regular_inspection():
    b = Buyer()
    # result = b.db['new_order'].find({'status': 0}, {'order_id':1, 'store_id':1, 'create_time':1})
    result = b.session.query(new_order).filter(new_order.status == 0)
    for row in result:
        order_id = row.order_id
        duration = (datetime.datetime.now() - row.create_time).total_seconds()
        if duration > b.duration_limit:
            store_id = row.store_id
            # booklist = b.db['new_order_detail'].find({'order_id': order_id}, {'book_id':1, 'count':1})
            booklist = b.session.query(new_order_detail).filter(new_order_detail.order_id == order_id)
            for row in booklist:
                book_id = row.book_id
                count = row.count
                # b.db['store'].update_one({'store_id': store_id, 'book_id': book_id}, {'$inc': {'stock_level': count}})
                result = b.session.query(store).filter(store.store_id == store_id, store.book_id == book_id).first()
                if result:
                    result.stock_level += count
                    b.session.add(result)
                    b.session.commit()
            # b.db['new_order'].update_one({'order_id': order_id}, {'$set': {'status': 4}})
            result = b.session.query(new_order).filter(new_order.order_id == order_id).first()
            result.status = 4
            b.session.add(result)
            b.session.commit()
