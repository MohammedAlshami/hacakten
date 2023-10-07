import pyrebase
import jwt
import datetime
import uuid
import hashlib




SECRET_KEY = "2B1fGuGYqV445v9x4Dn9HX0vtBmDFRgP"


class Firebase:
    def __init__(self):
        config = {
            "apiKey": "AIzaSyBLv1DiRB6egmpaoIKfjODXZF5fYheQKIM",
            "authDomain": "realtimedatabasetest-f226a.firebaseapp.com",
            "databaseURL": "https://realtimedatabasetest-f226a-default-rtdb.asia-southeast1.firebasedatabase.app",
            "storageBucket": "realtimedatabasetest-f226a.appspot.com",
            "serviceAccount": r"D:\Desktop_1\Hack@10\Server\hackaten\server\credentials\firebase_access.json",
        }
        self.firebase = pyrebase.initialize_app(config)

    def register_user(self, email, password):
        try:
            auth = self.firebase.auth()
            user = auth.sign_in_with_email_and_password(email, password)
            jwtToken = generate_jwt_token(user["localId"], email, SECRET_KEY)
            return jwtToken
        except Exception as ex:
            print(ex)
            return False

    def upload_user_info(
        self,
        first_name,
        last_name,
        university,
        major,
        age,
        discord_tag,
        email,
        password,
        confirm_password,
        join_reason,
    ):
        auth = self.firebase.auth()

        db = self.firebase.database()
        storage = self.firebase.storage()

        # Check if the "hack10User" table exists
        user_table_ref = db.child("hack10Users")
        user_table_exists = user_table_ref.get().val() is not None

        if not user_table_exists:
            # Create the "hack10User" table if it doesn't exist
            db.child("hack10Users").set({})

        # Authentication: Register a user (replace with your email and password)
        email = f"{uuid.uuid4()}@gmail.com"
        password = "password"

        try:
            user = auth.create_user_with_email_and_password(email, password)
            user_id = user["localId"]
        except Exception as e:
            print("User registration failed:", str(e))
            user_id = None

        if user_id:
            # Upload a PDF file to storage and get the file path
            file_path = (
                r"D:\download_1\screencapture-hackaten-2023-10-05-10_08_16 (1).pdf"
            )
            folder_path = rf"hack10/samples/{uuid.uuid4()}.pdf"
            try:
                storage.child(folder_path).put(file_path)
                file_url = storage.child(folder_path).get_url(None)
            except Exception as e:
                print("File upload failed:", str(e))
                file_url = None

            if file_url:
                # Create a record with user information
                user_info = {
                    "user_id": user_id,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "university": university,
                    "major": major,
                    "age": age,
                    "discord_tag": discord_tag,
                    "email": email,
                    "join_reason": join_reason,
                    "resume_path": file_url,
                }
                db.child("hack10User").child(user_id).set(user_info)
                print("User registered successfully with ID:", user_id)
                print("Resume file uploaded to:", file_url)
                return generate_jwt_token(user_id, email, SECRET_KEY)
        return None

def generate_uuid_from_file_name(file_name):
    # Create a new UUID using MD5 hash of the file name
    uuid_bytes = hashlib.md5(file_name.encode()).digest()
    return uuid.UUID(bytes=uuid_bytes, version=4)  # version 4 UUID

                     
def generate_jwt_token(user_id, email, secret_key, expiration_days=7):
    # Create a payload (a dictionary containing data)
    payload = {
        "user_id": user_id,
        "username": email,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(days=expiration_days),  # Token expiration time
    }

    # Encode the payload into a JWT token
    token = jwt.encode(payload, secret_key, algorithm="HS256")

    return token


def decode_jwt_token(token, secret_key):
    try:
        # Decode the token to get the payload
        decoded_payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return None
