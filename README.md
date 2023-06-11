# BookStore Report


## DataBase Design
![](ER.png)

- user

|user_id|password|balance|token|terminal|
|---|---|---|---|---|

```python
class user(Base):
    __tablename__ = 'user'
    user_id = Column(Text, primary_key = True, unique = True, nullable = False)
    password = Column(Text, nullable = False)
    balance = Column(Integer, nullable = False)
    token = Column(Text, nullable = False)
    terminal = Column(Text)
```

- store:

|store_id|book_id|book_info|stock_level|
|---|---|---|---|

```python
class store(Base):
    __tablename__ = 'store'
    store_id = Column(Text, primary_key = True, nullable = False)
    book_id = Column(Text, primary_key = True, nullable = False)
    book_info = Column(Text, nullable = False)
    stock_level = Column(Integer, nullable = False)
```

- book:

|_id|id|title|author|publisher|originate_title|translator|pub_year|pages|price|currency_unit|binding|isbn|author_intro|book_intro|book_intro|content|tags|picture|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

- user_store:

|user_id|store_id|
|---|---|

```python
class user_store(Base):
    __tablename__ = 'user_store'
    user_id = Column(Text, primary_key = True, nullable = False)
    store_id = Column(Text, primary_key = True, nullable = False)
```

- new_order:

|order_id|user_id|store_id|status|create_time|
|---|---|---|---|---|

```python
class new_order(Base):
    __tablename__ = 'new_order'
    order_id = Column(Text, primary_key = True, unique = True, nullable = False)
    user_id = Column(Text, nullable = False)
    store_id = Column(Text, nullable = False)
    status = Column(Integer, nullable = False)
    create_time = Column(DateTime, nullable = False)
```

- new_order_detail:

| order_id |book_id|count|price|
|----------|---|---|---|

```python
class new_order_detail(Base):
    __tablename__ = 'new_order_detail'
    order_id = Column(Text, primary_key = True, nullable = False)
    book_id = Column(Text, primary_key = True, nullable = False)
    count = Column(Integer, nullable = False)
    price = Column(Integer, nullable = False)
```


## Details
### Base 60%
Use sqlalchemy to implement the backend logic (Only show the Important Parts)

- user.py
  - register

    Add a new info of user into the database "user"
    ```python
    new_user = user(user_id = user_id, password = password, balance = 0, token = token, terminal = terminal)
    self.session.add(new_user)
    self.session.commit()
    ```

  - check_password

    Find the password of the user in the database and check whether it matches 
    ```python
    result = self.session.query(user).filter(user.user_id == user_id).first()
    ```
  
  - login

    Invoke check_password to check the user's password and update the token in the database to store the timestamp of the time when the user login
    ```python
    result = self.session.query(user).filter(user.user_id == user_id).first()
    ```

  - logout

    Update the token in the database (dummy_token)

    If the duration has been more than 3,600 s, the user will logout automatically
    ```python
    result = self.session.query(user).filter(user.user_id == user_id).first()
    ```
  
  - unregister

    Delete the infomation of the user from the database
    ```python
    result = self.session.query(user).filter(user.user_id == user_id).first()
    ```
  
  - change_password

    Fisrt, invoke check_password to check the user's password and then updata the new password in the database
    ```python
    result = self.session.query(user).filter(user.user_id == user_id).first()
    if result:
        result.password = new_password
        result.token = token
        result.terminal = terminal
        self.session.add(result)
        self.session.commit()
    else:
        return error.error_authorization_fail()
    ```

- buyer.py
  - new_order

    Fisrt, check the whether the bookstore and the book exist

    Then, check the stock_level of the book

    Update the new stock_level and create a new order in the database
  

    ```python
    order_detail = new_order_detail(order_id = uid, book_id = book_id, count = count, price = price)
    self.session.add(order_detail)
    self.session.commit()
    ```
  - payment
    
    First, cheak the user's password and the order id

    Then check the balance of the user

    If the balance is enough, then update the status of order to paid and the new balance of the user in the database.

    ```python
    // some code
    
    bookresult = self.session.query(store).filter(store.store_id == store_id, store.book_id == book_id).first()
    if bookresult:
        bookresult.stock_level += count
        self.session.add(bookresult)
        self.session.commit()
    else:
        return 536, "invalid store_id and book_id"
    
    // some code
    
    result = self.session.query(user).filter(user.user_id == buyer_id, user.balance >= total_price).first()
    if result:
        result.balance -= total_price
        self.session.add(result)
        self.session.commit()
    else:
        return error.error_not_sufficient_funds(order_id)

    result = self.session.query(user).filter(user.user_id == seller_id).first()
    if result:
        result.balance += total_price
        self.session.add(result)
        self.session.commit()
    else:
        return error.error_non_exist_user_id(seller_id)

    result = self.session.query(new_order).filter(new_order.order_id == order_id).first()
    if result:
        result.status = 1
        self.session.add(result)
        self.session.commit()
    else:
        return error.error_invalid_order_id(order_id)
    
    ```

  - add_funds

    First, cheak the password of the user. Then update the balance.
    ```python
    result = self.session.query(user).filter(user.user_id == user_id).first()
    if result:
        result.balance += add_value
        self.session.add(result)
        self.session.commit()
    else:
        return error.error_non_exist_user_id(user_id)
    ```

- seller.py
  - add_book

    Check the store_id and book_id and update the info of book in the database
    ```python
    new_book = store(store_id = store_id, book_id = book_id, book_info = book_json_str, stock_level = stock_level)
    self.session.add(new_book)
    self.session.commit()
    ```

  - add_stock_level

    Check the store_id and book_id and update the stock_level of book in the database
    ```python
    result = self.session.query(store).filter(store.store_id == store_id, store.book_id == book_id).first()
    if result:
        result.stock_level += add_stock_level
        self.session.add(result)
        self.session.commit()
    ```

  - create_store

    Check the store_id and add a new info of store in the database.
    ```python
    new_store = user_store(store_id = store_id, user_id = user_id)
    self.session.add(new_store)
    self.session.commit()
    ```

- store.py
  - init_tables

    Init the database (create the table)
    ```python
    def __init__(self):
    self.engine = create_engine("postgresql://postgres:737600@127.0.0.1:5432/testdb",
        echo=False,
        pool_size=8, 
        pool_recycle=60*30
    )
    self.DbSession = sessionmaker(bind = self.engine)
    self.session = self.DbSession()
    self.base = declarative_base()
    ```
  
- db_coon.py

  Some utils to check whether the _id exists
  - user_id_exist && book_id_exist && store_id_exist
    ```python
    def user_id_exist(self, user_id):
        result = self.session.query(user).filter(user.user_id == user_id).first()
        if result:
            return True
        else:
            return False

    def is_my_store(self, user_id, store_id):
        result = self.session.query(user_store).filter(user_store.user_id == user_id, user_store.store_id == store_id).first()
        if result:
            return True
        else:
            return False

    def book_id_exist(self, store_id, book_id):book_id})
        result = self.session.query(store).filter(store.store_id == store_id, store.book_id == book_id).first()
        if result:
            return True
        else:
            return False
    
    def store_id_exist(self, store_id):
        result = self.session.query(user_store).filter(user_store.store_id == store_id).first()
        if result:
            return True
        else:
            return False
    ```

### Addition 40%
#### Delivery
- buyer.py
  - send_out_delivery
    
    First check the _order_id_ and _user_id_

    Then update the status of the order (status = 2)
    ```python
    result = self.session.query(new_order).filter(new_order.order_id == order_id).first()
    if result:
        result.status = 2
        self.session.add(result)
        self.session.commit()
    else:
        return error.error_invalid_order_id(order_id)
    ```

  - take_delivery

    First check the _order_id_ and _user_id_

    Then update the status of the order (status = 3)
    ```python
    result = self.session.query(new_order).filter(new_order.order_id == order_id).first()
    if result:
        result.status = 3
        self.session.add(result)
        self.session.commit()
    else:
        return error.error_invalid_order_id(order_id)
    ```

#### Search Book
- create book table

  First, we will create a new table of book (PostgreSQL) to store the infomation of all book(by using the addbook.py)

- user.py
  - search_for_book


    ```python
    def search_for_book(self, user_id:str, target: str ,store_id: str = '-1') -> (int, str, list)
    ```

    If the value of _store_id_ is 1, we search in all stores.

    If the results of search is too large, we will return only 10 results once
    ```python
    result = self.session.query(books).filter(or_(
      books.title.ilike(f'%{target}%'),
      books.author.ilike(f'%{target}%'),
      books.publisher.ilike(f'%{target}%'),
      books.original_title.ilike(f'%{target}%'),
      books.translator.ilike(f'%{target}%'),
      books.author_intro.ilike(f'%{target}%'),
      books.book_intro.ilike(f'%{target}%'),
      books.content.ilike(f'%{target}%'),
      books.tags.ilike(f'%{target}%')
    )).limit(10)
    ```

#### Order Function
- buyer.py
  - order_cancel

    Cancle the order and update the information accroding to the status of order(paid or not paid)


  - order cancel automatically

    - be/server.py

      Check the order every 15 seconds (a short time to test easily)

      ```python
      scheduler = APScheduler()
      scheduler.add_job('regular_inspection', regular_inspection, trigger='interval', seconds=15)
      scheduler.start()
      ```

    - be/times.py
      A function to check the status of orders. If the order is not paid, then cancel the order automatically
      ```python
      def regular_inspection():
          b = Buyer()
          result = b.session.query(new_order).filter(new_order.status == 0)
          for row in result:
              order_id = row.order_id
              duration = (datetime.datetime.now() - row.create_time).total_seconds()
              if duration > b.duration_limit:
                  store_id = row.store_id
                  booklist = b.session.query(new_order_detail).filter(new_order_detail.order_id == order_id)
                  for row in booklist:
                      book_id = row.book_id
                      count = row.count
                      result = b.session.query(store).filter(store.store_id == store_id, store.book_id == book_id).first()
                      if result:
                          result.stock_level += count
                          b.session.add(result)
                          b.session.commit()
                  result = b.session.query(new_order).filter(new_order.order_id == order_id).first()
                  result.status = 4
                  b.session.add(result)
                  b.session.commit()
      ```

    Check the duration: if the time is longer than the pre-defined value and the order is not paid, then cancel the order.

    ```python
    duration = (datetime.datetime.now() - order.create_time).total_seconds()
    for row in booklist:
        book_id = row.book_id
        count = row.count
        if order.status <= 1 and duration > self.duration_limit:
            bookresult = self.session.query(store).filter(store.store_id == store_id, store.book_id == book_id).first()
            if bookresult:
                bookresult.stock_level += count
                self.session.add(userresult)
                self.session.commit()
            else:
                return 536, "invalid store_id and book_id", ""
        order_details.append(row.to_dict())
    ```
  - order_query

    Search all order and show their status.



## Evaluations
### Base 60%

![](pytest.png)

All 39 pass (contains our own tests) in 56.76s (contains 15s sleep for our own test)

### Additional 40%

For the additional function, we write three more test.py:
  - test_delivery.py

    First, create an order and test the delivery and take delivery.

    We test some unallowed behaviors
    - deliver before payment
    - take delivery before deliver
    - repeat deliver
    - repeat take delivery

  - test_search_book.py

    First, we create two book stores and add some books(a part of these books are same)

    We test the function search in one certain store and all stores.

  - test_order.py

    First, we create some orders.

    We test the delivery and take delivery. (For testing some unallowed behaviors)

    We test some unallowed behaviors
    - deliver before payment
    - auto cancel
    - deliver after cancel

    We test auto cancel by sleep 15s (a short time to test easily)

All our test programs have cover all the error number which we write. We also test some unallowed behaviors to ensure. So we believe our code coverage is high.

We use _coverage_ to test

![](coverage.png)

Our total coverage is 88%



## Improvement
### Search Results

```python
result = self.session.query(books).filter(or_(
                books.title.ilike(f'%{target}%'),
                books.author.ilike(f'%{target}%'),
                books.publisher.ilike(f'%{target}%'),
                books.original_title.ilike(f'%{target}%'),
                books.translator.ilike(f'%{target}%'),
                books.author_intro.ilike(f'%{target}%'),
                books.book_intro.ilike(f'%{target}%'),
                books.content.ilike(f'%{target}%'),
                books.tags.ilike(f'%{target}%')
            ))
```

### Access Control
We find that there do not exist some access control between the owner of the store and the buyers. 

Owing to the lack of access control, any user who knows the _store_id_ can modify the info of books, so we add access control in the backend.

```python
def is_my_store(self, user_id, store_id):
    # result = self.db['user_store'].find_one({'user_id': user_id, 'store_id': store_id})
    result = self.session.query(user_store).filter(user_store.user_id == user_id, user_store.store_id == store_id).first()
    if result:
        return True
    else:
        return False
```

And we will invoke this function to check access.

### Transaction Processing
Use rollback to deal with the abortion of the transaction
```python
except SQLAlchemyError as e:
  self.session.rollback()
  return (error number), "{}".format(str(e)), []
```

### Git
https://github.com/Shinaaaaaa/Database.git

Git and GitHub is used to manage the code version

