import base64
import cgi
import os
import fix_path
import hashlib
import random
import re
 
from exceptions import VerificationNeededException
from exceptions import BadUserException
from exceptions import UnregisteredException
from time import time
from tools import render_template
from cookies import Cookies
from send_email import SendEmail
from model.model import User
from model.model import Sessions

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.db import Key
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class UserManagement(webapp.RequestHandler):
    def __init__(self, handler=None):
        self.hashid = '_utmh'
        if(handler):
            self.cookies = Cookies(handler, max_age=86400)
            self.request = handler.request
            
    def get(self):
        self.cookies = Cookies(self,max_age=86400)
        render_template(None, 'view/footer.html')
        render_template(None, 'view/header.html')
        render_template(None, 'view/scripts.html')
        template_values = {}
        page = "view/"
        try:
            if(re.match('/login',self.request.path)):
                page += "login.html"
                self.response.out.write(render_template(template_values, page))
            elif(re.match(r'/signup_page', self.request.path)):
                page+="signup_page.html"
                template_values['redirect']=self.request.get("redirect")
                self.response.out.write(render_template(template_values, page))
            elif(re.match('/signup',self.request.path)):
                page += "signup.html"
                self.response.out.write(render_template(template_values, page))
            elif(re.match('/logout',self.request.path)):
                self.logout()
                self.redirect('/')
            elif(re.match('/act_test',self.request.path)):
                self.test()
            elif(re.match('/verify/([^/]+)/([^/]+)/?',self.request.path)):
                m = re.match('/verify/([^/]+)/([^/]+)/?',self.request.path)
                self.verify(m.group(1), m.group(2))
                self.redirect('/profile')
            elif(re.match('/verify/([^/]+)/?',self.request.path)):
                m = re.match('/verify/([^/]+)/?',self.request.path)
                page += "verify.html"
                template_values = {'user_key': m.group(1), 'verify_again': self.request.path.replace("verify","verify_again")}
                self.response.out.write(render_template(template_values, page))
            elif(re.match('/verify_again/([^/]+)/?',self.request.path)):
                m = re.match('/verify_again/([^/]+)/?',self.request.path)
                user = User.get(Key(m.group(1)))
                SendEmail().sendVerificationEmail(user, self.getUserHash(user))
                self.redirect('/complete')
            elif(re.match('/verify', self.request.path)):
                page += "verify.html"
                self.response.out.write(render_template(template_values, page))
            elif(re.match('/change_password/([^/]+)/([^/]+)',self.request.path)):
                m = re.match('/change_password/([^/]+)/([^/]+)',self.request.path)
                page += "change_password.html"
                template_values['user_key'] = m.group(1)
                template_values['change_key'] = m.group(2)
                self.response.out.write(render_template(template_values, page))
            elif(re.match('/change_password',self.request.path)):
                page += "change_password.html"
                self.response.out.write(render_template(template_values, page))
        except Exception, e:
            self.redirect('/error?type='+str(e))

    def post(self):
        self.cookies = Cookies(self,max_age=86400)
        name = self.request.get("user[name]")
        ip = self.request.remote_addr
        email = self.request.get("user[email]")
        password = self.request.get("user[key2]")
        password = base64.b64decode(password)
        new_password = self.request.get("user[new_pass]")
        verify = self.request.get("user[verify]")
        key = self.request.get("user[key]")
        redirect = self.request.get("redirect")
        error = self.request.get("redirect")
        if not redirect:
            redirect = "/complete"
        try:
            if(re.match('/login',self.request.path)):
                try:
                    self.login(email,password,ip)
                    self.redirect(redirect)
                except VerificationNeededException,e:
                    self.redirect('/verify/'+str(e).replace("'",""))
            elif(re.match('/signup',self.request.path)):
                self.signup(name,email,password)
                self.redirect('/complete?justsignedup=1')
            elif(re.match('/change_password/([^/]+)/([^/]+)',self.request.path)):
                m = re.match('/change_password/([^/]+)/([^/]+)',self.request.path)
                user = User.gql(Key(m.group(1)))
                hash = m.group(2)
                self.change_password(user, hash, new_password)
                self.redirect('/complete')
            elif(re.match('/change_password',self.request.path)):
                user = self.getUser()
                if user.password == self.getEncryptedPass(user.cubmail, password):
                    self.change_password(user, None, new_password)
                    self.redirect('/complete')
                else:
                    raise Exception("Wrong password ")
            elif(re.match('/verify',self.request.path)):
                if password:
                    self.verify(email, password, verify)
                else:
                    self.verify(key, verify)
                self.redirect('/complete')
        except Exception, e:
            if error:
                self.redirect(error)
            else:
                self.redirect("/error?type=%s"%str(e))
    # now for the meat
    
    def emailToChange(self, user):
        hash = self.getHash()
        session = Sessions(ip="changepass", hash=hash, user=user)
        SendEmail().sendChangePasswordEmail(user,hash)
        
    def change_password(self, user, key, new_password):
        new_passw = self.getEncryptedPass(user.cubmail, new_password)
        if key:
            ip = "changepass"
            hash = key
            session = Sessions.gql("WHERE ip=:1 AND hash=:2",ip,hash).get()
            if session and session.user.cubmail == user.cubmail:
                self.changePass(user.name, user.cubmail, user.password, new_passw)
                db.delete(session)
            else:
                raise Exception("Expired session")
        else:
            self.changePass(user.name, user.cubmail, user.password, new_passw)
                
                
    def signup(self, name, cubmail, password):
        if not (name and cubmail and password):
            raise BadUserException('No info provided')
        user = self.getUserByCubmail(cubmail)
        if user:
            raise BadUserException('User already signed up.')
        return self.addNewUser(name, cubmail, password)
    
    def isLoggedIn(self):
        return self.getUser()!=None
    
    def logout(self):
        if not self.isLoggedIn():
            return
        try:
            self.removeSessions(self.cookies[self.hashid])
            del self.cookies[self.hashid] #Delete a cookie from pending request and client browser
        except KeyError, e:
            return
    
    def login(self, cubmail, password, ip):
        user = self.getUserByCubmail(cubmail)
        passw = self.getEncryptedPass(cubmail, password)
        
        if user and passw == user.password:
            if user.level == 0:
                raise VerificationNeededException(str(user.key()))
            hash = self.getHash()
            self.addSessionUser(ip, hash, user)
            self.cookies[self.hashid] = hash
        elif user:
            raise BadUserException('Wrong password.')
        else:
            raise UnregisteredException('Not registered')
    
    def verifyEmail(self, cubmail, password, hash):
        user = self.getUserByCubmail(cubmail)
        passw = self.getEncryptedPass(cubmail, password)
        if user and passw == user.password:
            self.verify(user.key(), hash)
        
    def verify(self, user_key, hash, i=None):
        if i:
            return verifyEmail(user_key, hash, i)
        user = db.get(Key(user_key))
        if not user:
            raise BadUserException('Invalid user')
        s = Sessions.gql("WHERE ip='verify' AND hash=:1 AND user=:2",hash,user).get()
        if s:
            user.level = 1
            user.put()
            self.addSessionUser(self.request.remote_addr, hash, user)
            self.cookies[self.hashid] = hash
            db.delete(s)
        else:
            raise BadUserException('No session found for this user.')
            
    
    def getHash(self):
        m = hashlib.md5()
        n = str(random.random())
        m.update(n)
        return m.hexdigest()
    
    def addNewUser(self, name, cubmail, password):
        user = self.getUserByCubmail(cubmail)
        if user:
            raise Exception("user exists")
        if re.search("@(columbia|barnard).edu",cubmail):
            hash = self.getHash()
            user = self.addUser(name, db.Email(cubmail), self.getEncryptedPass(cubmail,password), hash)
            SendEmail().sendVerificationEmail(user, hash)
            return hash
        else:
            raise Exception("Not a valid email")
        
    def addUser(self, name, cubmail, passw, verification):
        user = User.gql("WHERE name=:1 AND cubmail=:2 AND password=:3", name, cubmail,passw).get()
        if not user:
            user = User(name = name, cubmail=cubmail, password = passw, level=0)
            user.put()
            self.addSessionUser('verify', verification, user)
        return user
    
    def changePass(self,name, cubmail, old_encrypt_passw, new_encrypt_passw):
        user = User.gql("WHERE name=:1 AND cubmail=:2 AND password=:3", name, cubmail,old_encrypt_passw).get()
        if user:
            user.password = new_encrypt_passw
            user.put()
            SendEmail().sendChangedPass(user)
        return user
    
    def removeUser(self, name, cubmail, passw):
        user = User.gql("WHERE name = :1 AND cubmail=:2 AND password=:3",name,cubmail,passw).get()
        if user:
            for i in Sessions.gql("WHERE user = :1",user):
                db.delete(i)
            db.delete(user)
    
    def removeSessions(self, hash):
        s = Sessions.gql("WHERE hash=:1",hash).get()
        if s:
            u = s.user
            s = Sessions.gql("WHERE user=:1",u)
            db.delete(s)
        
    def getUserByCubmail(self, cubmail):
        return User.gql("WHERE cubmail=:1", cubmail).get()
    
    def getUserHash(self, user):
        if not user:
            raise BadUserException("User not found.")
        session = Sessions.gql("WHERE ip='verify' AND user=:1",user).get()
        if session:
            return session.hash
        else:
            raise BadUserException("User not found.")

        
    def getEncryptedPass(self, cubmail, password):
        m = hashlib.sha256()
        m.update(cubmail)
        m.update(password)
        return m.hexdigest()
    
    
    def addSessionUser(self, ip, hash, user):
        session = Sessions()
        session.ip = ip
        session.hash = hash
        session.user = user
        session.put()
        return session
    
    def getUser(self):
        try:
            self.cookies[self.hashid]
        except KeyError, e:
            return None
        ip = self.request.remote_addr
        hash = self.cookies[self.hashid]
        session = Sessions.gql("WHERE ip=:1 AND hash=:2",ip,hash).get()
        if session:
            return session.user        