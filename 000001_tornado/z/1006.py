class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id: return None
        return self.backend.get_user_by_id(user_id)

    def get_user_locale(self):
        if "locale" not in self.current_user.prefs:
            # Use the Accept-Language header
            return None
        return self.current_user.prefs["locale"]


#uimodules.py:
class Entry(tornado.web.UIModule):
            def render(self,entry,show_comments=False):
                return self.render_string(
                    "module-entry.html",entry = entry,show_comments=show_comments)
        		        
from . import uimodules
