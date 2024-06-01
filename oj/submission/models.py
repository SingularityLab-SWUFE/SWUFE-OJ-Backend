from django.db import models
from problem.models import Problem
from contest.models import Contest
from account.models import User

class JudgeStatus:
    COMPILE_ERROR = -2
    WRONG_ANSWER = -1
    ACCEPTED = 0
    CPU_TIME_LIMIT_EXCEEDED = 1
    REAL_TIME_LIMIT_EXCEEDED = 2
    MEMORY_LIMIT_EXCEEDED = 3
    RUNTIME_ERROR = 4
    SYSTEM_ERROR = 5
    PENDING = 6
    JUDGING = 7
    PARTIALLY_ACCEPTED = 8


class Submission(models.Model):
    id = models.AutoField(primary_key=True)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    result = models.IntegerField(db_index=True, default=JudgeStatus.PENDING)
    # 从 JudgeServer 返回的判题详情
    # 或者其它 OJ 爬取的判题信息
    info = models.JSONField(default=dict)
    language = models.TextField()
    shared = models.BooleanField(default=False)
    # 存储该提交所用时间和内存值，方便提交列表显示
    # {time_cost: "", memory_cost: "", err_info: "", score: 0}
    statistic_info = models.JSONField(default=dict)
    ip = models.TextField(null=True)

    # 检查用户能否查看此提交
    def check_user_permission(self, user, check_share=True):
        # TODO
        pass

    class Meta:
        db_table = 'submission'
        ordering = ('-create_time',)

    def __str__(self):
        return self.id
