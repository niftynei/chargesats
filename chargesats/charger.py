import random, string, functools

from hashlib import sha256
from pyln.client import LightningRpc
from flask import Response, request


def randomword(length):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(length))


class Charger:
    rpc = None
    invoice_hashes = [] 
  
    def __init__(self):
      pass
      
    @classmethod
    def init_rpc(self, rpc_socket):
      self.rpc = LightningRpc(rpc_socket)

    def _verify_preimage(self, preimage):
      preimage_hash = sha256(bytes.fromhex(preimage)).hexdigest()
      found = False
      for hash in self.invoice_hashes:
              found = (hash == preimage_hash)
              if found:
                    break
                
      # pay-per-view means you pay every time.
      if found:
              self.invoice_hashes.remove(preimage_hash)
              
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
                                rune, preimage = parts[1].split(':', maxsplit=1)
                                print(rune, preimage)
                                if self.verify_preimage(preimage):
                                        return func(*args, **kwargs) 
              
                  rando_label = randomword(15)
                  invoice = self.rpc.invoice(amount_msat=amount, label="{}".format(rando_label), description="Payment for {} {}".format(request.method, request.path))
                  bolt11 = invoice['bolt11'] 
                  self.invoice_hashes.append(invoice['payment_hash'])
                                  
                  resp = Response("Needs payment ({}): {}".format(amount, bolt11), status=402)
                  resp.headers["WWW-Authenticate"] = 'L402 token="", invoice="{}"'.format(bolt11)
                  return resp
            return wrapper
        return _decorator(f_py) if callable(f_py) else _decorator
