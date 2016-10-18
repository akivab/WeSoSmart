import re
import hashlib

import json
from cgi import escape
# for the GetBooks section
from get_books import GetBooks
# for the PrintDB, ClearDB, and InitialSetup sections
from model.model import *
from google.appengine.ext.db import Key
from google.appengine.ext import webapp


def getSections(myclass):
    if re.search('COCI', myclass.dept):
        sections = Section.gql("WHERE section_key in ('20103COCI1101C040','20111COCI1102C034')")
    elif re.search('HUMA', myclass.dept):
        if re.search('1001|1002', myclass.number):
            sections =  Section.gql("WHERE section_key in ('20111HUMA1002C015','20103HUMA1001F059')")
        else:
            sections = Section.gql("WHERE class_id=:1",myclass)
    else:
        sections = Section.gql("WHERE class_id=:1",myclass)
    return sections

class GetData(webapp.RequestHandler):
    def post(self):
        toreturn = []
        if(self.request.get("dept")):
            dept = self.request.get("dept");
            if(re.match(r'[A-Z]{4}', dept)):
                    courses = Class.gql("WHERE dept=:1 ORDER BY name ASC", dept)
                    toreturn.append("("+str(courses.count())+") " + GetDepartments().get_dept_name(dept))
                    for k in courses:
                        toreturn.append(str(k.key()))
                        toreturn.append(k.number+ ": "+ k.name);
        elif(self.request.get("course")):
            course = self.request.get("course");
            myclass = Class.get(Key(course))
            sections = Section.gql("WHERE class_id=:1 ORDER BY semester DESC",myclass)
            toreturn.append(myclass.dept)
            toreturn.append(myclass.number)
            toreturn.append(myclass.name)
            for k in sections:
                prof_ids = UserClasses.gql("WHERE section_id=:1 AND relationship=:2",k,UserClasses().PROFESSOR)
                instructors = []
                for p in prof_ids:
                    prof = p.user_id
                    instructors.append(str(prof.key()))
                    instructors.append(prof.name)
                if(instructors):
                    toreturn.append(instructors)
                else:
                    toreturn.append(getst(k.instructor, "No instructor found"))
                toreturn.append(getst(k.location, "No location found"))
                toreturn.append(getst(k.class_time, "No time found"))
                toreturn.append(getst(str(k.key()), "No key found"))
                toreturn.append(getst(k.semester, "No semester found"))
        elif(self.request.get("books")):
            course = self.request.get("books")
            myclass = Class.get(Key(course))
            sections = getSections(myclass)
            books = []
            for k in sections:
                for classbook in ClassBooks.gql("WHERE section_id=:1",k):
                    try:
                        books.index(classbook.book_id)
                    except ValueError,e:
                        books.append(classbook.book_id)
            for b in books:
                if not b.name:
                    b.name = b.title
                if not b.prev or not b.picture:
                    try:
                        GetBooks().setBookInfo(b)
                        toreturn.append(str(b.picture.link))
                        toreturn.append(str(b.prev))
                    except Exception, e:
                        toreturn.append("/img/b8.jpg")
                        toreturn.append("/error?type='Page not found'")
                else:
                   toreturn.append(str(b.picture.link))
                   toreturn.append(str(b.prev))
                toreturn.append(b.title)
                toreturn.append(b.author)
                toreturn.append(b.description)
                toreturn.append("%.2f" % b.price)
                toreturn.append(str(b.key()))
        self.response.out.write(json.dumps(toreturn))

def getst(string, default):
    if(string):
        return string
    else:
        return default

class ClearDB(webapp.RequestHandler):
    def get(self):
        password = self.request.get("pass")
        m = hashlib.sha256()
        m.update(password)
        if(m.hexdigest() == '158189b0767fc7104d28a1848ca958828136ed4692cafa4120f49f49d836bd61'):
            db.delete(Subject.all())
            db.delete(UserBooks.all())
            db.delete(UserClasses.all())
            db.delete(ClassBooks.all())
            print "Success!"
        else:
            self.redirect("/")

class GetBookData(webapp.RequestHandler):
    def get(self):
        password = self.request.get("pass")
        m = hashlib.sha256()
        m.update(password)
        print "hello!"
        if(m.hexdigest() == '158189b0767fc7104d28a1848ca958828136ed4692cafa4120f49f49d836bd61'):
            books = Book.all()
            for i in books:
                GetBooks().setBookInfo(i)
                print "Got book data for %s" % i.title
            print "Success!"
        else:
            print "Can't do it!"

class PrintDB(webapp.RequestHandler):
    def get(self):
        print "<br>"
        print ''.join(['-' for _ in xrange(36)]),"Books",''.join(['-' for _ in xrange(36)])
        print "<br>"
        for k in Book.all():
            print k.isbn,"|",k.title, "|", k.price
            print "<br>"
        print ''.join(['-' for _ in xrange(36)]),"Classes",''.join(['-' for _ in xrange(36)])
        print "<br>"
        for k in Class.all():
            if(k.name):
                print k.name, "|", k.dept, "|", k.dept_name
                print "<br>"
        print ''.join(['-' for _ in xrange(36)]),"Users",''.join(['-' for _ in xrange(36)])
        print "<br>"
        for k in User.all():
            print k.name
            print "<br>"
        print ''.join(['-' for _ in xrange(36)]),"Sections",''.join(['-' for _ in xrange(36)])
        print "<br>"
        for k in Section.all():
            print k.section_key, "|", k.instructor
            print "<br>"
        print ''.join(['-' for _ in xrange(36)]),"UserClasses",''.join(['-' for _ in xrange(36)])
        print "<br>"
        for k in UserClasses.all():
            print "UserClass Entry"
            print "<br>"
        print ''.join(['-' for _ in xrange(36)]),"ClassBooks",''.join(['-' for _ in xrange(36)])
        print "<br>"
        for k in ClassBooks.all():
            print "ClassBooks Entry"
            print "<br>"
        print ''.join(['-' for _ in xrange(80)])
        print "<br>"

class InitialSetup(webapp.RequestHandler):
    def get(self):
        l = []
        type = self.request.get("type")
        for i in self.request.arguments():
            if(i != "type"):
                l.append((i, self.request.get(i)))
        if(type == "profs"):
            self.addProf(l)
        elif(type == "books"):
            self.addBook(l)
        elif(type == "section"):
            self.addSection(l)
        print self.request.query_string
    def addProf(self, data):
        section_key = self.request.get("section")
        section = Section.gql("WHERE section_key = :1", section_key).get()
        for attr in data:
            if(attr[0] == "name"):
                name_ = escape(attr[1])
            elif(attr[0] == "email"):
                m = re.match(r'(\S+)', attr[1])
                mail_ = m.group(1)
        professor = User.gql("WHERE cubmail = :1", db.Email(mail_)).get()
        if not professor:
            professor = User(name = name_, cubmail = db.Email(mail_), level = 2)
            professor.put()
        userclasses = UserClasses.gql("WHERE user_id = :1 AND section_id=:2", professor, section).get()
        if not userclasses:
            userclasses = UserClasses(user_id = professor, section_id = section, relationship = UserClasses().PROFESSOR)
            userclasses.put()


    def addBook(self, data):
        section_key = self.request.get("section")
        section = Section.gql("WHERE section_key = :1", section_key).get()
        for attr in data:
            print attr
            if(attr[0] == "req"):
                req_ = attr[1]
            elif(attr[0] == "isbn"):
                isbn_ = attr[1]
            elif(attr[0] == "title"):
                title_ = escape(attr[1])
            elif(attr[0] == "author"):
                author_ = escape(attr[1])
            elif(attr[0] == "price"):
                try:
                    price_ = float(attr[1])
                except Exception:
                    price = float(100)
        book = Book.gql("WHERE isbn = :1", isbn_).get()
        if not book:
            book = Book(isbn = isbn_, title = title_, author = author_, price = price_)
            book.put()
        classbooks = ClassBooks.gql("WHERE book_id=:1 AND section_id=:2", book, section).get()
        if not classbooks:
            classbooks = ClassBooks(req = req_, book_id = book, section_id = section)
            classbooks.put()

    def addSection(self, data):
        dept_ = ""
        dept_name_ = ""
        points_ = ""
        number_ = ""
        division_ = ""
        instructor_ = ""
        open_to_ = ""
        campus_ = ""
        section_ = ""
        location_ = ""
        time_ = ""
        approvals_ = ""
        note_ = ""
        section_key_ = ""
        call_num_ = ""
        name_ = ""
        type_ = ""
        for datum in data:
            # department information
            if(len(datum) > 0 and datum[0] == "Dept"):
                dept_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Department"):
                dept_name_raw = datum[1]
                dept_name_ = re.search(r'^([^,]+)', dept_name_raw).group(1)
            elif(len(datum) > 0 and datum[0] == "Points"):
                points_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Number"):
                number_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Division"):
                division_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Open To"):
                open_to_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Type"):
                type_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Title"):
                name_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Campus"):
                campus_ = datum[1]

            # section information
            elif(len(datum) > 0 and datum[0] == "Section"):
                section_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Semester"):
                semester_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Location"):
                location_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Time"):
                time_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Instructor"):
                instructor_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Approvals Required"):
                approvals_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Note"):
                note_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Section key"):
                section_key_ = datum[1]
            elif(len(datum) > 0 and datum[0] == "Call Number"):
                call_num_ = datum[1]

        myclass = Class.gql("WHERE dept = :1 and number = :2", dept_, number_).get()
        if not myclass:
            myclass = Class()
        myclass.dept = dept_
        myclass.dept_name = dept_name_
        myclass.points = points_
        myclass.number = number_
        myclass.division = division_
        myclass.name = name_
        myclass.type = type_
        myclass.open_to = open_to_
        myclass.campus = campus_
        myclass.put()
        mysection = Section.gql("WHERE section_key = :1", section_key_).get()
        if not mysection:
            mysection = Section()
        mysection.section = section_
        mysection.semester = semester_
        mysection.call_num = call_num_
        mysection.approvals = approvals_
        mysection.instructor = instructor_
        mysection.location = location_
        mysection.class_time = time_
        mysection.note = note_
        mysection.section_key = section_key_
        mysection.class_id = myclass
        mysection.put()

class GetDepartments(webapp.RequestHandler):
    def __init__(self):
        self.department_str ="""
ACCT|Accounting
ACTU|Actuarial Science
AFCV|African Civilization
AFAS|African-American Studies
AFRS|Africana Studies
AFEN|AFRICANA STUDIES/ENGLISH
AKAD|Akkadian
AMST|American Studies
AMHS|American Studies: History
ANCS|Ancient Studies
ANES|ANESTHESIOLOGY
ANTH|Anthropology
ANHS|Anthropology: History
APBM|PPL PHYS & APPL MATH & BMEN
AMCS|APPLIED MATH-COMPUTER SCIENCE
APMA|Applied Mathematics
APPH|Applied Physics
APAM|Applied Physics and Applied Math
ARAM|ARAMAIC
ACLG|Archaeology
ARCH|Architecture
AHIS|Art History
AHLW|ART HISTORY-LAW
AHHS|Art History: History
ASCE|Asian Civilization: East Asian
ASCM|Asian Civilization: Middle East
AHUM|Asian Humanities
AHMM|Asian Humanities: Music
ASST|Asian Studies
ASRL|Asian Studies: Religion
ASAM|Asian-American Studies
ASTR|Astronomy
ASPH|Astronomy and Physics
ACLS|ATHENA CENT FR LEADERSHIP STDS
AUFS|AUDITING-AFRICAN STUDIES
AUAT|AUDITING-ASTRONOMY
AUBI|AUDITING-BIOLOGY
AUCL|AUDITING-CLASSICAL LITERATURE
AUCZ|AUDITING-COMP LIT-CZECH
AUCF|AUDITING-COMP LIT-FRENCH
AUCV|AUDITING-COMP LIT-SLAVIC
AUCS|AUDITING-COMP LIT-SWEDISH
AUEC|AUDITING-ECONOMICS
AUER|AUDITING-ETHNICITY & RACE
AUFL|AUDITING-FILM
AUAN|Auditing: Anthropology
AUAH|Auditing: Art History
AUHA|Auditing: Asian Humanities
AUCC|Auditing: Classical Civilization
AUCA|Auditing: Classics-Art History
AUSL|Auditing: Comparative Literature and Society
AUCE|Auditing: Comparative Literature: English
AUEN|Auditing: English
AUHS|Auditing: History
AUHE|Auditing: History: East Asian
AUMH|Auditing: History: Middle East
AULS|Auditing: Latino Studies
AUMS|Auditing: Music
AUPH|Auditing: Philosophy
AUPS|Auditing: Political Science
AUPY|Auditing: Psychology
AURL|Auditing: Religion
AURS|Auditing: Russian
AUSO|Auditing: Sociology
AUCR|AUDT-CL-RUSS
AWAY|AWAY (HOSPITALS)
JBMP|B MASTER PRJ
BHSC|Behavioral Science
BENG|Bengali
BERK|Berkeley
BCHM|Biochemistry
BIET|BIOETHICS
BICO|BIOLOGICAL CONSERVATION
BIOL|Biology
BIOC|Biology and Chemistry
BMME| MECHANICAL ENGIN
BMEN|Biomedical Engineering
BINF|Biomedical Informatics
BMCH|Biomedical-Chemical Engineering
BMEB|Biomedical-Electrical Engineering-Biology
BIST|Biostatistics
BIOT|BIOTECHNOLOGY
BUSI|Business
BUEC|Business Economics
BUEX|Business Exchange Program
BULW|Business Law
CPRO|C PROGRAMMING
CANT|Cantonese
CATL|Catalan
CMBS|Cellular Molecular Biophysics
CHEN|Chemical Engineering
CHAP|COMP LIT & SOCIETY & PSCC
CHEE|Chemical Engineering and Earth/Environmental Engineering
CHEM|Chemistry
CHNS|Chinese
CIEN|Civil Engineering
CIEE|Civil Engineering and Earth and Environmental Engineering
CLCV|Classical Civilization
CLLT|Classical Literature
CLPH|Classical Philology
CLAH|Classics: Art History
CPMD|CLIN PRAC
COMM|Communications
COPR|COMMUNICATIONS PRACTICE
COMH|Community Health
CLPS| PSCC
CPLT|Comparative Literature
CPLS|Comparative Literature and Society
CLHS|COMPARATIVE LITERATURE-HISTORY
CLCZ|Comparative Literature: Czech
CLEA|Comparative Literature: East Asian
CLEN|Comparative Literature: English
CLFR|Comparative Literature: French
CLGR|Comparative Literature: German
CLGM|Comparative Literature: Greek Modern
CLIA|Comparative Literature: Italian
CLME|Comparative Literature: Middle East
CLRS|Comparative Literature: Russian
CLSL|Comparative Literature: Slavic
CLSP|Comparative Literature: Spanish
CLSW|Comparative Literature: Swedish
COMS|Computer Science
CSEE|Computer Science and Electrical Engineering
CSOR|Computer Science and Operations Research
CBMF|Computer Science, Bioengineering & Med Info
CSPH|Computing Science: Philosophy
CNAD|Construction Administration
COCI|Contemporary Civilization
CORE|Core
CREA|Creative Writing
CZCH|Czech
DNCE|Dance
DRAN|Decision and Risk Analysis
DNSC|Dental Science
DERM|DERMATOLOGY
DTCH|Dutch
EAEE|Earth and Environmental Engineering
ECIA|Earth and Environmental Engineering, Civil Engineering, Inta
EAIA|Earth and Environmental Engineering, Inta
EESC|Earth and Environmental Sciences
EAAS|East Asian
EAST|EAST ASIAN STUDIES
EARL|East Asian: Religion
EEEB|Ecology, Evolution and Environmental Biology
ECON|Economics
ECHS|Economics: History
ECPH|Economics: Philosophy
EDUC|Education
EGYP|Egyptian
EEME|Electrical and Mechanical Engineering
ECBM|Electrical Eng/ Computer Science/ Biomedical Engineering
ELEN|Electrical Engineering
EECS|Electrical Engineering and Computer Science
EEBM|Electrical Engineering: Biomedical
ENDO|Endodontics (DOS)
ENGI|Engineering
ENME|Engineering Mechanics
ENGL|English
ENTH|English Theatre
ENTA|English Theatre Arts
ENRE|English: Religion
ENVB|Environmental Biology
EHSC|Environmental Health Sciences
ENVP|Environmental Policy
EPID|Epidemiology
CSER|Ethnicity and Race, Center for Study of
EXSC|Exchange Scholar
EMPH|EXEC MASTERS IN PUBLIC HEALTH
EXIP|EXECUTIVE INTL PERSPECTIVE
EMPA|Executive MPA Program
EXRS|Extended Residence
FILM|Film
FINC|Finance
FINN|Finnish
FYSB|First-Year Seminar
FLXM|FLEX MARKETS
FLXO|FLEX ORGANIZATIONS
FLXP|FLEX PERFORMANCE
FREN|French
FUND|Fundraising Management
GNPH|General Public Health
GEST|General Studies
GEND|Genetics and Development
GEOR|Georgian
GERM|German
GMTH|GERMAN-THEATRE
PHGH|Global Health Track
GSAS|Graduate School of Arts and Science
GRAP|Graphics
GREK|Greek
GRKM|Greek, Modern
HAUS|HAUSA
HPMN|Health Policy and Management
HIST|History
HPSC|History and Philosophy of Science
HSPB|HISTORY-PUBLIC HEALTH
HSEA|History: East Asian
HSME|History: Middle East
HSPS|History: Political Science
HKNG|HONG KONG
HOSP|HOSPITAL
HSPP|Hughes Science Pipeline Project
HRMG|Human Resource Management
HRTS|Human Rights
HRSL|HUMAN RIGHTS-SLAVIC
HUMA|Humanities
HNGR|Hungarian
IMPL|IMPLANTOLOGY
INST|Independent Study
INDO|Indonesian
IEME|Industrial and Mechanical Engineering
IEOR|Industrial Engineering and Operations Research
IDRM|INFO & DIGITAL RESOURCE MGMT
INSM|Interdepartment Seminar
INTC|Interdisciplinary Correlation
INAF|International Affairs
IALW|INTERNATIONAL AFFAIRS-LAW
INBU|International Business
CORP|INTRO TO CORPORATE VALUATION
IRSH|Irish
ITAL|Italian
JPNS|Japanese
JAZZ|JAZZ STUDIES
JWST|JEWISH STUDIES
JOUR|Journalism
KORN|Korean
KYTO|KYOTO
LAND|Landscape Design
LCRS|LAT AM,CARIB,REGIONAL STUDIES
LATN|Latin
LATS|Latino Studies
LWPS|Law: Political Science
LING|LINGUISTICS
LOND|LONDON
MGMT|Management
MRKT|Marketing
MSAE|Materials Science and Engineering
MATH|Mathematics
MTFC|Matriculation and Facilities
MEBM|MECHANICAL & BIOMEDICAL ENGIN
MECE|Mechanical Engineering
MEDI|MEDECINE
MIMD|Medical Informatics
MEDR|Medieval and Renaissance Studies
MICR|Microbiology
MDES|Middle East
MUSI|Music
NMED|NARRATIVE MEDICINE
NECR|NEGOTIATION & CONFLICT RESOL
NBHV|Neurobiology and Behavior
NEUR|Neurology
NSBV|Neuroscience and Behavior
NURS|Nursing
NUTR|Nutrition
OBSG|Obstetrics & Gynecology (OBSG)
OCCT|Occupational Therapy
OPMN|Operations Management
OPDN|Operative Dentistry
OPHT|Opthalmology
ORBL|Oral Biology
OHMA|ORAL HISTORY MA
ORSG|Oral Surgery
ORTH|Orthodontics
ORTS|Orthopedic Surgery
OTOL|Otolaryngology
PARS|PARIS
PAMD|Pathology (PAMD)
PATH|Pathology (PATH)
PEDI|Pediatric Dentistry
PEDS|Pediatrics (Medical)
PDNT|Periodontics
PHMD|Pharmacology
PHAR|Pharmacology (PHAR)
PHIL|Philosophy
PHED|Physical Education
PHYT|Physical Therapy
PHYS|Physics
PSLG|Physiology
PLAN|Planning
POLI|Polish
POLS|Political Science
POPF|Population and Family Health
PORT|Portuguese
PEPM|Program In Economic Policy Management
PROS|Prosthodontics
PSCA|Psychoanalysis
PSYC|Psychology
PUAF|Public Affairs
PUBH|Public Health
PUNJ|Punjabi
QMSS|Quantitative Methods: Social Sciences
QUCH|QUECHUA
REGN|Regional Institute
REGI|Registered
REID|Reid Hall
RELI|Religion
RSRH|Research
RESI|Residence Unit
RMAN|Romanian
RUSS|Russian
RWJS|RWJ SCHOLARS
SIPA|School of International & Public Affairs
SCNC|Science
SCPP|Science and Public Policy
PSYH|SCIENCE OF PSYCHOLOGY
SCRB|Serbian-Croatian-Bosnian
IAEX|SIPA Exchange Scholar
SLLN|SLAVIC LINGUISTICS
SLLT|Slavic Literatures
SOEN|Social Enterprise
SOCW|Social Work
SOCI|Sociology
SOSC|Sociomedical Sciences
SPAN|Spanish
SPPO|SPANISH-PORTUGUESE
SPRT|Sports Management
STAT|Statistics
SIEO|Statistics, Industrial Eng, & Operations Research
FINM|STOCK MARKET
STOM|Stomatology
STAB|Study Abroad Program
SUMA|SUSTAINABILITY MANAGEMENT
SDEV|Sustainable Development
SWHL|Swahili
SWED|Swedish
TAGA|Tagalog
TMGT|Technology Management
THTR|Theatre
THEA|Theatre Arts
TIBT|Tibetan
UKRN|Ukrainian
URBS|Urban Studies
UTBS|UTS UT BIBLICAL STUDIES
UTCE|UTS UT Christian Ethics
UTCS|UTS UT Church and Society
UTCH|UTS UT Church History
UTCI|UTS UT Church Institutions
UTCW|UTS UT Commun Art and Worship
UTEC|UTS UT Ecumenics
UTNT|UTS UT New Testament
UTOT|UTS UT Old Testament
UTPS|UTS UT Psychiatry and Religion
UTRE|UTS UT Religion and Education
UTST|UTS UT Systematic Theology (UTST)
UTWR|UTS UT Systematic Theology (UTWR)
UTFE|UTS UTS UT Ecumenics
UTBX|UTS-GENERAL
UTCT|UTS: Cities
UTSU|UTS: COCURRIC
UZBK|Uzbek
VIET|Vietnamese
VIAR|Visual Arts
FOVA|Visual Arts (SHSP)
WLOF|Wolof
WMST|Women's Studies
WRIT|Writing
YIDD|Yiddish
ZULU|Zulu
        """
        self.deptmap = {}
        for i in self.department_str.split("\n"):
            b = i.strip().split("|")
            if len(b) > 1:
                self.deptmap[b[0]] = b[1]

    def get_dept_name(self,name):
        return self.deptmap[name]
