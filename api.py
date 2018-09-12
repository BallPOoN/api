# @Author : Keita.S 
# @Date	  : 2018-09-01
# @Brief  : API for mary

from flask import Flask, jsonify, abort, make_response, request
import peewee as pe
import random
import json
import sqlite3

def random_string(length, seq = '0123456789abcdefghijklmnopqrstuvwsyz'):
    sr = random.SystemRandom()
    return ''.join([sr.choice(seq) for i in range(length)])

db = 'data.db'

class user(pe.Model):
	name = pe.TextField()
	token = pe.TextField()
	tokenSec = pe.TextField()
	created = pe.TextField()
	favorite = pe.TextField()
	langtitude = pe.TextField()
	latitude = pe.TextField()

	class Meta:
		database = db

api = Flask(__name__)


# userを作成するためのエンドポイント
@api.route('/user', methods=['POST'])
def post_user():
    # jsonリクエストを辞書型に格納するよ
    dataDict = json.loads(request.data)
    try:
        connection = sqlite3.connect(db)
        connection.row_factory = sqlite3.Row
	sql = connection.cursor()

	# 指定したuserがすでに存在するかどうかを確認する
	selection = 'select * from user where name=?'
	key = (dataDict['name'],)
	sql.execute(selection, key)
	rows = sql.fetchall()

	# 既にユーザーが存在している...だと!?
	if len(rows) == 1:
	    result = {"result" : False}

    	# ユーザーはまだいないぞ...!!
	else:
            insert = 'insert into user (name, token, tokenSec, created) values (?,?,?,?)'
	    data = (dataDict['name'], dataDict['token'], dataDict['tokenSec'], dataDict['created'])
	    sql.execute(insert,data)
	    connection.commit()
	    result = {"result" : True}
	connection.close()
	except user.DoesNotExist:
	    abort(404)

	return make_response(jsonify(result))


# @brief : user認証を行うためのエンドポイント
@api.route('/oauth', methods=['POST'])
def oauth_user():
    dataDict = json.loads(request.data)
    try:
        # 取り敢えずユーザーを検索するぞ
        selection = 'select * from user where name=?'
	key=(dataDict['name'],)
	connection = sqlite3.connect(db)
	connection.row_factory = sqlite3.Row
	sql = connection.cursor()
	sql.execute(selection, key)
	rows = sql.fetchall()
	result = {"result":False}

	# そもそもユーザーが存在しないぞ
	if len(rows) == 0:
            # ToDo:
            # ユーザーが存在しなかったときに必要な処理を実装
	    dummy = 'a'
        # ユーザーが存在したな
	elif len(rows) == 1:
	    row = rows[0]
	    if row['name'] == dataDict['name'] and row['token'] == dataDict['token'] and row['tokenSec'] == dataDict['tokenSec']:
	        result = {
	            "result" : True
		    }
	connection.close()
	except user.DoesNotExist:
	    abort(404)

	return make_response(jsonify(result))

# @Brief : userを消去するためのエンドポイント
@api.route('/user/<string:name>', methods=['DELETE'])
def del_user():
    try:
        delete = 'delete from user where name=?'
        key = (name,)
        connection = sqlite3.connect(db)
        connection.row_factory = sqlite3.Row
        sql = connection.cursor()
        sql.execute(delete, key)
        result = {"result":True}

        # ToDo:
        # 消去が成功したかどうかをデータベースに問い合わせて確認
        # 一定期間はデータを残すような機構を検討
        connection.close()
    except user.DoesNotExist:
        abort(404)

    return make_response(jsonify(result))

# @Brief : user情報を更新するためのエンドポイント
def update_user():
    dummy = 'a'


# @Brief : Error Handler
@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error' : 'Not Found'}), 404)

# @Brief : Main function
if __name__ == '__main__':
    api.run(host = '0.0.0.0', port = 23456)
