from rest_framework import serializers
from .models import Submission


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'


class SubmissionDisplaySerializer(serializers.ModelSerializer):

    problem_title = serializers.CharField(
        source='problem.title', read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'create_time', 'username',
                  'result', 'language', 'problem_title']
