from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
import os
from tqdm import tqdm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# importing firebase for authentication
from .modules import Firebase, generate_jwt_token, decode_jwt_token, SECRET_KEY

firebase = Firebase()


from django.http import JsonResponse
import json


def say_hello(request):
    session_auth = request.COOKIES.get("session_auth")
    if session_auth is None:
        if request.method == "POST":
            data = json.loads(request.body)
            email = str(data.get("email"))
            password = str(data.get("password"))
            print(email, password)

            # Assuming firebase.register_user returns True for successful authentication
            isAuthValid = firebase.register_user(email, password)

            if isAuthValid:
                # Return a JSON response with status and user name
                response_data = {
                    "status": "success",
                    "session_auth": isAuthValid[1],  # Replace with the actual username
                }
                return JsonResponse(response_data)
            else:
                response_data = {"status": "fail"}
                return JsonResponse(response_data)

        return render(request, "signin/index.html")
    else:
        return render(request, "participant_hub\index.html")


def signup(request):
    session_auth = request.COOKIES.get("session_auth")
    if session_auth is None:
        if request.method == "POST":
            print(len(request.POST))

            first_name = request.POST.get("firstName", "")
            last_name = request.POST.get("lastName", "")
            university = request.POST.get("university", "")
            major = request.POST.get("major", "")
            age = request.POST.get("age", "")
            discord_tag = request.POST.get("discordTag", "")
            email = request.POST.get("email", "")
            password = request.POST.get("password", "")
            confirm_password = request.POST.get("confirmPassword", "")
            join_reason = request.POST.get("joinReason", "")

            isAuthValid = firebase.upload_user_info(
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
            )

            if isAuthValid:
                # Return a JSON response with status and user name
                response_data = {
                    "status": "success",
                    "session_auth": isAuthValid,  # Replace with the actual username
                }
                return JsonResponse(response_data)
            else:
                response_data = {"status": "fail"}
                return JsonResponse(response_data)
            # resume_file = request.FILES.get("resume", None)

            # # Handle the file, e.g., save it to the server
            # if resume_file:
            #     file_path = os.path.join("D:\Desktop_1", resume_file.name)
            #     with open(file_path, 'wb+') as destination:
            #         file_size = resume_file.size
            #         progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)
            #         for chunk in resume_file.chunks():
            #             destination.write(chunk)
            #             progress_bar.update(len(chunk))
            #         progress_bar.close()

            return HttpResponse("File uploaded")

        else:
            return render(request, "signup/index.html")
    else:
        return render(request, "participant_hub\index.html")


def participant_hub(request):
    print("participant_hub view called")
    return render(request, "participant_hub\index.html")


def case_studies(request):
    return render(request, "participant_hub\case_studies\index.html")


def grouping(request):
    session_auth = request.COOKIES.get("session_auth")
    if session_auth:
        if request.method == "POST":
            request_type = str(request.POST.get("type", ""))
            request_data = str(request.POST.get("data", ""))

            if request_type == "create":
                user_payload = decode_jwt_token(session_auth, SECRET_KEY)
                userid = user_payload["user_id"]    
                is_create = firebase.create_group(userid, request_data)

                if is_create:
                    # print(request_type, request_data)

                    response_data = {
                        "status": "success",
                        "session_auth": str(
                            generate_jwt_token(
                                "ju9MG6Li6cSHlx5UEx3LFXXivIZ2", "user@example9.com", SECRET_KEY
                            )
                        ),
                        
                    }
                    return JsonResponse(response_data)
                else:
                    response_data = {
                        "status": "fail",
                        "msg": "Group Name Already Exists, Please Choose A different Name."
                    }
                    
                    return JsonResponse(response_data)
                
            if request_type == "join":
                user_payload = decode_jwt_token(session_auth, SECRET_KEY)
                userid = user_payload["user_id"]    
                is_create = firebase.join_group(userid, request_data)

                if is_create == 1:
                    response_data = {
                            "status": "success",
                            "session_auth": str(
                                generate_jwt_token(
                                    "ju9MG6Li6cSHlx5UEx3LFXXivIZ2", "user@example9.com", SECRET_KEY
                                )
                            ),
                            
                        }
                    return JsonResponse(response_data)
                elif is_create == 0:
                    response_data = {
                        "status": "fail",
                        "msg": "Sorry but the group is already full"
                    }
                    
                    return JsonResponse(response_data)
                elif is_create == -1:
                    response_data = {
                        "status": "fail",
                        "msg": "Group Doesn't Exist"
                    }
                    return JsonResponse(response_data)



    return render(request, "participant_hub\grouping\index.html")


def rules(request):
    return render(request, "participant_hub\\rules\index.html")


def mentors(request):
    return render(request, "participant_hub\\mentors\index.html")


def resources(request):
    return render(request, "participant_hub\\resources\index.html")


def submission(request):
    return render(request, "participant_hub\\submission\index.html")
