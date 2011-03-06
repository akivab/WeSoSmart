'''
Created on Jan 1, 2011

@author: akiva
'''
from google.appengine.api import mail

class SendEmail():
    def __init__(self):
        self.email = "akiva@wesosmart.com"
    def sendVerificationEmail(self, user, hash):
        email = user.cubmail
        if not mail.is_email_valid(email):
            # Return an error message...
            raise Exception("Can't send email to " + email)
        body_string =  """
Dear %s,

Thank you for signing up with WeSoSmart! Please verify your account at %s/verify/%s/%s.

If that's too much, just log in at WeSoSmart with this code: %s.

If you have any questions, don't hesitate to ask!

Best,
WeSoSmart
        """ % (user.name, "http://www.wesosmart.com",str(user.key()), hash, hash)
        
        mail.send_mail(sender="WeSoSmart Support <%s>"%self.email,
                      to=email,
                      subject="Please verify your WeSoSmart account",
                      body=body_string)
        mail.send_mail(sender="WeSoSmart Support <%s>"%self.email,
                      to="%s"%self.email,
                      subject="Verifying account for %s"%user.name,
                      body="key: %s, email %s"%(hash, user.cubmail))
    def sendBookMsg(self, user, ub, message):
        msg ="""
Dear %s,

Someone has shown interest in a book you listed (%s %s %s).

Send them an email to let them know you are interested by:
1) visiting their page (at http://www.wesosmart.com/user/%s)
2) emailing them (at %s), or
3) checking out more info about the book (at http://www.wesosmart.com/book/%s).

Best,
WeSoSmart
        """  % (user.name, ub.user_id.name, "wants" if ub.status == 0 else "has", ub.book_id.title, str(ub.user_id.key()), ub.user_id.cubmail, str(ub.book_id.key()))
        mail.send_mail(sender="WeSoSmart Support <%s>"%self.email,
                      to=user.cubmail,
                      subject="WeSoSmart found a match for %s!"%ub.book_id.title,
                      body=msg)

    def sendEmailAboutComment(self, toemail, user, comment, subject_type, subject_key):
        msg = """
Dear %s,

A comment was written by %s that may be of interest to you:

%s

To view this comment in context, visit http://www.wesosmart.com/%s/%s.

Bye!
WeSoSmart
""" % (toemail.name, user.name, comment, subject_type, str(subject_key))
        mail.send_mail(sender="WeSoSmart Support <%s>"%self.email,
                      to=toemail.cubmail,
                      subject="Comment on WeSoSmart",
                      body=msg)
    
    def sendDirect(self,user_to_name, user_to_email, user_from_key, user_from_name, user_from_email, email):        
        msg = """
Dear %s,

You have received a message via WeSoSmart from %s:

%s

To respond, email %s or visit http://www.wesosmart.com/user/%s.

Best,
WeSoSmart
"""%(user_to_name, user_from_name, email, user_from_email, user_from_key)
        mail.send_mail(sender="WeSoSmart Support <%s>"%self.email,
                      to=user_to_email,
                      subject="WeSoSmart message from %s (%s)"%(user_from_name,user_from_email),
                      body=msg)