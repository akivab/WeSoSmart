import urllib2
import re
from HTMLParser import HTMLParser

class DeptParser(HTMLParser):
    start = False
    list = []
    
    def handle_starttag(self, tag, attrs):
        if not (self.start):
            if (snd(attrs) and "#DADADA" == snd(attrs)):
                self.start = True
                
        if(self.start and re.search(r'a', tag)):
            if not (re.search(r"(_top|home.html|/about/)$", snd(attrs))):
                    self.list.append(snd(attrs))
                
    def getList(self):
        return self.list

class ClassParser(HTMLParser):
    list = []
    def handle_starttag(self, tag, attrs):
        if(len(attrs) > 0 and len(attrs[0]) >1 and "href"==fst(attrs)):
            if not (re.search(r'COURSES', snd(attrs))):
                self.list.append(snd(attrs))

    def getList(self):
        return self.list

class SectionParser(HTMLParser):
    details_list = []

    current_subject = None
    set_current_subject = False

    title = None
    set_title = False
    
    def handle_starttag(self,tag,attrs):
        if(tag == "tr"):
            self.current_subject = None
            self.set_current_subject = False
        elif(tag == "td"):
            if not self.current_subject:
                self.set_current_subject = True
            else:
                self.set_current_subject = False
        elif(tag == "meta" and not self.title):
            if(attrs[0][1]=="description"):
                s = re.search("^([^;]+)", attrs[1][1])
                self.title = s.group(1).strip()
                self.details_list.append(("Title", self.title))
            else:
                self.details_list = []                
                
    def handle_data(self,data):
        if not (re.search(r'^\s*$', data)):
            if self.set_current_subject:
                self.current_subject = data
            elif self.current_subject:
                if(re.search(r'.*\d\:\d+[ap]m',data)):
                    self.details_list.append(("Time", data))
                else:
                    self.details_list.append((self.current_subject, data))

    def getDetailsList(self):
        return self.details_list
    
def snd(list):
    if(len(list) > 0 and len(list[0])>1):
        return list[0][1]
    return None
    
def fst(list):
    if(len(list) > 0 and len(list[0])>1):
        return list[0][0]
    return None
    
class GetClasses():
    class_list = []
    section_list = []
    def get(self):
        for i in range(ord("A"),ord("B")):
            url = "http://www.columbia.edu/cu/bulletin/uwb/sel/subj-%s.html" % chr(i)
            
            try:
                result = urllib2.urlopen(url)
                parser = DeptParser()
                parser.feed(result.read())
                self.class_list = parser.getList()
            except urllib2.URLError, e:
                self.handleError(e)
                
        for i in self.class_list:
            url = "http://www.columbia.edu" + i.replace(".html","_text.html");
            try:
                result = urllib2.urlopen(url)
                parser = ClassParser()
                parser.feed(result.read())
                self.section_list = parser.getList()
            except urllib2.URLError, e:
                self.handleError(e)
                
        for i in self.section_list:
            url = "http://www.columbia.edu" + i
            try:
                result = urllib2.urlopen(url)
                s = re.search('([A-Z]+)/([^-]+)-([^-]+)-([^/]+)/$', url)
                url_info = [("Dept", s.group(1)),
                 ("Semester", s.group(3))]
                parser = SectionParser()
                parser.feed(result.read())
                url_info.extend(parser.getDetailsList())
                self.section_list.append(url_info);

            except urllib2.URLError, e:
                self.handleError
    def get_section_details(self):
        return self.section_list
    def doSomethingWithResult(self, thing):
        print thing
    def handleError(self, error):
        print "error"

class GetBooks():
    profs = None
    books = None
    def getFor(self, section):
        try:
            site = "http://courseworks.columbia.edu/public/"+section
            result = urllib2.urlopen(site)
            s = result.geturl().replace("courseenter","intro_out")
            s = s.replace("?no=","?crs=");
            result = urllib2.urlopen(s);
            parser = BookParser()
            parser.feed(result.read())
            self.books = [section]
            self.profs = [section]
            self.books.extend(parser.getBookList())
            self.profs.extend(parser.getProfList())
        except urllib2.URLError, e:
            self.handleError
    def getProfs(self):
        return self.profs
    def getBooks(self):
        return self.books

class BookParser(HTMLParser):
    current = None
    current_tag = None
    isbn = None
    prof_mail = None
    prof_name = None
    necessary = ""
    tmp = ""
    bookList = []
    profList = []

    def getBookList(self):
        return self.bookList
    def getProfList(self):
        return self.profList
    
    def handle_starttag(self,tag,attrs):
        self.current_tag = tag
        if(tag == "tr"):
            self.isbn = None
            self.title = None
            self.author = None
            self.price = None
    def handle_data(self,data):
        if(re.match(r'^\s*$', data)):
            return
        data = data.strip()
        if re.search('Instructor Information',data):
            self.current = "prof name"
            self.prof_name = None
            self.tmp = ""
        elif(self.current and re.search(r'prof', self.current)):
            if(re.search(r'name', self.current)):
                if(re.search('Professor|Telephone|\d|E-mail',data)):
                    if not self.prof_name:
                        self.prof_name = self.tmp
                    if(re.search('E-mail', data)):
                        self.current = "prof mail"
                    self.tmp = ""
                else:
                    if not (self.tmp == ""):
                        self.tmp+=" "
                    self.tmp += data
            elif(re.search('@',data)):
                self.prof_mail = data
                self.profList.append([("name", self.prof_name), ("email", self.prof_mail)])
                self.tmp = ""
                self.current = self.current_tag
        elif(self.current_tag == "strong"):
            self.necessary = data
        elif(self.necessary): 
            if(self.necessary and re.match(r'\d{13}', data)):
                self.isbn = data
            elif(self.isbn and not self.title):
                self.title = data
            elif(self.isbn and not self.author):
                match = re.search(r'[A-Z](([A-Z]|[^.;]|[a-z]|\s)+)', data)
                if(match):
                    self.author = match.group(0).strip()
                else:
                    self.title = self.title + " " + data
            elif(re.match(r'\$', data)):
                self.price = data[1:]
                thisList = [("req", self.necessary),
                     ("isbn", self.isbn),
                     ("title", self.title),
                     ("author", self.author),
                     ("price", self.price)]
                self.bookList.append(thisList)
            else:
                self.current = self.current_tag

#g = GetBooks()
#g.getFor("20103ARCH6170A001")
#g = GetClasses()
#g.get()
#FILE = open("tmp.html","r", 0)
#parser = BookParser()
#parser.feed(''.join(FILE.readlines()))
#print parser.getBookList()
#print parser.getProfList()
