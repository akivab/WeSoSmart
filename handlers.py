'''
Created on Jan 3, 2011

@author: akiva
'''
import re
import random
from tools import render_template
from controller.controller import GetBooks
from controller.controller import getSections
from model.model import *

from controller.user_management import UserManagement
from django.utils.html import escape
from django.utils import simplejson
from google.appengine.ext import db
from google.appengine.ext.db import Key
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

class Handler(webapp.RequestHandler):
    def __init__(self, handler=None, template_values=None):
        if handler:
            self.request = handler.request
            self.response = handler.response
            self.template_values= template_values
    
class CommentHandler(Handler):
    def post(self):
        user = UserManagement(self).getUser()
        if not user:
            self.redirect('/error?type="Not signed in"')
            return
        subject = self.request.get("subject")
        orig = self.request.get("orig")
        comment = escape(self.request.get("comment_text"))
        file = self.request.get("file")
        Comment.addComment(user, Key(subject), self.request.get("subject_type"), comment,file)
        self.redirect("/"+self.request.get("subject_type")+"/"+orig)
        
class SectionHandler(Handler):
    def get(self):
        sections = [db.get(Key(i)) for i in self.request.get("keys").split(",")]
        classes = [i.class_id for i in sections]
        page = "view/imported_books.html"
        self.template_values['classes']= classes
        self.template_values['sections']= sections
        self.response.out.write(render_template(self.template_values, page))
        
class PriceHandler(Handler):
    def post(self):
        id = db.get(Key(self.request.get("id")))
        price = self.request.get("price")
        type = 0 if self.request.get("type")=="want" else 1
        id.price = price
        id.put()

class SendHandler(Handler):
    def post(self):
        try:
            if self.template_values['signed_in']:
                user_from = self.template_values['um'].getUser()
                email = self.request.get("message")
                to = self.request.get("to")
                if to == "akiva.bamberger@gmail.com":
                    SendEmail().sendDirect("Wise Wizard", to, str(user_from.key()), user_from.name, user_from.cubmail, email)
                else:
                    user_to = User.get(Key(self.request.get("to")))
                    tmp = UserUsers(user_id = user_from, level=1,
                              message = "Sent to <a href='http://www.wesosmart.com/user/%s'>%s</a>: %s"%(str(user_to.key()), user_to.name,  email))
                    tmp.put()
                    tmp = UserUsers(user_id = user_to, level=1, 
                              message = "Sent from <a href='http://www.wesosmart.com/user/%s'>%s</a>: %s"%(str(user_from.key()), user_from.name, email))
                    tmp.put()
                    SendEmail().sendDirect(user_to.name, user_to.cubmail, str(user_from.key()), user_from.name, user_from.cubmail,email)
            else:
                SendEmail().sendDirect("Wise Wizard", "akiva.bamberger@gmail.com", "", "Anonymous", "Anonymous", email + " not signed in, but to "+self.request.get("to"))
        except Exception, e:
            SendEmail().sendDirect("Wise Wizard", "akiva.bamberger@gmail.com", "", "Anonymous", "Anonymous", email + " error "+str(e) + " to "+self.request.get("to"))
        self.response.out.write(render_template(None, "view/complete.html"))
        
    def get(self):
        user_to = self.request.get("id")
        if user_to == "thewizard":
            self.template_values['to']= "Webmaster"
            self.template_values['email'] = "akiva.bamberger@gmail.com"
        else:
            user_to = User.get(Key(user_to))
            self.template_values['to']=user_to.name
            self.template_values['email']=str(user_to.key())
        page="view/sendmessage.html"
        self.response.out.write(render_template(self.template_values, page))

class MessageHandler(Handler):
    def get(self):
        if not self.template_values['signed_in']:
            self.redirect('/signup_page?redirect=%s'%self.request.url)
            return
        page = "view/messages.html"
        self.template_values['title']="Messages"
        userusers = UserUsers.gql("WHERE user_id = :1 ORDER BY time DESC", self.template_values['um'].getUser())
        to_keep = []
        to_forget = []
        for i in userusers:
            try:
                i.userbook_id
                to_keep.append(i)
            except Exception, e:
                if i.level == 1:
                    to_keep.append(i)
                else:
                    to_forget.append(i)
        for i in to_forget:
            db.delete(i)
        self.template_values['messages']=to_keep
        self.template_values['length'] = len(self.template_values['messages'])
        self.response.out.write(render_template(self.template_values, page))

class ImportHandler(Handler):
    def get(self):
        page = "view/import_books.html"
        self.template_values['title']="Import"
        self.response.out.write(render_template(self.template_values, page))
        
    def post(self):
        classn = []
        sections = []
        for i in re.finditer(r'([A-Z]+) (\w?\d+).(\d+).(\d+).(\d+)',self.request.get("book_import")):
            tmp = Class.gql("WHERE dept=:1 AND number=:2",i.group(1), i.group(2)).get()
            tmps = Section.gql("WHERE section=:1 AND semester=:2 AND class_id=:3", i.group(3), i.group(4)+i.group(5), tmp).get()
            if tmp:
                classn.append(tmp)
            if tmps:
                sections.append(tmps)
        page = "view/imported_books.html"
        self.template_values['classes']= classn
        self.template_values['sections']= sections
        self.response.out.write(render_template(self.template_values, page))
        
class ClassHandler(Handler):
    def post(self):
        classn = Class.get(Key(self.request.get("class")))
        books = []
        ids = []
        sections = getSections(classn)
        for k in [ClassBooks.gql("WHERE section_id=:1",j) for j in sections]:
            for classbook in k:
                try:
                    ids.index(classbook.book_id.key())
                except Exception,e:
                    i = classbook.book_id
                    ids.append(i.key())
                    if not i.picture:
                        GetBooks().setBookInfo(i)
                    books.append([i.picture.link, i.prev, i.title, i.author, i.description, "%.2f"%i.price, str(i.key())])
        self.response.out.write(simplejson.dumps(books))
                        
class KeyHandler(Handler):
    def get_info(self):
        results = memcache.get("results")
        if results is not None:
            return results
        else:
            results = self.render_info()    
            if not memcache.add("results", results,86400):
                logging.error("Memcache set failed.")
            return results

    def render_info(self):
        results = Subject.gql("WHERE class = 'Book'")
        return simplejson.dumps([i.name[:60] if i.name else "" for i in results])
    
    def post(self):
        self.response.out.write(self.get_info())
    def get(self):
        search = self.request.get("s")
        subject = Subject.gql("WHERE name >= :1 AND name < :2", search, search + u"\ufffd").get()
        if not subject:
            subject = Subject.gql("WHERE isbn=:1",search).get()
        if not subject:
            subject = Subject.gql("WHERE author >= :1 AND author < :2",search, search + u"\ufffd").get()
        if subject:
            self.redirect("/book/%s"%str(subject.key()))
        else:
            self.redirect("/")
                        
class SubjectHandler(webapp.RequestHandler):
    def __init__(self, handler=None, template_values=None):
        if handler:
            self.request = handler.request
            self.path = self.request.path
            self.response = handler.response
            self.template_values= template_values
            self.template_values['random'] = random.randrange(1,8)
            self.template_values['uk']= self.template_values['um'].getUser()
            self.page = "view/subject_page.html"
    
    def getUser(self, user):
        if user.level < 2 and not self.template_values['signed_in']:
            self.redirect('/signup_page?redirect=%s'%self.request.url)
            return
        if not user.picture:
            self.template_values['picture']='/img/noimage.jpg'
        else:
            self.template_values['picture']=user.picture.link;
        self.template_values['title']=user.name
        if user.level != 2:
            self.template_values['newb'] = True
        self.template_values['pro'] = (user.cubmail == "ion2101@columbia.edu"
                                       or user.cubmail == "ab2928@columbia.edu" 
                                       or user.cubmail == "ebw2115@columbia.edu"
                                       or user.cubmail == "rab2172@columbia.edu")
        self.template_values['is_user'] = True
        self.template_values['user_class_list'] = UserClasses.gql("WHERE user_id=:1",user);
        self.template_values['book_want_list'] = UserBooks.gql("WHERE user_id=:1 AND status=:2",user,0)
        self.template_values['book_have_list'] = UserBooks.gql("WHERE user_id=:1 AND status=:2",user,1)
        self.response.out.write(render_template(self.template_values, self.page))
    
    def getClass(self, section):
        if not section.name:
            section.name = section.class_id.name
            section.put()
        if not section.picture:
            self.template_values['picture']='/img/noimage_generic.jpg'
        else:
            self.template_values['picture']=section.picture.link
        self.template_values['is_class'] = True
        self.template_values['classbooks'] = ClassBooks.gql("WHERE section_id=:1",section) 
        self.template_values['userclasses'] = UserClasses.gql("WHERE section_id=:1",section)
        self.template_values['title']="%s (%s %s)"%(section.name, 
                                                    ("Spring" if section.semester[-2:-1]=="1" else "Summer" if section.semester[-2:-1]=="2" else "Fall"),
                                                     section.semester[:-1])
        self.response.out.write(render_template(self.template_values, self.page))
    
    def getBook(self, book):
        if not book.name:
            book.name = book.title
            book.put()
        if not book.prev:
            try:
                GetBooks().setBookInfo(book)
                self.template_values['picture']=book.picture.link.replace("zoom=5","zoom=1");
            except Exception,e:
                self.template_values['picture']="/img/b8.jpg"
        else:
            if book.picture.link:
                self.template_values['picture']=book.picture.link.replace("zoom=5","zoom=1");
            else:
                self.template_values['picture']="/img/b8.jpg"
        self.template_values['is_book'] = True
        self.template_values['title']=book.name
        self.template_values['book_class_list'] = ClassBooks.gql("WHERE book_id = :1", book)
        self.template_values['book_want_list'] = UserBooks.gql("WHERE book_id=:1 AND status=0",book)
        self.template_values['book_have_list'] = UserBooks.gql("WHERE book_id=:1 AND status=1",book)
        self.template_values['wantcount'] = self.template_values['book_want_list'].count()
        self.template_values['havecount'] = self.template_values['book_have_list'].count()
        self.response.out.write(render_template(self.template_values, self.page))
    
    def getComments(self, subject):
        return Comment.getComments(subject)
    
    def get(self):
        m = re.match(r'/(book|user|class)/(.+)$', self.path)
        s = Subject.get(Key(m.group(2)))
        self.template_values['description'] = s
        self.template_values['comments'] = self.getComments(s)
        if m.group(1) == "user":
            self.getUser(s)
        elif m.group(1)=="book":
            self.getBook(s)
        elif m.group(1)=="class":
            self.getClass(s)