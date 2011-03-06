from model import Class
from model import db

class ClassTest:
    def remove_all(self):
        query = Class().all()
        for result in query:
            db.delete(result)
    def test_add(self,dept,name,number):
        print "adding "+name
        if not (self.test_exists(dept, name, number)):
            myclass = Class(description=name, name=name, department=dept, number=number)
            db.put(myclass)
    def test_exists(self,dept,name,number):
        return Class.gql("WHERE department = :1 AND number = :2", dept,number).get()        
    def test_remove(self, dept,number):
        print "removing "+dept+" "+number
        classes = Class.gql("WHERE department = :1 AND number = :2", dept,number)
        myclass = classes.get()
        try:
            db.delete(myclass)
        except (Exception):
            print "can't find "+dept+" "+number+"\n"
    def test_modify(self,dept,number,new_name):
        result = Class.gql("WHERE department = :1 AND number = :2", dept,number).get();
        print "modifying "+result.name+" to "+new_name
        result.name = new_name
        db.put(result)
    def test_print_db(self):
        query = Class.all()
        string = "database:\n"
        count = 0
        for result in query:
            string += str(count) + " "+ result.name + ": ("+result.department+","+result.number+")\n"
            count = count+1
        print string
    def __init__(self):
        print "class test"
        self.remove_all()
        self.test_add("COMS","Intro to CS", "C1004")
        self.test_print_db()
        self.test_add("COMS", "Advanced CS", "W4444")
        self.test_print_db()
        self.test_add("COMS", "Advanced CS", "W4444")
        self.test_print_db()
        self.test_modify("COMS","C1004", "Intro to CS in Java")
        self.test_print_db()
        self.test_remove("COMS", "C1004")
        self.test_print_db()
        self.test_remove("COMS","W4444")
        self.test_print_db()
        self.test_remove("COMS", "C1004")
        self.test_print_db()
        print "done with classes test"
        
