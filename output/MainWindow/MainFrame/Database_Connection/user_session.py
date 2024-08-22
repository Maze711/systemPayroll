import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class UserSession:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UserSession, cls).__new__(cls, *args, **kwargs)
            cls._instance.session_data = {}
        return cls._instance

    def __getitem__(self, key):
        return self.session_data.get(key)

    def __setitem__(self, key, value):
        self.session_data[key] = value

    def __contains__(self, key):
        return key in self.session_data

    def clearSession(self):
        self.session_data.clear()

    def getALLSessionData(self):
        return self.session_data