'''
Created on Jan 3, 2011

@author: akiva
'''
import os
from google.appengine.ext.webapp import template

def render_template(template_vals, file):
    path = os.path.join(os.path.dirname(__file__), file)
    return template.render(path, template_vals)
