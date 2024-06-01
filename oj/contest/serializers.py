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

    class Meta:
        model = Contest
        fields = ('title', 'description', 'start_time',
                  'end_time', 'password', 'rule_type', 'visible')


class ContestAdminSerializer(serializers.ModelSerializer):

    status = serializers.CharField()

    class Meta:
        model = Contest
        fields = '__all__'


class ContestSerializer(ContestAdminSerializer):

    class Meta:
        model = Contest
        exclude = ('password', 'visible')


class ACMContestRankSerializer(ContestSerializer):

    class Meta:
        model = ACMContestRank
        fields = '__all__'


class OIContestRankSerializer(ContestSerializer):
    
    class Meta:
        model = OIContestRank
        fields = '__all__'
