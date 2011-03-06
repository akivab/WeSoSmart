from images import GetImage
from model import User
from model import db

# class User(Subject):
#     name = db.StringProperty()
#     cubmail = db.EmailProperty()
#     nick = db.StringProperty()
#     email = db.EmailProperty()
#     picture = db.BlobProperty()
#     public = db.IntegerProperty()
#     registered = db.IntegerProperty()
#     password = db.StringProperty()

class UserTest:
    def remove_all(self):
        query = User().all()
        for result in query:
            db.delete(result)
            
    def test_add(self,cubmail):
        print "adding "+cubmail
        if not (self.test_exists(cubmail)):
            user = User(cubmail=cubmail, registered=1)
            db.put(user)
    def test_exists(self,cubmail):
        return User.gql("WHERE cubmail = :1", cubmail).get()        
    def test_remove(self, cubmail):
        print "removing "+cubmail
        users = User.gql("WHERE cubmail = :1", cubmail)
        myclass = users.get()
        try:
            db.delete(myclass)
        except (Exception):
            print "can't find "+cubmail+"\n"
    def test_oked(self, key):
        print "testing ok with key "+str(key)
        result = db.get(key);
        result.registered = 2;
    def test_modify(self, key):
        result = db.get(key)
        print "modifying "+result.cubmail+" with picture "
        result.picture = db.Blob(open("model/test.png","rb").read())
        db.put(result)
    def test_get_key(self, cubmail):
        result = User.gql("WHERE cubmail = :1", cubmail).get()
        return result.key()
    def test_print_db(self):
        query = User.all()
        string = "database:\n"
        count = 0
        for result in query:
            if result.picture:
                string += str(count) + " "+ result.cubmail + ": (Pic found,"+str(result.registered)+")\n"
            else:
                string += str(count) + " "+ result.cubmail + ": (Pic not found,"+str(result.registered)+")\n"
            count = count+1
        print string
    def __init__(self):
        print "class test"
        self.remove_all()
        self.test_add("ab2928@columbia.edu")
        self.test_print_db()
        self.test_add("ab2928@columbia.edu")
        self.test_print_db()
        key = self.test_get_key("ab2928@columbia.edu")
        self.test_print_db()
        self.test_oked(key)
        self.test_print_db()
        self.test_modify(key)
        self.test_print_db()
        self.test_remove("ab2928@columbia.edu")
        self.test_print_db()
        self.test_remove("ab2928@columbia.edu")
        self.test_print_db()
        print "done with classes test"
        