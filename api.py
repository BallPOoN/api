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
	longtitude = pe.TextField()
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

# @brief : 指定したuserの情報を取得するためのエンドポイント
@api.route('/uinfo/<string:name>', methods=['GET'])
def get_user(name):
    try:
        selection = 'select * from user where name=?'
        key = (name,)
        connection = sqlite3.connect(db)
        connection.row_factory = sqlite3.Row
        sql = connection.cursor()
        sql.execute(selection, key)
        rows = sql.fetchall()
        result = {"result":False}
        if len(rows) == 0:
            dummy = 'a'
        elif len(rows) == 1:
            # ToDo:
            # Profileを表示するのに必要な情報を取得する
            # 投稿リストも必要だと思うのでそれ用のdbにもアクセスしてレスポンスに追加する
            row = rows[0]
            result = {
                "result":True,
                "name":row['name'],
                "favorite":row['favorite'],
                "latitude":row['latitude'],
                "longtitude":row['longtitude']
                }
        connection.close()
    except user.DoesNotExist:
        abort(404)

    return make_response(jsonify(result))

# @Brief : userを消去するためのエンドポイント
@api.route('/user/<string:name>', methods=['DELETE'])
def del_user(name):
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
        # 猶予期間が終了したら投稿リストからも削除しなければいけない
        connection.close()
    except user.DoesNotExist:
        abort(404)

    return make_response(jsonify(result))

# @Brief : user情報を更新するためのエンドポイント
@api.route('/update/<string:name>', methods=['POST'])
def update_user(name):
    # ToDo:
    # ユーザーの情報を更新する処理を実装する
    # 位置情報，好きなもの，その他主にProfile関連
    dataDict = json.loads(request.data)
    try:
        update = 'update user set favorite=?,latitude=?,longtitude=?where name=?'
        key = (dataDict['favorite'], dataDict['latitude'], dataDict['longtitude'], name)
        connection = sqlite3.connect(db)
        connection.row_factory = sqlite3.Row
        sql = connection.cursor()
        sql.execute(update, key)
        connection.commit()
        result = {"result":True}

        connection.close()
    except user.DoesNotExist:
        abort(404)

    return make_response(jsonify(result))

@api.route('/post', methods=['POST'])
def post_tweet():
    dataDict = json.loads(request.data)

    try:
        insert = 'insert into post (name, time, latitude, longtitude, altitude, feel, comment) values (?,?,?,?,?,?,?)'
        data = (dataDict['name'], dataDict['time'], dataDict['latitude'], dataDict['longtitude'], dataDict['altitude'], dataDict['feel'], dataDict['comment'])
        update = 'update user set longtitude=?,latitude=?,altitude=?,feel=?,comment=?where name=?'
        key = (dataDict['longtitude'], dataDict['latitude'], dataDict['altitude'], dataDict['feel'], dataDict['comment'], dataDict['name'])
        connection = sqlite3.connect(db)
        connection.row_factory = sqlite3.Row;
        sql = connection.cursor()
        sql.execute(insert, data)
        sql.execute(update, key)
        connection.commit()
        result = {"result":True}
        connection.close()
    except user.DoesNotExist:
        abort(404)

    return make_response(jsonify(result))

@api.route('/get_tweet', methods=['POST'])
def get_tweet():
    dataDict = json.loads(request.data)
    try:
        name_ = dataDict.get('name')
        since_ = dataDict.get('since')
        to_ = dataDict.get('to')
        id_ = dataDict.get('id')
        lat_ = dataDict.get('latitude')
        long_ = dataDict.get('longtitude')
        dist_ = dataDict.get('distance')
        count = dataDict.get('count')
        key = 'select * from post where name = ? and time <= datetime(?) and time >= datetime(?) and id <= ? order by id desc'
        data = (name_, to_, since_, id_)
        connection = sqlite3.connect(db)
        connection.row_factory = sqlite3.Row
        sql = connection.cursor()
        sql.execute(key, data)

        rows = sql.fetchall()

        result = []
        for row in rows:
            tmp = {'id':row['id'],
                    'name':row['name'],
                    'time':row['time'],
                    'longtitude':row['longtitude'],
                    'latitude':row['latitude'],
                    'altitude':row['altitude'],
                    'feel':row['feel'],
                    'comment':row['comment']}
            result.append(tmp)
            print(tmp)

    except user.DoesNotExist:
        abort(404)

    return make_response(jsonify(result))

@api.route('/get_around', methods=['POST'])
def get_around():
    print(request.data)
    dataDict = json.loads(request.data)
    try:
        extend = '''.load /home/ubuntu/api/libsqlitefunctions.so'''
        key = 'select *, (6371000*ACOS(cos(radians(?))*cos(radians(latitude))*cos(radians(longtitude)-radians(?))+sin(radians(?))*sin(radians(latitude)))) as distance from user where distance <= ?;'


        lat_ = dataDict.get('latitude')
        long_ = dataDict.get('longtitude')
        dist_ = int(dataDict.get('distance'))
        data = (lat_, long_, lat_, dist_)

        print(data)
        print(type(dist_))

        connection = sqlite3.connect(db)
        connection.row_factory = sqlite3.Row
        connection.enable_load_extension(True)
        connection.execute("select load_extension('./libsqlitefunctions.so')")
        sql = connection.cursor()
        sql.execute(key, data)

        rows = sql.fetchall()

        result = []
        for row in rows:
            tmp = { 'id':row['id'],
                    'name':row['name'],
                    'longtitude':row['longtitude'],
                    'latitude':row['latitude'],
                    'distance':row['distance'],
                    'feel':row['feel'],
                    'comment':row['comment'],
                    'description':row['comment'],
                    'altitude':row['altitude'],
                    'longitude':row['longtitude']}
            result.append(tmp)
            print(tmp)
    except user.DoesNotExist:
        abort(404)

    return make_response(jsonify(result))

# @Brief : Error Handler
@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error' : 'Not Found'}), 404)

# @Brief : Main function
if __name__ == '__main__':
    api.run(host = '0.0.0.0', port = 23456)
