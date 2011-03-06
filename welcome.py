import fix_path

import cgi
import os
import re

from tools import render_template

from controller.controller import *
from controller.get_books import SetupCL
from controller.get_books import GetBooks
from handlers import *
from model.model import *
from django.utils.html import escape
from controller.user_management import UserManagement
from controller.user_actions import UserAction
from serve_img import GetImage

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.db import Key
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images

class MainPage(webapp.RequestHandler):
    def post(self):
        um = UserManagement(self)
        user = um.getUser()
        signed_in = um.isLoggedIn()
        template_values = {'signed_in': signed_in, 'um':um}
        template_values['recent_comments'] = Comment.getRecent()  
        if(re.match('/settings', self.request.path)):
            pic = self.request.get("user[picture]")
            try:
                if pic:
                    picture = Picture.addPicture(db.Blob(images.resize(pic, 100, 100)))
                    user.picture = picture
                    user.put()
                self.redirect('/complete')
            except Exception, e:
               self.redirect('/error?type="problem with picture!"')
        elif(re.match(r'/add_price',self.request.path)):
            PriceHandler(self).post()
        elif(re.match(r'/add_class',self.request.path)):
            ClassHandler(self).post()
        elif(re.match(r'/add_class_book',self.request.path)):
            AddHandler(self).post()
        elif(re.match(r'/comment',self.request.path)):
            CommentHandler(self).post()
        elif(re.match(r'/sendmessage',self.request.path)):
            SendHandler(self,template_values).post()
        elif(re.match(r'/get_keywords', self.request.path)):
            KeyHandler(self).post()
        elif(re.match(r'/removeuserobj',self.request.path)):
            id = self.request.get("id")
            try:
                user = um.getUser()
                obj = None
                try:
                    obj = UserBooks.get(Key(id))
                except Exception, e:
                    obj = UserClasses.get(Key(id)) 
                if obj and obj.user_id.key() == user.key():
                    db.delete(obj) 
            except Exception, e:
                pass
            print "success"
            return
        elif(re.match(r'/addClassBook',self.request.path)):
        
            class_id = self.request.get("class")
            section_id = Section.get(Key(class_id))
            book_isbn = self.request.get("isbn")
            book_price = self.request.get("price")
            if re.match(r'\d+$', book_isbn):
                book = Book.gql("WHERE isbn=:1",book_isbn).get()
                if not book:
                    book = Book(isbn = book_isbn, price = float(book_price))
                    book.put()
                GetBooks().setBookInfo(book)
                book.title = escape(book.title)
                book.author = escape(book.author)
                book.put()
                classbook = ClassBooks.gql("WHERE section_id = :1 AND book_id=:2", section_id, book).get()
                if not classbook:
                    classbook = ClassBooks(section_id = section_id, book_id = book, req = "Recommended")
                    classbook.put()
            self.redirect('/complete')
            
        elif(re.match(r'/delete_comment',self.request.path)):
            user = UserManagement(self).getUser()
            c = Comment.get(self.request.get("c"))
            if c.user_id.key() == user.key():
                Comment.erase(c)
        elif(re.match(r'/import',self.request.path)):
            ImportHandler(self, template_values).post()
            return
        
    def get(self):
        render_template(None, 'view/footer.html')
        render_template(None, 'view/header.html')
        render_template(None, 'view/scripts.html')
        path = self.request.path;
        um = UserManagement(self)
        signed_in = um.isLoggedIn()
        
        template_values = {'signed_in': signed_in, 'um':um}
        template_values['recent_comments'] = Comment.getRecent()  
        page = "view/"
        if(path == "/"):
            page+="index.html"
            data = UserBooks().getRecent(20)
            template_values['recent_activity']=data
            template_values['is_homepage']=True
            template_values['title']="Home"
        elif(re.match(r'/find', path)):
            page+="find_books.html"
            template_values['title']="Find Books"
        elif(re.match(r'/about', path)):
            page+="about.html"
            template_values['about']=True
        elif(re.match(r'/settings', path)):
            page+="settings.html"
        elif(re.match(r'/search', path)):
            KeyHandler(self).get()
            return
        elif(re.match(r'/recent_listings', path)):
            page+="recent_listings.html"
            template_values['books'] = UserBooks().getRecent(100)
            template_values['title']="Recent Listings"
        elif(re.match(r'/complete',path)):
            page+="complete.html"
            if self.request.get("justsignedup"):
                template_values['justsignedup']=True
            template_values['task']="Mission"
        elif(re.match(r'/error',path)):
            page+="complete.html"
            template_values['reason']=self.request.get("type")
        elif(re.match(r'/profile',path)):
            if(signed_in):
                sh = SubjectHandler(self, template_values)
                sh.path = '/user/'+str(um.getUser().key()) 
                sh.template_values['profile'] = True
                sh.get()
                return
            else:
                self.redirect('/signup_page?redirect=%s'%self.request.url)
                return
        elif(re.match(r'/messages',path)):
            MessageHandler(self,template_values).get()
            return
        elif(re.match(r'/enroll', path)):
            class_id = self.request.get("class")
            try:
                section_id = Section.get(Key(class_id))
                user_id = um.getUser()
                userclass = UserClasses.gql("WHERE user_id = :1 AND section_id = :2", user_id, section_id).get()
                if not userclass:
                    userclass = UserClasses(user_id=user_id, section_id = section_id, relationship=0)
                    userclass.put()
                self.redirect("/complete")
            except Exception, e:
                self.redirect('/error?type='+str(e))
            return
        elif(re.match(r'/addClassBook', path)):
            page = "addClassBook.html"
            template_values['class'] = self.request.get("class")
        elif(re.match(r'/sections',path)):
            SectionHandler(self,template_values).get()
            return
        elif(re.match(r'/sendmessage', path)):
            SendHandler(self,template_values).get()
            return
        else:
            m = re.match(r'/(book|user|class)/(.+)$', self.request.path)
            if(m):
                SubjectHandler(self, template_values).get()
                return
            elif(self.request.path == "/import"):
                ImportHandler(self, template_values).get()
                return
            else:
                self.redirect("/")

        try:
            self.response.out.write(render_template(template_values, page))
        except Exception, e:
            self.redirect("/signup_page?redirect=/&reason="+str(e))

    

apps_binding = []
apps_binding.append(('/image', GetImage))
#apps_binding.append(('/db_print', PrintDB))
#apps_binding.append(('/reset', ClearDB))
apps_binding.append(('/getbooksforclass', ClassHandler))
#apps_binding.append(('/get_classes', InitialSetup))
apps_binding.append(('/data', GetData))
apps_binding.append(('/act.*', UserAction))
apps_binding.append(('/login', UserManagement))
apps_binding.append(('/logout', UserManagement))
apps_binding.append(('/signup', UserManagement))
apps_binding.append(('/signup_page', UserManagement))
#apps_binding.append(('/change_password.*', UserManagement))
apps_binding.append(('/setup_cl', SetupCL))
apps_binding.append(('/get_departments', GetDepartments))
apps_binding.append(('/verify.*', UserManagement))
apps_binding.append(('.*', MainPage))

application = webapp.WSGIApplication(apps_binding, debug=False)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()