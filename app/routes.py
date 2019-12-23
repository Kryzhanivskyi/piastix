from app import app
from flask import render_template, request, redirect
import json
import requests
import hashlib
import sqlite3
import uuid
from datetime import datetime


@app.route('/')
@app.route('/index')
def index():
    connection = sqlite3.connect('app.db')
    conn = connection.cursor()
    conn.execute('SELECT * FROM currency')
    db_list = conn.fetchall()
    currency_list = []
    for currency in db_list:
        currency_list.append(currency[1])
    return render_template('index.html', currencies=currency_list)


@app.route('/make_payment', methods=['POST'])
def make_payment():
    amount = request.form['amount']
    currency = request.form['currency']
    description = request.form['description']
    shop_id = 5
    shop_order_id = 101
    payway = "payeer_rub"
    if currency == "EUR":
        currency_code = 978
        srt_to_hash = amount + ':' + str(currency_code) + ':' + str(shop_id) + ':' + str(shop_order_id) + 'SecretKey01'
        signature = hashlib.sha256(srt_to_hash.encode()).hexdigest()
        context = {"amount": amount, "currency": currency_code, "shop_id": shop_id, "sign": signature,
                   "shop_order_id": shop_order_id, "description": description}
        con = sqlite3.connect('app.db')
        c = con.cursor()
        c.execute("INSERT INTO payment (currency_id, amount, description, uid_code, payment_sending_time)"
                  "VALUES (?,?,?,?,?)", (1, float(amount), description, str(uuid.uuid4()), datetime.utcnow()))
        con.commit()
        return render_template('piastrix.html', **context)
    elif currency == "USD":
        payer_currency = 840
        shop_currency = 840
        srt_to_hash = str(payer_currency) + ":" + amount + ":" + str(shop_currency) + ":" + str(shop_id) + ":" +\
                      str(shop_order_id) + "SecretKey01"
        signature = hashlib.sha256(srt_to_hash.encode('utf-8')).hexdigest()
        headers = {'Content-Type': 'application/json'}
        data = {
            "description": description,
            "payer_currency": payer_currency,
            "shop_amount": amount,
            "shop_currency": shop_currency,
            "shop_id": str(shop_id),
            "shop_order_id": shop_order_id,
            "sign": signature
        }
        response = requests.post('https://core.piastrix.com/bill/create', headers=headers, data=json.dumps(data))
        json_response = response.json()
        result = json_response.get('result')
        if result:
            con = sqlite3.connect('app.db')
            c = con.cursor()
            c.execute("INSERT INTO payment (currency_id, amount, description, uid_code, payment_sending_time)"
                      "VALUES (?,?,?,?,?)", (2, float(amount), description, str(uuid.uuid4()), datetime.utcnow()))
            con.commit()
            return redirect(json_response['data']['url'])
        else:
            data = {
                "code": json_response['error_code'],
                "message": json_response['message']
            }
            response = app.response_class(
                response=json.dumps(data),
                status=400,
                mimetype='application/json'
            )
            return response
    else:
        currency_code = 643
        payway = 'payeer_rub'
        srt_to_hash = amount + ':' + str(currency_code) + ':' + payway + ':' + str(shop_id) + ':' +\
                      str(shop_order_id) + 'SecretKey01'
        signature = hashlib.sha256(srt_to_hash.encode()).hexdigest()
        headers = {'Content-Type': 'application/json'}
        data = {
            "currency": currency_code,
            "sign": signature,
            "payway": payway,
            "amount": amount,
            "shop_id": str(shop_id),
            "shop_order_id": shop_order_id,
            "description": description
        }
        response = requests.post('https://core.piastrix.com/invoice/create', headers=headers, data=json.dumps(data))
        json_response = response.json()
        result = json_response.get('result')
        if result:
            method = json_response['data']['method']
            url = json_response['data']['url']
            response_data = json_response['data']['data']
            lang = response_data['lang']
            m_curorderid = response_data['m_curorderid']
            m_historyid = response_data['m_historyid']
            m_historytm = response_data['m_historytm']
            referer = response_data['referer']
            context = {"method": method, "url": url, "lang": lang, "m_curorderid": m_curorderid,
                       "m_historyid": m_historyid, "m_historytm": m_historytm, "referer": referer}

            con = sqlite3.connect('app.db')
            c = con.cursor()
            c.execute("INSERT INTO payment (currency_id, amount, description, uid_code, payment_sending_time)"
                      "VALUES (?,?,?,?,?)", (3, float(amount), description, str(uuid.uuid4()), datetime.utcnow()))
            con.commit()
            return render_template('invoice.html', **context)
        else:
            data = {
                "code": json_response['error_code'],
                "message": json_response['message']
            }
            response = app.response_class(
                response=json.dumps(data),
                status=400,
                mimetype='application/json'
            )
            return response


@app.route('/report')
def report():
    connection = sqlite3.connect('app.db')
    conn = connection.cursor()
    conn.execute('SELECT * FROM payment')
    db_list = conn.fetchall()
    data = []
    for item in db_list:
        cursor_dict = {
            'id': item[0],
            'currency_id': item[1],
            'amount': item[2],
            'payment_sending_time': item[3],
            'description': item[4],
            'uid_code': item[5]
        }
        data.append(cursor_dict)
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response
