import asyncio,prometheus_client
from flask import Flask, Response
from gevent import pywsgi
from metrics import *
from collect import api2metrics
from config import get_args
from flask_basicauth import BasicAuth

args = get_args()

app = Flask(__name__)

app.config["BASIC_AUTH_USERNAME"] = 'admin'
app.config["BASIC_AUTH_PASSWORD"] = '123456'
basic_auth = BasicAuth(app)

@app.route('/')
@basic_auth.required
def index():
    return "<h1>Customized Exporter</h1><br><a href='metrics'>Metrics</a>"
@app.route('/metrics')
@basic_auth.required
def fusion_info():
    api2metrics()
    return Response(prometheus_client.generate_latest(REGISTRY),mimetype="text/plain")

if __name__=="__main__":
    # app.run(host='0.0.0.0', port=9088)
    address = args.address
    port = args.port
    server = pywsgi.WSGIServer((address, port), app)
    server.serve_forever()
