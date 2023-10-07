import pyrebase
import jwt
import datetime
import uuid
import hashlib
from fuzzywuzzy import fuzz

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

    def create_group(self, user_id, group_name):
        group_table_name = "hack10Groups"
        user_table_name = "hack10User"
        db = self.firebase.database()
        is_name_exist = group_name_check(db, group_table_name, group_name)

        if is_name_exist:
            user_table_ref = db.child(group_table_name)
            user_table_exists = user_table_ref.get().val() is not None

            if not user_table_exists:
                db.child(group_table_name).set({})

            group_id = generate_uuid_from_group_name(group_name)
            group_info = {
                "group_id": group_id,
                "group_name": group_name,
                "members": [user_id],
            }

            db.child(group_table_name).child(group_id).set(group_info)

            user_ref = db.child(user_table_name).child(user_id)
            user_ref.update({"group_id": group_id})

            print("Group registered successfully with ID:", group_id)
            return True
        else:
            return False

    def join_group(self, user_id, group_id):
        group_table_name = "hack10Groups"
        user_table_name = "hack10User"
        db = self.firebase.database()

        is_group_exist = db.child(group_table_name).child(group_id)
        print()
        if is_group_exist.get().val():
            group_record = is_group_exist.get().val()

            if len(group_record["members"]) < 3:
                if user_id not in group_record["members"]:
                    group_record["members"].append(user_id)
                new_group_value = {
                    "group_id": group_id,
                    "group_name":  group_record["group_name"],
                    "members": group_record["members"],
                }
                db.child(group_table_name).child(group_id).set(new_group_value)
                return 1
            else:
                return 0
        return -1
        
        
        # db.child(group_table_name).order_by_child("group_id").equal_to(f"'{group_id}'").get()

            # print(is_group_exist)
        # if is_group_exist.get().exists():
        #     print("Group Exists")
        # else:
        #     print("group doesn't exist")
        # is_name_exist = group_name_check(db, group_table_name, group_name)

        # if is_name_exist:
        #     user_table_ref = db.child(group_table_name)
        #     user_table_exists = user_table_ref.get().val() is not None

        #     if not user_table_exists:
        #         db.child(group_table_name).set({})

        #     group_id = generate_uuid_from_group_name(group_name)
        #     group_info = {
        #         "group_id": group_id,
        #         "group_name": group_name,
        #         "members": [user_id],
        #     }

        #     db.child(group_table_name).child(group_id).set(group_info)

        #     user_ref = db.child(user_table_name).child(user_id)
        #     user_ref.update({"group_id": group_id})

        #     print("Group registered successfully with ID:", group_id)
        #     return True
        # else:
        #     return False


def group_name_check(db, table_name, group_name, threshold=80):
    record_ids = []

    # Reference to your Firebase database table
    table_ref = db.child(table_name)

    # Retrieve data from the table
    records = table_ref.get().each()

    if records:
        for record in records:
            # Extract the record ID (the key)
            record_data = record.val()
            if "group_name" in record_data:
                record_id = record_data["group_name"]
                record_ids.append(record_id)

        # checking similarity
        for existing_name in record_ids:
            similarity = fuzz.ratio(group_name.lower(), existing_name.lower())

            if similarity >= threshold:
                print(similarity)
                return False

        return True


def generate_uuid_from_group_name(groupName):
    uuid_bytes = hashlib.md5(groupName.encode()).digest()
    return str(uuid.UUID(bytes=uuid_bytes, version=4))


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
