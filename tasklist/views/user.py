from django.shortcuts import render
from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from django.http import JsonResponse
from django.core.mail import EmailMessage

import tasklist.const as const

from .util import TasksUtil
from ..models import UserData,TaskData


class LoginView(View):
    """ ログイン処理 """
    def get(self, request):
        params = {}
        return render(request, 'tasks/login.html', params)

    def post(self, request):
        # フォームからメールアドレスとパスワードを取得
        form_uid = request.POST.get('userid')   
        form_pw = request.POST.get('password')
        # フォームの情報と一致するユーザーを取り出す
        u = UserData.objects.filter(mail_address__iexact=form_uid).filter(password__exact=form_pw)
        if len(u) == 1 :    # 合致するユーザー情報が一つだけあった場合ログインの処理
            # セッションにユーザー情報を書き込む
            request.session['userid'] = u[0].id
            request.session['username'] = u[0].user_name
            # マイページにリダイレクト
            return redirect('tasks:mypage')
        else:               # 合致しなければもとに戻る
            # ログイン画面のフォームにメールアドレスを予め書き込む
            params = {'mail': form_uid, 'error': const.ERROR}
            return render(request, 'tasks/login.html', params)


class RegisterView(View):
    """ 新規ユーザー登録処理 """
    def get(self, request):
        params = {'error': const.CLEAR, 'errormsg': ''}
        return render(request, 'tasks/register.html', params)

    def post(self, request):
        params = {'error': const.CLEAR, 'errormsg': ''}
        req = request.POST
        uname = req.get('uname')
        uid = req.get('uid')
        uidconf = req.get('uidconf')
        pwd = req.get('pwd')
        pwdconf = req.get('pwdconf')
        params = { 'error': const.CLEAR, 'nameerror': const.CLEAR, 'uiderror': const.CLEAR, 'pwderror': const.CLEAR }
        if uname == '' :
            errormsg = 'ユーザー名が空欄です'
            params['error'] = const.ERROR
            params['nameerror'] = const.ERROR
            params['nameerrormsg'] = errormsg
            
        if uid == '' and uidconf == '' :
            errormsg = 'メールアドレスが空欄です'
            params['error'] = const.ERROR
            params['uiderror'] = const.ERROR
            params['uiderrormsg'] = errormsg

        if uid != uidconf :
            errormsg = '確認用のメールアドレスが異なります'
            params['error'] = const.ERROR
            params['uiderror'] = const.ERROR
            params['uiderrormsg'] = errormsg
            
        if pwd == '' and pwdconf == '' :
            errormsg = 'パスワードが空欄です'
            params['error'] = const.ERROR
            params['pwderror'] = const.ERROR
            params['pwderrormsg'] = errormsg

        if pwd != pwdconf :
            errormsg = '確認用のパスワードが異なります'
            params['error'] = const.ERROR
            params['pwderror'] = const.ERROR
            params['pwderrormsg'] = errormsg

        # if 登録済みのメールアドレスかどうか
        u = UserData.objects.filter(mail_address__iexact=uid)
        if len(u) != 0 :
            errormsg = '既に登録されているメールアドレスです'
            params['error'] = const.ERROR
            params['uiderror'] = const.ERROR
            params['uiderrormsg'] = errormsg

        if params['error'] == const.CLEAR :
            #ここに新規登録の処理
            um = UserData.objects.create(user_name=uname, mail_address=uid, password=pwd)
            print('model',um)
            #ここにセッション書き込み
            request.session['userid'] = UserData.objects.filter(mail_address__iexact=uid)[0].id
            request.session['username'] = uname

        return JsonResponse(params)

class PwdResetView(View):
    def get(self, request):
        params = {'error': const.CLEAR, 'alertmsg': ''}
        return render(request, 'tasks/pwd_reset.html', params)

    def post(self, request):

        req = request.POST
        uid = req.get('uid')
        u = UserData.objects.filter(mail_address__iexact=uid)
        error = const.CLEAR
        alertmsg = ''
        if len(u) != 0:
            newpwd = TasksUtil.generate_newpwd(12)
            print('new pwd:',newpwd)
            u[0].password = newpwd
            u[0].save()
            subject = 'Tasklist パスワードリセット'
            message = 'Tasklistのパスワードがリセットされました。\r\n新しいパスワード:'+newpwd
            from_email = 'tennn.points@gmail.com'
            recipient_list = [uid]
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.send()
            error = const.CLEAR
            alertmsg = 'パスワードがリセットされました。登録しているメールアカウントをご確認ください'
        else :
            error = const.ERROR
            alertmsg = '登録されていないメールアドレスです'

        '''
        メール送信用のコード
        subject = "Email Test"
        message = "Email Test"
        from_email = 'tennn.points@gmail.com'  # 送信者
        recipient_list = ["tennn.points@gmail.com"]  # 宛先リスト
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.send()
        '''
        
        params = {'error': error , 'alertmsg': alertmsg}

        return JsonResponse(params)



