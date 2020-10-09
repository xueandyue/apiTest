from django.shortcuts import render
import logging,json
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response
from Login.models import UserInfo
from Common.util import init_filter_session
logger = logging.getLogger('Login')


# Create your views here.
def login(request):
    """
    登录
    """
    if request.method == 'POST':
        username = request.POST.get('account')
        password = request.POST.get('password')
        if UserInfo.objects.query_user(username, password) == 1:
            logger.info('{username} 登录成功'.format(username=username))
            request.session['login_status'] = True
            request.session['now_account'] = username
            return HttpResponseRedirect('/Index/index')
        else:
            logger.info('{username} 登录失败，请检查用户名或者密码'.format(username=username))
            request.session['login_status'] = False
            data={}
            data['tishi']='tishi();'
            return render(request, 'Login/login.html',data)
    elif request.method == 'GET':
        return render(request, 'Login/login.html')


def register(request):
    """
    注册
    """
    if request.is_ajax():
        user_info = json.loads(request.body)

        username = user_info.pop('account')
        password = user_info.pop('password')
        email = user_info.pop('email')
        msg = ''
        if UserInfo.objects.filter(username__exact=username).filter(status=1).count() > 0:
            logger.debug('{username} 已被其他用户注册'.format(username=username))
            msg = '该用户名已被注册，请更换用户名'
        elif UserInfo.objects.filter(email__exact=email).filter(status=1).count() > 0:
            logger.debug('{email} 已被其他用户注册'.format(email=email))
            msg = '邮箱已被其他用户注册，请更换邮箱'
        else:
            UserInfo.objects.create(username=username, password=password, email=email)
            logger.info('新增用户：{user_info}'.format(user_info=user_info))
            msg = 'ok'
        return HttpResponse('恭喜您，账号已成功注册' if msg == 'ok' else msg)
    else:
        return render_to_response('Login/register.html')


def login_check(func):
    """
    检查登录状态
    """
    def wrapper(request, *args, **kwargs):
        if not request.session.get('login_status'):
            return HttpResponseRedirect('/Login/login')
        return func(request, *args, **kwargs)
    return wrapper


@login_check
def log_out(request):
    """
    注销登录
    :param request:
    :return:
    """
    if request.method == 'GET':
        logger.info('{username}退出'.format(username=request.session['now_account']))
        try:
            del request.session['now_account']
            del request.session['login_status']
            init_filter_session(request, type=False)
        except KeyError:
            logging.error('session invalid')
        return HttpResponseRedirect("/Login/login/")



