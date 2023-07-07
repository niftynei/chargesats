# Charge Sats

A very simple Python library to add Pay-Per-View technology to a Flask endpoint.

Here's a quick example of how to use it. Note that it assumes the CLN node is running on/within reach of the Flask server.



```
from flask import Flask
from chargesats import Charger


app = Flask(__name__)


# Init the charger!
lnrpc = '/home/runner/.lightning/regtest/lightning-rpc'
Charger.init(lnrpc, 'secret do not share')


@app.route('/')
# Use the charger to charge some sats for an endpoint!
@Charger.charge(amount="100sat")
def index():
    return 'This cost you 100 sats\\n'


app.run(host='0.0.0.0', port=81)
```

## Pending Tasks

- Uses runes as tokens for repeat calls
- Add ability to use commando


## Authors

@niftynei (niftynei@gmail.com) is the responsible party.
