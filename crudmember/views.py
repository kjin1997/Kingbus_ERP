from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login
from django.http import JsonResponse
from .models import User, UserFile
from .forms import UserForm

from datetime import datetime
from random import choice
from string import ascii_lowercase

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from .tokens import account_activation_token


def home(request):
    id = request.session.get('user')
    if id:
        user_info = User.objects.get(pk=id)
        context = {
            "name" : user_info.name,
        }
        return render(request, 'crudmember/home.html', context)
    return redirect('crudmember:login')

def signup_terms(request):
    return render(request, 'crudmember/signup_terms.html')

def welcome(request):
    return render(request, 'crudmember/welcome.html')

def id_overlap_check(request):
    user_id = request.GET.get('user_id')
    try:
        # 중복 검사 실패
        user = User.objects.get(user_id=user_id)
    except:
        # 중복 검사 성공
        user = None
    if user is None:
        overlap = "pass"
    else:
        overlap = "fail"
    context = {'overlap': overlap}
    return JsonResponse(context)   


def signup(request):
    if request.method == "GET":
        form = UserForm

        return render(request, 'crudmember/signup.html', {
            'form': form,
            'test': "asdfasdasdfasf",
        })

    elif request.method == 'POST':
        user_form = UserForm(request.POST)
        
        user_id = request.POST.get('user_id', None)
        password1 = request.POST.get('password1', None)
        password2 = request.POST.get('password2', None)
        files = request.FILES.getlist('file')
        mail = ''.join(request.POST.getlist('manager_mail', None))

        res_data = {}

        if User.objects.filter(user_id=user_id).exists(): #아이디 중복체크
            res_data['error'] = '사용중인 아이디입니다.'
            print("error")
        elif password1 != password2:
            res_data['error'] = "비밀번호가 다릅니다."
            print("error")
        elif user_form.is_valid():
            print("PASS")
            user = user_form.save(commit=False)
            user.password = make_password(password1)
            user.manager_mail = mail
            user.save()

            for upload_file in files:
                user_file = UserFile(
                    user_id=get_object_or_404(User, user_id=user_id),
                    file=upload_file
                )
                user_file.save()
            #auth.login(request, user)
            return render(request, 'crudmember/welcome.html', res_data)
        else:
            print("NOOO", user_form)
        return render(request, 'crudmember/signup.html', res_data)
        

def login(request):
    # 로그인 기능
    res_data = {}
    if request.method == 'POST':
        login_username = request.POST.get('userid', None)
        login_password = request.POST.get('password', None)
        
        try:
            user = User.objects.get(user_id=login_username)
        except Exception as e:
            print("error", e)
            res_data['error'] = "아이디/비밀번호가 다릅니다."
            return render(request, 'crudmember/login.html', res_data)
            
        if check_password(login_password, user.password):
            request.session['user'] = user.id
            request.session['name'] = user.name
            request.session['login_time'] = str(datetime.now())[:16]
            request.session['today'] = str(datetime.now())[:10]
            #세션 만료시간 설정 0을 넣으면 브라우져 닫을시 세션 쿠키 삭제 + DB만료기간 14일
            request.session.set_expiry(0)
            

                #세션도 딕셔너리 변수 사용과 똑같이 사용하면 된다.
                #세션 user라는 key에 방금 로그인한 id를 저장한것.
            return redirect('home')
        else:
            res_data['error'] = "아이디/비밀번호가 다릅니다."
            print("비밀번호다름")
            return render(request, 'crudmember/login.html', res_data)
    else:
        user_id = request.session.get('user')
        if user_id:
            return redirect('home')
        return render(request, 'crudmember/login.html')


def logout(request):
    try:
        request.session.clear()
    except KeyError:
        pass
    return redirect('home')


def profile(request):
    res_data = {}
    if request.method == 'GET':
        return render(request, 'crudmember/profile.html')
    if request.method == 'POST':
        # user_id = request.session.get('user')
        # 비밀번호 변경폼
        if 'cngpw' in request.POST:
            user = User.objects.get(pk=request.session.get('user'))
            oldpw = request.POST.get('old_password', None)
            if check_password(oldpw, user.password):
                newpw = request.POST.get('new_password1', None)
                newpw2 = request.POST.get('new_password2', None)
                if newpw == newpw2:
                    if len(newpw) >= 4:
                        user.password = make_password(newpw)
                        user.save()
                        # login(request, user)
                    else:
                        res_data['error'] = "길이 너무 짧음"
                        return render(request, 'crudmember/profile.html', res_data)
                else:
                    res_data['error'] = "1,2틀림"
                    return render(request, 'crudmember/profile.html', res_data)
            else:
                res_data['error'] = "old비번틀림"
                return render(request, 'crudmember/profile.html', res_data)
        return redirect('home')


def passwordfinder(request):
    res_data={}
    if request.method == 'GET':
        return render(request, 'crudmember/passwordfinder.html')  # return redirect('passwordfinder')
    if request.method == 'POST':
        if 'findpw' in request.POST:
            userid = request.POST.get('userid', None)
            name = request.POST.get('name', None)
            tel = request.POST.get('tel', None)
            try:
                user = User.objects.get(userid = userid)
            except Exception:
                res_data['error'] = "아이디없음"
                return render(request, 'crudmember/passwordfinder.html', res_data)
            if user.name == name:
                print("aaaaaaaaaaaaaaaaa", user.tel, tel)
                if user.tel == str(tel):  # tel을 숫자로받아야함 (임시)
                    result = ""    # 난수생성해서 비번초기화하기
                    for i in range(4):
                        result += choice(ascii_lowercase)
                    user.password = make_password(result)
                    user.save()
                    res_data['error'] = "비밀번호 초기화 완료 : " + result
                    return render(request, 'crudmember/passwordfinder.html', res_data)
                else:
                    res_data['error'] = "번호없음"
                    return render(request, 'crudmember/passwordfinder.html', res_data)
            else:
                res_data['error'] = "이름없음"
                return render(request, 'crudmember/passwordfinder.html', res_data)
            
        if 'sendemail' in request.POST:
            userid = request.POST.get('userid', None)
            useremail = request.POST.get('useremail', None)
            try:
                user = User.objects.get(userid = userid)
            except Exception:
                res_data['error'] = "아이디없음"
                return render(request, 'crudmember/passwordfinder.html', res_data)
            current_site = get_current_site(request)
            message = render_to_string('crudmember/user_passwordfinder_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).encode().decode(),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = "패스워드 변경 메일입니다."
            user_toemail = useremail
            email = EmailMessage(mail_subject, message, to=[user_toemail])
            email.send()
            return HttpResponse(
                '<div style="font-size: 40px; width: 100%; height:100%; display:flex; text-align:center; '
                'justify-content: center; align-items: center;">'
                '입력하신 이메일<span>로 인증 링크가 전송되었습니다.</span>'
                '</div>'
            )
            return redirect('home')


# def pwchangeauth(request, uid64, token):

#     uid = force_text(urlsafe_base64_decode(uid64))
#     user = User.objects.get(pk=uid)

#     if user is not None and account_activation_token.check_token(user, token):
#         res_data = {}
#         if request.method == 'GET':
#             return render(request, 'crudmember/passwordchangeauth.html')
#             # return redirect('home')
#         if request.method == 'POST':
#             newpw = request.POST.get('new_password1', None)
#             newpw2 = request.POST.get('new_password2', None)
#             if newpw == newpw2:
#                 if len(newpw) >= 4:
#                     user.password = make_password(newpw)
#                     user.save()
#                     # login(request, user)
#                 else:
#                     res_data['error'] = "길이 너무 짧음"
#                     return render(request, 'crudmemeber/passwordchangeauth.html', res_data)
#             else:
#                 res_data['error'] = "1,2틀림"
#                 return render(request, 'crudmemeber/passwordchangeauth.html', res_data)
#         return redirect('home')
#     else:
#         return HttpResponse('비정상적인 접근입니다.')