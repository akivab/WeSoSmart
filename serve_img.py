import fix_path
from google.appengine.ext import db
from google.appengine.ext.db import Key
from google.appengine.ext import webapp
class GetImage(webapp.RequestHandler):
    def get(self):
        key = self.request.get('s')
        picture = db.get(Key(key))
        if (picture and picture.data):
            self.response.headers['Content-Type'] = 'image/jpeg'
            self.response.out.write(picture.data)
        else:
            self.redirect('/img/test.jpg')