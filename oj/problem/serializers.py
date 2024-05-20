from rest_framework import serializers
from .models import Problem, ProblemSet
from django import forms

class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = '__all__'


class CreateProblemSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(
        max_length=32, allow_blank=True, allow_null=True)
    title = serializers.CharField(max_length=1024)
    description = serializers.CharField()
    input = serializers.CharField()
    output = serializers.CharField()
    test_case_id = serializers.CharField(max_length=32)
    time_limit = serializers.IntegerField(min_value=1, max_value=1000 * 60)
    memory_limit = serializers.IntegerField(min_value=1, max_value=1024)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=32), allow_empty=False)
    hint = serializers.CharField(allow_blank=True, allow_null=True)
    source = serializers.CharField(
        max_length=256, allow_blank=True, allow_null=True)
        


class ProblemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'title', 'source', 'tag', 'remote_id', 'difficulty',
                  'total_submission_number', 'solved_submission_number']


class ProblemSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemSet
        fields = '__all__'
        

class TestCaseUploadForm(forms.Form):
    spj = forms.CharField(max_length=12)
    test_cases = forms.FileField()
