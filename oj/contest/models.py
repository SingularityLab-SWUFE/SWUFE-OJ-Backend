from django.db import models
from account.models import User
from ckeditor.fields import RichTextField


class Contest(models.Model):
    title = models.TextField()
    description = RichTextField()
    # 是否需要密码
    password = models.TextField(null=True)
    # ACM/OI
    rule_type = models.TextField(default='ACM')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    visible = models.BooleanField(default=True)

    class Meta:
        db_table = "contest"
        ordering = ("-start_time",)


class ContestRank(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    submission_number = models.IntegerField(default=0)

    class Meta:
        abstract = True


class ACMContestRank(ContestRank):
    accepted_number = models.IntegerField(default=0)
    # total_time is only for ACM contest, total_time =  ac time + none-ac times * 20 * 60
    total_time = models.IntegerField(default=0)
    # {"23": {"is_ac": True, "ac_time": 8999, "error_number": 2, "is_first_ac": True}}
    # key is problem id
    submission_info = models.JSONField(default=dict)

    class Meta:
        db_table = "acm_contest_rank"
        unique_together = (("user", "contest"),)


class OIContestRank(ContestRank):
    total_score = models.IntegerField(default=0)
    # {"23": 333}
    # key is problem id, value is current score
    submission_info = models.JSONField(default=dict)

    class Meta:
        db_table = "oi_contest_rank"
        unique_together = (("user", "contest"),)
