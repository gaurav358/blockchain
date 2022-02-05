from collections import OrderedDict

from utility.printable import Printable

class Transaction(Printable):
   
    def __init__(self, sender, receiver, sign, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.sign = sign
