# -*- coding: utf-8 -*-
# __author__="ZJL"
 
from flask import Flask, render_template
from flask import request
from flask import Response
 
import json
 
app = Flask(__name__)


def Response_headers(content):
    resp = Response(content)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/')
def hello_world():
    # return render_template('try.html')
    return Response_headers('hello world')


@app.route('/echarts')
def echarts():
    datas = {
            "data": [
                {"name": "allpe", "num": 100},
                {"name": "peach", "num": 123},
                {"name": "Pear", "num": 234},
                {"name": "avocado", "num": 20},
                {"name": "cantaloupe", "num": 1},
                {"name": "Banana", "num": 77},
                {"name": "Grape", "num": 43},
                {"name": "apricot", "num": 0}
            ]
        }

    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp


@app.errorhandler(403)
def page_not_found(error):
    content = json.dumps({"error_code": "403"})
    resp = Response_headers(content)
    return resp


@app.errorhandler(404)
def page_not_found(error):
    content = json.dumps({"error_code": "404"})
    resp = Response_headers(content)
    return resp


@app.errorhandler(400)
def page_not_found(error):
    content = json.dumps({"error_code": "400"})
    resp = Response_headers(content)
    return resp


@app.errorhandler(410)
def page_not_found(error):
    content = json.dumps({"error_code": "410"})
    resp = Response_headers(content)
    return resp


@app.errorhandler(500)
def page_not_found(error):
    content = json.dumps({"error_code": "500"})
    resp = Response_headers(content)
    return resp


if __name__ == '__main__':
    app.run(debug=True)

    # threaded=True
