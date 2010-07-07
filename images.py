
from datetime import datetime, timedelta
from google.appengine.ext import webapp
from google.appengine.ext import db

HTTP_DATE_FMT = '%a, %d %b %Y %H:%M:%S GMT'

class Image(db.Model):
    modified = db.DateTimeProperty(auto_now=True)
    data = db.BlobProperty()
    
    @classmethod
    def get_from_path(cls, path):
      from google.appengine.api import memcache
      cached_image = memcache.get(path)
      if cached_image is not None:
        image = cached_image
      else:
        image = Image.get_by_key_name(path)
        if image:
          memcache.set(path, image)

      return image
    
    @classmethod
    def update_cache(cls, path):
      from google.appengine.api import memcache
      memcache.delete(path)
      Image.get_from_path(path)
    
class ImageHandler(webapp.RequestHandler):
    def get(self, path):
      image = Image.get_from_path(path)
          
      if image and image.data:
        if not self.modified_since(image.modified):
          self.response.set_status(304)
        else:
          self.send_caching_headers(image.modified, cache=False)
          self.response.headers['Content-Type'] = "image/jpeg"
          self.response.out.write(image.data)
      else:
        self.error(404)
        
    def modified_since(self, last_modified):
      modified = True
      if 'If-Modified-Since' in self.request.headers:
        modified_since = datetime.strptime(self.request.headers['If-Modified-Since'], HTTP_DATE_FMT)
        if modified_since >= last_modified.replace(microsecond=0):
          modified = False
            
      return modified
    
    def send_caching_headers(self, last_modified, cache=True, days=30):
      last_modified_header = last_modified.strftime(HTTP_DATE_FMT)
      self.response.headers['Last-Modified'] = last_modified_header
        
#      if cache:
#        expiration = datetime.utcnow() + timedelta(days)
#        expires_header = expiration.strftime(HTTP_DATE_FMT)
#        self.response.headers['Expires'] = expires_header
#        self.response.headers['Cache-Control'] = 'private, max-age=%d' % int(3600*24*days)
    
class ImageUpload(webapp.RequestHandler):
  def post(self):
    data = self.request.get("img")
    path = self.request.get("path")
    
    image = Image(key_name=path)
    image.data = db.Blob(str(data))
    image.put()
    image.update_cache(image.key().name())

    
    
    