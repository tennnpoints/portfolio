from django.urls import path
from tasklist.views import user
from tasklist.views import mypage

app_name = 'tasks'

urlpatterns = [
    path('', user.LoginView.as_view(),name='top'),
    path('login', user.LoginView.as_view(),name='login'),
    path('register', user.RegisterView.as_view(),name='register'),
    path('pwd_reset', user.PwdResetView.as_view(),name='pwd_reset'),
    path('mypage', mypage.MypageView.as_view(),name='mypage'),
    path('newtask', mypage.NewTaskView.as_view(),name='newtask'),
    path('setting', mypage.SettingView.as_view(),name='setting'),
]