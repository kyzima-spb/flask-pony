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

from flask import request, abort, redirect, url_for, render_template
from pony.orm import db_session, ObjectNotFound

from . import app
from .models import Customer
from .forms import CustomerForm


@app.route('/customer/<int:customer_id>')
@db_session
def customer_show(customer_id):
    try:
        return render_template('customer/show.html', customer=Customer[customer_id])
    except ObjectNotFound:
        abort(404)


@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    form = CustomerForm(request.form)

    if form.validate_on_submit():
        with db_session:
            customer = Customer(email=form.email.data,
                                   password=form.password.data,
                                   name=form.name.data,
                                   country=form.country.data,
                                   address=form.address.data)
        return redirect(url_for('customer_show', customer_id=customer.id))

    return render_template('customer/register.html', form=form)


@app.route('/customer/edit/<int:customer_id>', methods=['GET', 'POST'])
@db_session
def customer_edit(customer_id):
    try:
        customer = Customer[customer_id]
    except ObjectNotFound:
        abort(404)

    form = CustomerForm(request.form, obj=customer)

    if form.validate_on_submit():
        customer.email = form.email.data
        customer.password = form.password.data
        customer.name = form.name.data
        customer.country = form.country.data
        customer.address = form.address.data
        return redirect(url_for('customer_show', customer_id=customer.id))

    return render_template('customer/edit.html', form=form)
