import pyrebase

class Firebase:
    def __init__(self):
        config = {
        "apiKey": "AIzaSyBLv1DiRB6egmpaoIKfjODXZF5fYheQKIM",
        "authDomain": "realtimedatabasetest-f226a.firebaseapp.com",
        "databaseURL": "https://realtimedatabasetest-f226a-default-rtdb.asia-southeast1.firebasedatabase.app",
        "storageBucket": "realtimedatabasetest-f226a.appspot.com",
        "serviceAccount": r"D:\Desktop_1\Hack@10\Server\hackaten\server\credentials\firebase_access.json"
        }
        self.firebase = pyrebase.initialize_app(config)


    def register_user(self, email, password):
        try:
            auth = self.firebase.auth()
            user = auth.sign_in_with_email_and_password(email, password)
            return True
        except Exception as ex:
            return False
