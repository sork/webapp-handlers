
from google.appengine.ext import webapp

class RESTfulHandler(webapp.RequestHandler):
  def post(self, *args):
    method = self.request.headers.get('X-HTTP-Method-Override')
    
    if method == "PUT":
      self.put(*args)
    elif method == "DELETE":
      self.delete(*args)
    else:
      self.error(405)