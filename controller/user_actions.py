'''
Created on Jan 2, 2011

@author: akiva
'''
import fix_path

from model.model import User
from model.model import Book
from model.model import UserBooks
from model.model import UserUsers

import json as simplejson
from user_management import UserManagement

from google.appengine.ext.db import Key
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class UserAction(webapp.RequestHandler):
    def __init__(self, handler=None):
        self.WANT,self.HAVE = range(2)

    def post(self):
        self.um = UserManagement(self)
        self.user = self.um.getUser()

        status = self.request.get("type")
        book = self.request.get("book")
        price = self.request.get("price")
        book_id = self.getBook(book)
        toreturn = self.setAction(book_id, self.WANT if status == "want" else self.HAVE, price)
        self.response.out.write(simplejson.dumps(toreturn))

    # update a price or add a book/status
    def setAction(self, book, status, price=None):
        user = self.user
        if not user:
            raise Exception("Not signed in")
        ub = UserBooks.gql("WHERE user_id = :1 AND book_id = :2 AND status=:3",user,book,status).get()
        if not ub:
            ub = UserBooks(user_id = user, book_id = book, status = status, price=price)
            ub.put()
            self.sendMessages(ub)
        elif price:
            ub.price = price
            ub.put()
        return [str(ub.key()), ub.price]

    def sendMessages(self, ub):
        status = self.HAVE if ub.status == self.WANT else self.WANT
        for j in UserBooks.gql("WHERE book_id=:1 AND status=:2", ub.book_id, status):
            response = "match found"
            UserUsers.addMessage(j.user_id, ub, response)
            UserUsers.addMessage(ub.user_id, j, response)

    def getBook(self,book_str):
        return Book.get(Key(book_str))

    def getActions(self, book, status):
        ub = UserBooks.gql("WHERE status=:1 AND book_id=:2", status, book)
