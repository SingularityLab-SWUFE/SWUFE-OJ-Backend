from django.db import models
from ckeditor.fields import RichTextField
from account.models import User
from contest.models import Contest

class ProblemTag(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'tag'


class ProblemDifficulty(object):
    High = 'High'
    Mid = 'Mid'
    Low = 'Low'


class Problem(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)
    # remote
    is_remote = models.BooleanField(default=False, null=True)
    remote_id = models.CharField(max_length=50, null=True)
    source = models.CharField(max_length=255, null=True)
    # 标签的多对多关联
    tag = models.ManyToManyField(to=ProblemTag)
    difficulty = models.CharField(max_length=10, default="Easy")
    # problem detail
    description = RichTextField()
    input = RichTextField()
    output = RichTextField()
    # [{input: "test", output: "123"}, {input: "test123", output: "456"}]
    samples = models.JSONField(null=True)
    # None for remote problem
    test_case_id = models.TextField(null=True, default=None)
    hint = RichTextField(null=True)
    # submission info
    total_submission_number = models.IntegerField(default=0)
    solved_submission_number = models.IntegerField(default=0)
    # ms/MB
    # C/C++
    standard_time_limit = models.IntegerField(default=1000)
    # Default as 256MB
    standard_memory_limit = models.IntegerField(default=256)
    # JAVA, python, etc.
    other_time_limit = models.IntegerField(default=2000)
    other_memory_limit = models.IntegerField(default=512)

    def __repr__(self):
        return f"<Problem {self.title}: id={self.id}>"
    
    class Meta:
        db_table = 'problem'

class ProblemSet(models.Model):
    name = models.TextField(max_length=200, verbose_name="名字")
    contest = models.ForeignKey(Contest, null=True, on_delete=models.CASCADE)
    description = models.TextField(verbose_name="描述")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="创建用户")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    last_update = models.DateTimeField(auto_now=True, verbose_name="最近更新时间")
    problems_included = models.ManyToManyField(Problem, related_name='included_in', verbose_name="包含的题目")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'problem_set'