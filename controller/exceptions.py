'''
Created on Jan 2, 2011

@author: akiva
'''
class BadUserException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class VerificationNeededException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class UnregisteredException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
