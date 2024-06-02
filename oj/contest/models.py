from django.db import models
from account.models import User
from ckeditor.fields import RichTextField
from django.utils import timezone


class ContestStatus(object):
    NOT_START = 0
    ENDED = 1
    RUNNING = 2


class ContestType(object):
    TRAINING = 'training'
    RATED = 'rated'


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
    contest_type = models.CharField(default=ContestType.TRAINING, max_length=50)


    @property
    def status(self):
        if self.start_time > timezone.now():
            return ContestStatus.NOT_START
        elif self.end_time < timezone.now():
            return ContestStatus.ENDED
        else:
            return ContestStatus.RUNNING

    def _force_end(self):
        self.end_time = timezone.now()
        self.save()
    
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
    # {"23": {"accepted": True, "ac_time": 8999, "failed_number": 2, "is_first_ac": True}}
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
