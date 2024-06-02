from rest_framework import serializers

from .models import Contest, ACMContestRank, OIContestRank


class CreateContestSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=128)
    description = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    password = serializers.CharField(max_length=128, required=False)
    rule_type = serializers.ChoiceField(choices=['ACM', 'OI'])
    visible = serializers.BooleanField(default=True)
    contest_type = serializers.CharField(max_length=128)

    class Meta:
        model = Contest
        fields = ('title', 'description', 'start_time', 'id',
                  'end_time', 'password', 'rule_type', 'visible', 'contest_type')


class ContestAdminSerializer(serializers.ModelSerializer):

    status = serializers.CharField()

    class Meta:
        model = Contest
        fields = '__all__'


class ContestSerializer(ContestAdminSerializer):

    class Meta:
        model = Contest
        exclude = ('password', 'visible')


class ACMContestRankSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username')

    class Meta:
        model = ACMContestRank
        fields = ('username', 'submission_number',
                  'accepted_number', 'total_time', 'submission_info', 'contest')


class OIContestRankSerializer(serializers.ModelSerializer):

    class Meta:
        model = OIContestRank
        fields = '__all__'
