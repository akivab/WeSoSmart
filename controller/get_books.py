'''
Created on Jan 10, 2011

@author: akiva
'''
import xml.parsers.expat
import urllib
import urllib2
import base64
import re
from google.appengine.ext import webapp
from model.model import CL
from model.model import Picture

class BookXmlHandler:
    def __init__ (self):
        self.p = xml.parsers.expat.ParserCreate()
        self.p.CharacterDataHandler = self.characters
        self.p.StartElementHandler = self.startElement
        self.p.EndElementHandler = self.endElement
        self.to_set = None
        self.image = None
        self.title = None
        self.author = None
        self.description = None
        self.prev = None
    def parse(self, xml_data):
        self.p.Parse(xml_data)
    def startElement(self, name, attrs):
        if(name == "dc:title"):
            self.to_set = "title"
        elif(name == "dc:creator"):
            self.to_set = "author" 
        elif(name == "dc:description"):
            self.to_set = "description"
        elif(name == "link" and re.search(r'thumbnail',attrs["rel"])):
            self.image = str(attrs["href"])
        elif(name == "link" and re.search(r'preview|info',attrs["rel"])):
            self.prev = str(attrs["href"])
    def characters(self, chars):
        if(self.to_set == "author"):
            if(self.author):
                self.author = self.author + ", "+chars
            else:
                self.author = chars
        elif(self.to_set == "title"):
            if(self.title):
                self.title = self.title + " " +  chars
            else:
                self.title = chars
        elif(self.to_set == "description"):
            if(self.description):
                self.description = self.description + " " + chars
            self.description = chars 
    def endElement(self, name):
        self.to_set = None
    def printAll(self):
        print self.title
        print self.author
        print self.description
        print self.image
        print self.prev

    def setBook(self,b):
        b.title = self.title
        b.name = self.title
        b.author = self.author
        b.description = self.description
        pic = b.getPictureLink()
        if not pic:
            pic = Picture(link = self.image)
            pic.put()
            b.picture = pic
        b.prev = self.prev
        b.put()
        
class SetupCL(webapp.RequestHandler):
    def get(self):
        key = "D77"
        str1 = "5061737377643%s737369737468656265737426736F757263653%s65736F736D6172742D3126736572766963653D7072696E7426456D61696C3%s65736F736D61727431253430676D61696C2E636F6D264163636F756E74547970653D484F535445445F4F525F474F4F474C45" % (key,key,key)
        str2 = "aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS9hY2NvdW50cy9DbGllbnRMb2dpbg=="
        req = urllib2.urlopen(urllib2.Request(base64.b64decode(str2),
                                              base64.b16decode(str1)))
        m = re.search('Auth=(\S+)', req.read())
        try:
            c = CL(auth = m.group(1))
            c.put()
            print "success."
        except Exception, e:
            print "failed: " + str(e)
        
class GetBooks(webapp.RequestHandler):
    def __init__(self):
        self.auth = CL.gql("ORDER BY time DESC").get().auth
        self.base_url = 'http://books.google.com/books/feeds/volumes?q=isbn:'
        self.headers = { 'Authorization' : 'GoogleLogin auth='+self.auth }
    def setBookInfo(self, b):
        isbn = b.isbn
        url = self.base_url + isbn + "&lr=en"
        req = urllib2.Request(url, None, self.headers);
        response = urllib2.urlopen(req)
        the_page = response.read()
        parser = BookXmlHandler()
        parser.parse(the_page)
        parser.setBook(b)
    def get(self):
        url = self.base_url+self.request.get("isbn")+"&lr=en"
        req = urllib2.Request(url, None, self.headers)
        response = urllib2.urlopen(req)
        the_page = response.read()
        parser = BookXmlHandler()
        parser.parse(the_page)
        parser.printAll()
