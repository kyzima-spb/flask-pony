# coding: utf-8
#
# Copyright 2017 Kirill Vercetti
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from decimal import Decimal
from pony.orm import Required, Optional, Set, PrimaryKey, buffer

from . import pony


db = pony.db


class Customer(db.Entity):
    email = Required(str, unique=True)
    password = Required(str)
    name = Required(str)
    country = Optional(str)
    address = Optional(str)
    cart_items = Set('CartItem')
    orders = Set('Order')


class Product(db.Entity):
    name = Required(str)
    categories = Set('Category')
    description = Optional(str)
    picture = Optional(buffer)
    price = Required(Decimal)
    quantity = Required(int)
    cart_items = Set('CartItem')
    order_items = Set('OrderItem')


class CartItem(db.Entity):
    quantity = Required(int)
    customer = Required(Customer)
    product = Required(Product)


class OrderItem(db.Entity):
    quantity = Required(int)
    price = Required(Decimal)
    order = Required('Order')
    product = Required(Product)
    PrimaryKey(order, product)


class Order(db.Entity):
    state = Required(str)
    date_created = Required(datetime)
    date_shipped = Optional(datetime)
    date_delivered = Optional(datetime)
    total_price = Required(Decimal)
    customer = Required(Customer)
    items = Set(OrderItem)


class Category(db.Entity):
    name = Required(str)
    products = Set(Product)
