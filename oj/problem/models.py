from django.db import models
from ckeditor.fields import RichTextField


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
 