from model import Subject
from model import db
 
class SubjectTest:
    def remove_all(self):
        query = Subject().all()
        for result in query:
            db.delete(result)
    def test_add(self,name):
        print "adding "+name
        subject = Subject()
        subject.description = name
        db.put(subject)
    def test_remove(self, name):
        print "removing "+name
        subjects = Subject.gql("WHERE description = :1", name)
        subject = subjects.get()
        try:
            db.delete(subject)
        except (Exception):
            print "can't find "+name+"\n"
    def test_modify(self,old_name,new_name):
        print "modifying "+old_name+" to "+new_name
        subjects = Subject.gql("WHERE description = :1", old_name)
        subject = subjects.get()
        subject.description = new_name
        db.put(subject)
    def test_print_db(self):
        query = Subject.all()
        string = "database:\n"
        count = 0
        for result in query:
            string += str(count)+" "+result.description + "\n"
            count = count+1
        print string
    def __init__(self):
        print "subject test"
        self.remove_all()
        self.test_add("monkey")
        self.test_print_db()
        self.test_add("dog")
        self.test_print_db()
        self.test_modify("monkey","man")
        self.test_print_db()
        self.test_remove("dog")
        self.test_print_db()
        self.test_remove("man")
        self.test_print_db()
        self.test_remove("man")
        self.test_print_db()
        print "done with subject test"
