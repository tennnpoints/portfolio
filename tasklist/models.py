from django.db import models

# Create your models here.
class UserData(models.Model):
    user_name = models.CharField(max_length=128)            # ユーザー名
    mail_address = models.EmailField()                      # メールアドレス
    password = models.CharField(max_length=128)             # パスワード
    latest_update = models.DateField(blank=True, null=True) # 最終更新日

class TaskData(models.Model):
    user_id = models.IntegerField()                     # タスクの持ち主のユーザーID
    task_name = models.CharField(max_length=128)        # タスク名
    task_desc = models.CharField(max_length=512)        # タスク説明文
    status = models.BooleanField()                      # 完了/未完了
    repeat = models.BooleanField()                      # 繰り返しの有無
    deadline = models.DateField(blank=True, null=True)  # 期日(空欄あり)
    repeattype = models.IntegerField()                  # 繰り返しの方式(曜日を月曜から0~6の数字で　毎日の場合-1)
