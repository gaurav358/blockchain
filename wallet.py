from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii


class Wallet:

    def __init__(self):
        self.privatekey = None
        self.publickey = None

    def create_keys(self):
    
        privatekey, publickey = self.generate_keys()
        self.privatekey = privatekey
        self.publickey = publickey

    def save_keys(self):
        if self.publickey != None and self.privatekey != None:
            try:
                with open('wallet.txt', mode='w') as f:
                    f.write(self.publickey)
                    f.write('\n')
                    f.write(self.privatekey)
                return True
            except (IOError, IndexError):
                pass
            finally:
                print("in the save keys")

    def load_keys(self):
        try:
            with open('wallet.txt', mode='r') as f:
                keys = f.readlines()
                publickey = keys[0][:-1]
                privatekey = keys[1]
                self.publickey = publickey
                self.privatekey = privatekey
            return True
        except (IOError, IndexError):
            pass
        finally:
            print("in the save keys")


    def generate_keys(self):      
        privatekey = RSA.generate(1024, Crypto.Random.new().read)
        publickey = privatekey.publickey()
        return (binascii.hexlify(privatekey.exportKey(format='DER')).decode('ascii'), binascii.hexlify(publickey.exportKey(format='DER')).decode('ascii'))

    def sign_transaction(self, sender, receiver, amount):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.privatekey)))
        hash = SHA256.new((str(sender) + str(receiver) + str(amount)).encode('utf8'))
        sign = signer.sign(hash)
        return binascii.hexlify(sign).decode('ascii')

    @staticmethod
    def verify_transaction(transaction):
        publickey = RSA.importKey(binascii.unhexlify(transaction.sender))
        public_verify = PKCS1_v1_5.new(publickey)
        h = SHA256.new((str(transaction.sender) + str(transaction.receiver) + str(transaction.amount)).encode('utf8'))
        return public_verify.verify(h, binascii.unhexlify(transaction.sign))