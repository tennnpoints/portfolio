import datetime
import random
import string
class TasksUtil:
    """
    タスク管理の共通処理用の関数のためのクラス
    """

    def new_deadline(weekday):  
        """
        曜日繰り返しの次の締切を計算する関数
        parameters
        weekday : int
            次の締切の曜日
        """

        today = datetime.datetime.today()
        newdeadline = today + datetime.timedelta(days=7 - today.weekday() + weekday ) - datetime.timedelta(days=1)
        return newdeadline

    def generate_newpwd(n: int):
        random_list = [random.choice(string.ascii_letters + string.punctuation) for n in range(n)]
        return "".join(random_list)