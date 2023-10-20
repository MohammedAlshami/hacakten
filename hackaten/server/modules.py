import pyrebase
import jwt
import datetime
import uuid
import hashlib
from fuzzywuzzy import fuzz
from cryptography.fernet import Fernet
import json

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

    def verify_password(self, new_password, verification_code):
        auth = self.firebase.auth()

        try:
            auth.verify_password_reset_code(verification_code, new_password)
            return True
        except Exception as ex:
            return False

    def verify_register(self, verification_code):
        auth = self.firebase.auth()
        try:
            auth.verify_password_reset_code(verification_code, "")
            return False
        except Exception as ex:
            json_str = str(ex).split("] ")[1]

            error_dict = dict(json.loads(json_str))["error"]["message"]

            if error_dict == "WEAK_PASSWORD":
                return True

            return False

    def password_reset(self, email):
        print("password_reset")
        auth = self.firebase.auth()
        try:
            auth.send_password_reset_email(email)
            return email
        except Exception as ex:
            print(ex)
            return False

    def register_user(self, email, password):
        try:
            auth = self.firebase.auth()
            user = auth.sign_in_with_email_and_password(email, password)
            jwtToken = generate_jwt_token(user["localId"], SECRET_KEY)
            response_data = {
                "status": "success",
                "session_auth": jwtToken,  # Replace with the actual username
            }
            return (True, response_data)
        except Exception as ex:
            json_str = str(ex).split("] ")[1]

            # Convert the JSON string to a dictionary
            error_dict = dict(json.loads(json_str))["error"]["message"]

            response_data = {
                "status": "fail",
            }
            if error_dict.startswith("TOO_MANY_ATTEMPTS_TRY_LATER"):
                response_data["type"] = "requests"
                response_data[
                    "message"
                ] = "You have exceeded the maximum number of allowed requests. Please try again later."
            elif error_dict.startswith("INVALID_PASSWORD"):
                response_data["type"] = "password"
                response_data["message"] = "The password you entered is incorrect."
            elif error_dict.startswith("EMAIL_NOT_FOUND"):
                response_data["type"] = "email"
                response_data[
                    "message"
                ] = "The email address you provided does not exist."
            return (False, response_data)

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
        isLocal
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

        try:
            auth.get_user_by_email(email)
            print("User with this email already exists.")
            return None  # You can handle this case as needed
        except:
            pass

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
                    "local": isLocal 
                }
                db.child("hack10User").child(user_id).set(user_info)
                print("User registered successfully with ID:", user_id)
                print("Resume file uploaded to:", file_url)

                # sending email verification
                auth.send_email_verification(user_id)
                return generate_jwt_token(user_id, SECRET_KEY)
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
            print(group_id, user_id)

            print("Group registered successfully with ID:", group_id)
            return True
        else:
            return False

    def join_group(self, user_id, group_id):
        group_table_name = "hack10Groups"
        user_table_name = "hack10User"
        db = self.firebase.database()

        is_group_exist = db.child(group_table_name).child(group_id)
        group_val = is_group_exist.get().val()
        print(group_val)
        if group_val:
            group_record = group_val

            if len(group_record["members"]) < 3:
                if user_id not in group_record["members"]:
                    group_record["members"].append(user_id)
                new_group_value = {
                    "group_id": group_id,
                    "group_name": group_record["group_name"],
                    "members": group_record["members"],
                }
                db.child(group_table_name).child(group_id).set(new_group_value)

                user_ref = db.child(user_table_name).child(user_id)
                user_ref.update({"group_id": group_id})
                return 1
            else:
                return 0
        return -1

    def get_group(self, user_id):
        print(user_id)
        group_table_name = "hack10Groups"
        user_table_name = "hack10User"
        db = self.firebase.database()

        is_group_exist = db.child(user_table_name).child(user_id)

        group_id = None  # Initialize group_id to None

        try:
            group_id = is_group_exist.get().val()["group_id"]
        except Exception as e:
            pass

        if group_id:
            is_group_exist = db.child(group_table_name).child(group_id)
            group_record = is_group_exist.get().val()
            group_info = {
                "group_id": group_id,
                "group_name": group_record.get("group_name", "UKNOWN"),
                "members": [
                    get_member(db, i) for i in group_record.get("members", "UNKNOWN")
                ],
                "members_len": len(group_record["members"]),
            }
            print(group_info)
            return group_info

    def check_group(self, user_id):
        db = self.firebase.database()
        user_table_name = "hack10User"
        is_group_exist = db.child(user_table_name).child(user_id).get().val()
        if is_group_exist:
            is_group_involved = is_group_exist.get("group_id", None)
            if is_group_involved:
                return True
        return False

    def remove_group(self, user_id):
        group_table_name = "hack10Groups"
        user_table_name = "hack10User"
        db = self.firebase.database()

        print(user_id)
        user_ref = db.child(user_table_name).child(user_id)
        user_info = dict(user_ref.get().val())
        group_id = user_info["group_id"]
        user_info.pop("group_id")
        db.child(user_table_name).child(user_id).set(user_info)

        group_ref = db.child(group_table_name).child(group_id)
        group_info = dict(group_ref.get().val())
        if user_id in group_info["members"]:
            group_info["members"].remove(user_id)
            if len(group_info["members"]) == 0:
                db.child(group_table_name).child(group_id).remove()
            else:
                db.child(group_table_name).child(group_id).set(group_info)
            return True
        return False
        
        # print(user_data)
        # user_data.pop('group_id')
        # if user_data:
            
            # group_id = user_data.get("group_id")

            # Step 2: Delete the group_id from the user record
            # user_ref.update({"group_id": "1"})
            # user_ref = db.child(user_table_name).child(user_id)
            # user_data = user_ref.get().val()
            # print(user_data)
            # Step 3: Find the group by group_id and remove user_id from the members list
            # group_ref = db.child(group_table_name).child(group_id)
            # group_data = group_ref.get().val()
            # print(group_data)
            # if group_data:
            #     members = group_data.get("members", [])
            #     if user_id in members:
            #         members.remove(user_id)
            #         group_ref.update({"members": members})
            #         return True
            #     else:
            #         print("User not found in group members list.")
            #         return False
            # else:
            #     print("Group not found.")
            #     return False
        # else:
        #     print("User not found.")
        #     return False

    def create_project(
        self,
        user_id,
        case_study,
        project_name,
        project_image,
        project_description,
        project_pdf,
        project_github,
        project_video,
    ):
        group_table_name = "hack10Groups"
        project_table_name = "hack10Projects"
        user_table_name = "hack10User"
        db = self.firebase.database()

        project_table_ref = db.child(project_table_name)
        project_table_exists = project_table_ref.get().val() is not None

        if not project_table_exists:
            db.child(project_table_name).set({})

        group_id = (
            db.child(user_table_name).child(user_id).get().val().get("group_id", None)
        )

        project_ref = db.child(user_table_name).child(user_id)

        project_id = None  # Initialize group_id to None

        try:
            project_id = project_ref.get().val()["project_id"]
            print(project_id)
        except Exception as e:
            pass

        if not project_id:
            project_id = generate_uuid_from_group_name(group_id)

        group_info = {
            "project_id": project_id,
            "case_study": case_study,
            "project_name": project_name,
            "project_image": project_image,
            "project_description": project_description,
            "project_pdf": project_pdf,
            "project_github": project_github,
            "project_video": project_video,
            "group_id": group_id,
        }

        db.child(project_table_name).child(project_id).set(group_info)

        user_ref = db.child(user_table_name).child(user_id)
        user_ref.update({"project_id": project_id})

        group_ref = db.child(group_table_name).child(group_id)
        group_ref.update({"project_id": project_id})

        print("Project registered successfully with ID:", project_id)

    def get_project(self, user_id):
        print(user_id)
        group_table_name = "hack10Groups"
        project_table_name = "hack10Projects"
        user_table_name = "hack10User"
        db = self.firebase.database()

        project_ref = db.child(user_table_name).child(user_id)

        project_id = None  # Initialize group_id to None

        try:
            project_id = project_ref.get().val()["project_id"]
        except Exception as e:
            pass

        print(project_id)
        if project_id:
            project_ref = db.child(project_table_name).child(project_id)
            project_record = project_ref.get().val()
            project_info = {
                "project_id": project_id,
                "case_study": project_record["case_study"],
                "project_name": project_record["project_name"],
                "project_image": project_record["project_image"],
                "project_description": project_record["project_description"],
                "project_pdf": project_record["project_pdf"],
                "project_github": project_record["project_github"],
                "project_video": project_record["project_video"],
            }
            return project_info


def get_member(db, user_id):
    user_table_name = "hack10User"
    is_group_exist = db.child(user_table_name).child(user_id)
    group_record = is_group_exist.get().val()
    return f'{group_record.get("first_name", "UKNOWN")} {group_record.get("last_name", "UKNOWN")}'


def group_name_check(db, table_name, group_name, threshold=95):
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


def generate_jwt_token(user_id, secret_key):
    expiration_days = 7
    # Create a payload (a dictionary containing data)
    payload = {
        "user_id": user_id,
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


def encrypt_text(text, key):
    fernet = Fernet(key)
    encrypted_text = fernet.encrypt(text.encode())
    return encrypted_text


def decrypt_text(encrypted_text, key):
    fernet = Fernet(key)
    decrypted_text = fernet.decrypt(encrypted_text).decode()
    return decrypted_text
