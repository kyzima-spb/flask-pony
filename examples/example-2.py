# coding: utf-8

from flask import Flask
from pony.orm import Required

from flask_pony import Pony


app = Flask(__name__)

pony = Pony()
pony.init_app(app)

db = pony.db


class User(db.Entity):
    name = Required(str, 50)


pony.connect()

app.run(debug=True)
