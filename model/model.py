import re
import random

from controller.send_email import SendEmail
from google.appengine.api import memcache
from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable
        
class Picture(db.Model):
    data = db.BlobProperty()
    link = db.StringProperty()
    def addPicture(blob):
        picture = Picture(data = blob)
        picture.put()
        picture.link = "/image?s="+str(picture.key())
        picture.put()
        return picture
    addPicture=Callable(addPicture)
                    

class Subject(polymodel.PolyModel):
    name = db.StringProperty()
    description = db.StringProperty()
    picture = db.ReferenceProperty(Picture)
    time = db.DateTimeProperty(auto_now_add=True)
    def getPictureLink(self):
        if self.picture:
            return self.picture.link

class User(Subject):
    cubmail = db.EmailProperty()
    nick = db.StringProperty()
    email = db.EmailProperty()
    # level is 0 upon first registering.
    # level is 1 for those who want greatest privacy
    # level is 2 for those who want greatest publicity (and professors)
    level = db.IntegerProperty()
    password = db.StringProperty()
    def getData(self):
        data = []
        data.append(("h2 class='head'", "Professor" if self.level==2 else "Student"))
        data.append(("a href='mailto:"+self.cubmail+"'", self.cubmail))
        return data
    def __str__(self):
        return str(self.getData())

class Sessions(db.Model):
    hash = db.StringProperty()
    ip = db.StringProperty()
    user = db.ReferenceProperty(User)
    time = db.DateTimeProperty(auto_now_add=True)    
    
class Class(Subject):
    dept = db.StringProperty()
    dept_name = db.StringProperty()
    division = db.StringProperty()
    open_to = db.StringProperty()
    campus = db.StringProperty()
    type = db.StringProperty()
    points = db.StringProperty()
    max_points = db.IntegerProperty()
    number = db.StringProperty()

class CL(db.Model):
    auth = db.StringProperty()
    time = db.DateTimeProperty(auto_now_add=True)
    
class Section(Class):
    semester = db.StringProperty()
    section = db.StringProperty()
    call_num = db.StringProperty() 
    location = db.StringProperty()
    class_time = db.StringProperty()
    approvals = db.StringProperty()
    instructor = db.StringProperty()
    section_key = db.StringProperty()
    note = db.StringProperty()
    class_id = db.ReferenceProperty(Class)

class Book(Subject):
    isbn = db.StringProperty()
    title = db.StringProperty()
    author = db.StringProperty()
    price = db.FloatProperty()
    prev = db.StringProperty()
    
class UserBooks(db.Model):
    user_id = db.ReferenceProperty(User)
    book_id = db.ReferenceProperty(Book)
    # 0 is want, 1 is have
    status = db.IntegerProperty()
    price = db.StringProperty()
    time = db.DateTimeProperty(auto_now_add=True)
        
    def getForHomepage(self):
        name = self.user_id.name
        m=re.match(r'^(\S+)',name)
        if m:
            name = m.group(1)
        pic = self.book_id.getPictureLink()
        if not pic:
            pic = "/img/b8.jpg"
        data = ( "/book/"+str(self.book_id.key()), pic, "/user/"+str(self.user_id.key()), name,  
                str("wants" if self.status == 0 else "has"), "/book/"+str(self.book_id.key()),
                self.book_id.title, "%s%s"%("$" if (self.price and self.price[:1]!="$") else ("for " if self.price else ""), self.price if self.price else ""))
        return "<div class='recent_activity_item'><a href='%s'><img src='%s' /></a><div class='recent_activity_text'><a href='%s'>%s</a> %s <a href='%s'>%s</a> %s</div></div>" % data
    
    def getRecent(self, num):
        recent = UserBooks.all()
        recent.order('-time')
        
        toreturn = [i.getForHomepage() for i in recent[:num]]
        return toreturn
    def getUsers(book, status):
        return [i.user_id for i in UserBooks.gql("WHERE book_id=:1 AND status=:2", book,status)]
    def __str__(self):
        return str(users) + str(self.getData())               
    getUsers = Callable(getUsers)         
    
class ClassBooks(db.Model):
    section_id = db.ReferenceProperty(Section)
    book_id = db.ReferenceProperty(Book)
    req = db.StringProperty()


class UserClasses(db.Model):
    STUDENT, PROFESSOR = range(2)
    user_id = db.ReferenceProperty(User)
    section_id = db.ReferenceProperty(Section)
    relationship = db.IntegerProperty()
    grade = db.StringProperty()
    
class UserUsers(db.Model):
    user_id = db.ReferenceProperty(User)
    userbook_id = db.ReferenceProperty(UserBooks)
    message = db.StringProperty(multiline=True)
    level = db.IntegerProperty()
    time = db.DateTimeProperty(auto_now_add=True)
    def addMessage(user,ub, message):
        UserUsers(user_id=user,userbook_id=ub,message=message).put()
        SendEmail().sendBookMsg(user,ub,message)
    addMessage=Callable(addMessage)

class Comment(Subject):
    user_id = db.ReferenceProperty(User)
    subject_id = db.ReferenceProperty(Subject)
    subject_type = db.StringProperty()
    comment = db.StringProperty(multiline=True)
    file = db.ReferenceProperty()
    public = db.IntegerProperty()
    depth = db.IntegerProperty()
    def getRecent():
        comments = []
        for i in Comment.all().order('-time')[:5]:
            m = i.subject_id
            while(True):
                try:
                     m = m.subject_id
                except Exception, e:
                    comments.append(Comment(user_id = i.user_id, subject_id=m, comment=i.comment, subject_type=i.subject_type))
                    break
        return comments 

    def addComment(user, subject, subject_type, comment,file=None):
        other = Picture(link="/img/b"+str(random.randrange(1,8))+".jpg")
        
        if user.picture:
            file = user.picture
        else:
            file = other.put()
        
        newcomment = Comment(user_id=user,subject_id=subject, comment=comment, subject_type=subject_type, file=file)
        newcomment.put()
        
        m = db.get(subject)
        
        while(True):
                try:
                    m = m.subject_id
                except Exception, e:
                    try:
                        m.cubmail
                        SendEmail().sendEmailAboutComment(m, user, comment, subject_type, m.key())
                    except Exception, e:
                        pass
                    break
        try:
            m = db.get(subject)
            to_email = m.user_id
            SendEmail().sendEmailAboutComment(to_email, user, comment, subject_type, m.key())
        except Exception, e:
            pass
        
    def getComments(subject_id, depth=0):
        comments = Comment.gql("WHERE subject_id = :1 ORDER BY time ASC", subject_id)
        toReturn = []
        for comment in comments:
            comment.depth = depth
            comment.put()
            toReturn.append(comment)
            replies = Comment.getComments(comment, depth+1)
            toReturn.extend(replies)
        return toReturn
    def erase(comment):
        if Comment.gql("WHERE subject_id=:1",comment).get():
            comment.file = Picture(link="/img/b"+str(random.randrange(1,8))+".jpg").put()
            comment.comment = "[deleted]"
            comment.put()
        else:
            db.delete(comment)
    erase = Callable(erase)
    getRecent = Callable(getRecent)
    addComment = Callable(addComment)
    getComments = Callable(getComments)