from django.shortcuts import render
from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from django.http import JsonResponse
import datetime
from .util import TasksUtil

import tasklist.const as const

from ..models import UserData,TaskData

class MypageView(View):
    def get(self, request):
        params = {}
        
        # セッションからユーザーID取得
        uid = request.session['userid']

        # 今日の日付を取得
        today = datetime.date.today()
        print('today is:',today)
        
        # 更新の有無を管理する変数の用意
        refresh = False
        
        # モデルから最終更新日を取得して比較
        currentuser = UserData.objects.filter(id=uid)[0]
        print('Latest Update:',currentuser.latest_update)
        if currentuser.latest_update == None :
            refresh = True
        elif currentuser.latest_update < today :
            refresh = True

        # 更新が必要だったら行う
        if refresh == True :
            # データ更新
            task_refresh = TaskData.objects.filter(user_id=uid,repeat=True)
            for tasks in task_refresh :
                if tasks.deadline != None :     # 日付が空白ではなかった場合
                    if tasks.deadline < today :
                        # 新しい締切の設定
                        tasks.deadline = TasksUtil.new_deadline(tasks.repeattype)
                        tasks.status = False
                        tasks.save()

            currentuser.latest_update = today
            currentuser.save()
            print(currentuser.latest_update)

        print('Refresh:',refresh)

        task_undone = TaskData.objects.filter(user_id=uid,status=False).order_by('-id')
        for tasks in task_undone :
            tasks.timeover = False
            if tasks.repeat == False and tasks.deadline != None :
                if tasks.deadline < today :
                    tasks.timeover = True

        task_done = TaskData.objects.filter(user_id=uid,status=True).order_by('-id')

        params = { 'task_undone':task_undone,'task_done':task_done }
        return render(request, 'tasks/mypage.html', params)
    
    def post(self,request):
        params = {}
        task_id = request.POST.get('task_id')
        task_id = int(task_id)
        status = request.POST.get('status')
        task = TaskData.objects.filter(id=task_id)[0]
        if status == 'toggle' :
            print(task.status)
            task.status = (not task.status)
            print(task.status)
            task.save()
        elif status == 'delete' :
            task.delete()
        return JsonResponse(params)

class NewTaskView(View):
    def get(self, request):
        params = {}
        return render(request, 'tasks/newtask.html', params)
    
    def post(self,request):
        params = {}
        error = 0
        descerror = const.CLEAR
        nameerror = const.CLEAR
        repeaterror = const.CLEAR
        uid = request.session['userid']
        task_name = request.POST.get('task_name')
        task_desc = request.POST.get('task_desc')
        repeat = request.POST.get('repeat')
        repeattype = request.POST.get('repeattype')
        repeattype = int(repeattype)
        if len(task_name) > 128 :
            nameerror = const.ERROR
        if len(task_desc) > 512 :
            descerror = const.ERROR
        if repeat == '1' :
            if repeattype != -1 :
                repeat = True
                deadline = TasksUtil.new_deadline(repeattype)
            else :
                repeaterror = const.ERROR
        else :
            repeat = False
            deadline = None

        error = descerror + nameerror + repeaterror

        if error == 0 :
            nt = TaskData.objects.create(user_id=uid, task_name=task_name, task_desc=task_desc, status=False, repeat=repeat, repeattype=repeattype, deadline=deadline)
            return JsonResponse(params)
        else :
            params = {'error':1,'descerror':descerror,'nameerror':nameerror,'repeaterror':repeaterror}
            return JsonResponse(params)


class SettingView(View):
    def get(self, request):
        uid = request.session['userid']
        user = UserData.objects.filter(id=uid)[0]
        params = {'user_name': user.user_name, 'mail_address': user.mail_address}
        return render(request, 'tasks/setting.html', params)

    def post(self, request):        
        uid = request.session['userid']
        params = {'error': const.CLEAR, 'errormsg': '', 'nameerror': const.CLEAR, 'mailerror': const.CLEAR, 'pwderror': const.CLEAR}
        req = request.POST
        behavior = req.get('behavior')
        uname = req.get('uname')
        mail = req.get('uid')
        mailconf = req.get('uidconf')
        pwd = req.get('pwd')
        pwdconf = req.get('pwdconf')
        user = UserData.objects.filter(id=uid)[0]

        if behavior == 'username' :
            if uname == '' :
                errormsg = 'ユーザー名が空欄です'
                params['error'] = const.ERROR
                params['nameerror'] = const.ERROR
                params['nameerrormsg'] = errormsg
            
            if params['nameerror'] != const.ERROR :
                user.user_name = uname
                user.save()

        elif behavior == 'mailaddress' :
            if mail == '' and mailconf == '' :
                errormsg = 'メールアドレスが空欄です'
                params['error'] = const.ERROR
                params['mailerror'] = const.ERROR
                params['mailerrormsg'] = errormsg

            if mail != mailconf :
                errormsg = '確認用のメールアドレスが異なります'
                params['error'] = const.ERROR
                params['mailerror'] = const.ERROR
                params['mailerrormsg'] = errormsg
            
            if params['mailerror'] != const.ERROR :
                user.mail_address = mail
                user.save()

        elif behavior == 'password' :
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
            
            if params['pwderror'] != const.ERROR :
                user.password = pwd
                user.save()
        params['behavior'] = behavior 
        return JsonResponse(params)