from flask import Flask
from chargesats import Charger


app = Flask(__name__)


# Init the charger!
lnrpc = '/tmp/l1-regtest/regtest/lightning-rpc'
secret = 'very private string no one knows'
Charger.init(lnrpc, secret)


@app.route('/')
# Use the charger to charge some sats for an endpoint!
@Charger.charge(amount="100sat")
def index():
    return 'This cost you 100 sats\\n'


app.run(host='0.0.0.0', port=6666)
