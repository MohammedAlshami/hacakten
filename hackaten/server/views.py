from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
import json
import os
from tqdm import tqdm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import urllib.parse
from django.urls import reverse


from django.template import RequestContext

# importing firebase for authentication
from .modules import Firebase, generate_jwt_token, decode_jwt_token, SECRET_KEY

firebase = Firebase()


from django.http import JsonResponse
import json


def landing_page(request):
    session_auth = request.COOKIES.get("session_auth")
    is_session_valid = decode_jwt_token(session_auth, SECRET_KEY)

    if is_session_valid:
        is_session_valid = True
    else:
        is_session_valid = False

    if session_auth:
        return render(request, "landing/index.html", {"user_exist": is_session_valid})


def password_reset(request):
    email_cookie = request.COOKIES.get("reset_auth")

    if email_cookie:
        response = HttpResponse("blah")
        # response.set_cookie('reset_auth', domain="", max_age_seconds=0.1)

        email_valid = decode_jwt_token(email_cookie, SECRET_KEY)
        if email_valid:
            email = email_valid["user_id"]
            return render(request, "signin/email_sent.html", {"email": email})

    if request.method == "POST":
        data = json.loads(request.body)
        email = str(data.get("email"))

        is_email_exist = firebase.password_reset(email)
        if is_email_exist:
            print(1)
            response_data = {
                "status": "success",
                "reset_auth": generate_jwt_token(email, SECRET_KEY),
            }
            return JsonResponse(response_data)
        else:
            response_data = {
                "status": "fail",
                "reason": "The email address you provided does not exist.",
            }
            return JsonResponse(response_data)

    return render(request, "signin/email_reset.html")


def reset_msg(request, **kwargs):
    # email = request.GET.get('email', None)
    # if email:
    return render(request, "signin/email_sent.html")


def register_verify(request):
    oob_code = request.GET.get("oobCode", None)
    email = request.GET.get("email", None)

    if oob_code and email:
        is_reset_success = firebase.verify_register(oob_code)
        if is_reset_success:
            return HttpResponseRedirect("/hub")
        else:
            return render(request, "404.html")

        # print(oob_code)
    # return render(request, "signin/password_reset.html")


def password_confirm(request):
    if request.method == "POST":
        data = json.loads(request.body)
        oob_code = str(data.get("oobCode", None))
        if oob_code:
            email = str(data.get("email", None))
            password = str(data.get("password"))
            is_reset_success = firebase.verify_password(password, oob_code)
            if is_reset_success:
                isAuthValid = firebase.register_user(email, password)
                print(isAuthValid[1])
                # Return a JSON response with status and user name
                return JsonResponse(isAuthValid[1])
            else:
                response_data = {"status": "fail", "reason": "Password is bad"}
                return JsonResponse(response_data)
        else:
            response_data = {"status": "fail", "reason": "no oopcode"}
            return JsonResponse(response_data)

        # print(oob_code)
    return render(request, "signin/password_reset.html")


def sign_in(request):
    session_auth = request.COOKIES.get("session_auth")
    if session_auth is None:
        if request.method == "POST":
            data = json.loads(request.body)
            email = str(data.get("email"))
            password = str(data.get("password"))
            print(email, password)

            # Assuming firebase.register_user returns True for successful authentication
            isAuthValid = firebase.register_user(email, password)

            if isAuthValid[0]:
                # Return a JSON response with status and user name
                return JsonResponse(isAuthValid[1])
            else:
                print(isAuthValid[1])
                return JsonResponse(isAuthValid[1])

        return render(request, "signin/index.html")
    else:
        return HttpResponseRedirect("/hub")


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
                response_data = {
                    "status": "fail",
                    "reason": "User Email Already Exists",
                }
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
        return HttpResponseRedirect("/hub")


def participant_hub(request):
    print("participant_hub view called")
    return render(request, "participant_hub\index.html")


def case_studies(request):
    return render(request, "participant_hub\case_studies\index.html")


def custom_404(request, *args, **argv):
    response = render_to_response(
        "404.html", {}, context_instance=RequestContext(request)
    )
    response.status_code = 404
    return response


def group_join(request):
    return render(request, "participant_hub\grouping\join.html")


def group_create(request):
    return render(request, "participant_hub\grouping\create.html")


def register_options(request):
    session_auth = request.COOKIES.get("session_auth")
    if session_auth:
        return HttpResponseRedirect("/hub")

    return render(request, "signup\options.html")


def grouping(request):
    session_auth = request.COOKIES.get("session_auth")
    if session_auth:
        user_payload = decode_jwt_token(session_auth, SECRET_KEY)
        userid = user_payload["user_id"]
        check_group = firebase.check_group(userid)
        if check_group:
            return HttpResponseRedirect("/groups/hub")

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
                                userid,
                                SECRET_KEY,
                            )
                        ),
                    }
                    return JsonResponse(response_data)
                else:
                    response_data = {
                        "status": "fail",
                        "msg": "Group Name Already Exists, Please Choose A different Name.",
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
                                userid,
                                SECRET_KEY,
                            )
                        ),
                    }
                    return JsonResponse(response_data)
                elif is_create == 0:
                    response_data = {
                        "status": "fail",
                        "msg": "Sorry but the group is already full",
                    }

                    return JsonResponse(response_data)
                elif is_create == -1:
                    response_data = {"status": "fail", "msg": "Group Doesn't Exist"}
                    return JsonResponse(response_data)

        else:
            return render(request, "participant_hub\grouping\index.html")

    return HttpResponseRedirect("/login")


def rules(request):
    return render(request, "participant_hub\\rules\index.html")


def group_hub(request):
    session_auth = request.COOKIES.get("session_auth")

    if session_auth:
        user_payload = decode_jwt_token(session_auth, SECRET_KEY)
        userid = user_payload["user_id"]

        if request.method == "POST":
            leave_request = str(request.POST.get("type", ""))
            is_leave_success = firebase.remove_group(userid)
            if is_leave_success:
                response_data = {"status": "success"}
                return JsonResponse(response_data)
            else:
                response_data = {"status": "fail"}
                return JsonResponse(response_data)

        check_group = firebase.check_group(userid)
        if check_group:
            payload = firebase.get_group(userid)
            return render(request, "participant_hub\\grouping\group_hub.html", payload)

    return HttpResponseRedirect("/login")
    # return render(request, "participant_hub\\grouping\index.html")


def mentors(request):
    return render(request, "participant_hub\\mentors\index.html")


def resources(request):
    return render(request, "participant_hub\\resources\index.html")


def submission(request):
    session_auth = request.COOKIES.get("session_auth")
    if session_auth:
        user_payload = decode_jwt_token(session_auth, SECRET_KEY)
        user_id = user_payload["user_id"]
        if request.method == "POST":
            case_study = str(request.POST.get("case_study", ""))
            project_name = str(request.POST.get("project_name", ""))
            project_image = str(request.POST.get("project_image", ""))
            project_description = str(request.POST.get("project_description", ""))
            project_github = str(request.POST.get("project_github", ""))
            project_pdf = str(request.POST.get("project_pdf", ""))
            project_video = str(request.POST.get("project_video", ""))

            firebase.create_project(
                user_id,
                case_study,
                project_name,
                project_image,
                project_description,
                project_pdf,
                project_github,
                project_video,
            )

            response_data = {
                "status": "success",
                "session_auth": str(generate_jwt_token(user_id, SECRET_KEY)),
            }
            return JsonResponse(response_data)

    return render(request, "participant_hub\\submission\index.html")


def project(request):
    session_auth = request.COOKIES.get("session_auth")
    user_payload = decode_jwt_token(session_auth, SECRET_KEY)
    userid = user_payload["user_id"]
    project = firebase.get_project(userid)
    return render(request, "participant_hub\\submission\project.html", project)


def project_edit(request):
    session_auth = request.COOKIES.get("session_auth")
    user_payload = decode_jwt_token(session_auth, SECRET_KEY)
    userid = user_payload["user_id"]
    project = firebase.get_project(userid)

    print(project)
    return render(request, "participant_hub\\submission\project_edit.html", project)
