import random, string, functools, hmac

from hashlib import sha256
from pyln.client import LightningRpc
from flask import Response, request


def randomword(length):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(length))


class Charger:
    rpc = None
    hmac_list = []
    secret = ''.encode()
  
    def __init__(self):
      pass
      
    @classmethod
    def init(self, rpc_socket, secret):
      self.rpc = LightningRpc(rpc_socket)
      self.secret = secret.encode()

    @classmethod
    def _make_hmac(self, payment_hash, method, path, data):
      mac = hmac.new(self.secret, digestmod=sha256)
      mac.update(payment_hash.encode())
      mac.update(method.encode())
      mac.update(path.encode())
      mac.update(data.encode())
      return mac.hexdigest()

    @classmethod
    def _verify_hmac(self, hmac, preimage, method, path, data):
      preimage_hash = sha256(bytes.fromhex(preimage)).hexdigest()

      exp_hmac = self._make_hmac(preimage_hash, method, path, data)
      return exp_hmac == hmac

    @classmethod
    def _check_usage(self, hmac):
      found = False
      for mac in self.hmac_list:
              found = (hmac == mac)
              if found:
                    break
                
      # pay-per-view means you pay every time.
      if found:
              self.hmac_list.remove(hmac)
              
      return found

    @classmethod
    def charge(self, f_py=None, amount="100msat"):
        assert callable(f_py) or f_py is None
        def _decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                  if "Authorization" not in request.headers:
                        pass
                  else:
                        parts = request.headers["Authorization"].split()
                        if len(parts) == 2 and (parts[0] == "L402" or parts[0] == "l402"):
                                hmac, preimage = parts[1].split(':', maxsplit=1)
                                if self._verify_hmac(hmac, preimage, request.method, request.path, '') and self._check_usage(hmac):
                                        return func(*args, **kwargs) 
              
                  rando_label = randomword(15)
                  invoice = self.rpc.invoice(amount_msat=amount, label="{}".format(rando_label), description="Payment for {} {}".format(request.method, request.path))
                  bolt11 = invoice['bolt11'] 

                  hmac = self._make_hmac(invoice['payment_hash'], request.method, request.path, '')
                  self.hmac_list.append(hmac)
                                  
                  resp = Response("Needs payment ({}): {}".format(amount, bolt11), status=402)
                  resp.headers["WWW-Authenticate"] = 'L402 token="{}", invoice="{}"'.format(hmac, bolt11)
                  return resp
            return wrapper
        return _decorator(f_py) if callable(f_py) else _decorator
