import dateutil.parser
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated

from utils.api import APIView
from utils.token import JWTAuthTokenSerializer
from account.models import User
from problem.models import ProblemSet
from .models import Contest, ACMContestRank, OIContestRank, ContestStatus
from .serializers import (ContestSerializer,
                          ContestAdminSerializer,
                          ACMContestRankSerializer,
                          OIContestRankSerializer,
                          CreateContestSerializer)


class ContestViewAPI(APIView):

    def check_password(self, password, contest):
        if password is None:
            return self.error("Password is required")
        elif password != contest.password:
            return self.error("Password is incorrect")
        else:
            return self.success(ContestSerializer(contest).data)

    def get(self, request):
        contest_id = request.GET.get('contest_id')
        if not contest_id:
            return self.error("contest_id is required")
        try:
            contest = Contest.objects.get(id=contest_id, visible=True)
            if contest.password:
                return self.check_password(request.GET.get('password'), contest)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")


class ContestRegisterAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthTokenSerializer]

    def post(self, request):
        user = request.user
        contest_id = request.POST.get('contest_id')
        if not contest_id:
            return self.error("contest_id is required")
        try:
            contest = Contest.objects.get(id=contest_id, visible=True)
            if contest.status == ContestStatus.ENDED:
                return self.error("Contest has ended")
            rule_type = contest.rule_type
            if rule_type == "ACM":
                ACMContestRank.objects.create(user=user, contest=contest)
            elif rule_type == "OI":
                OIContestRank.objects.create(user=user, contest=contest)
            else:
                return self.error("Unsupported rule type")
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")


class ContestAdminAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthTokenSerializer]

    def post(self, request):
        user = request.user
        if not user.is_admin:
            return self.error("Normal user has no permission to start a contest.")

        data = request.data

        if data.get("password") and data["password"] == "":
            data["password"] = None
        start_time = dateutil.parser.parse(data["start_time"])
        end_time = dateutil.parser.parse(data["end_time"])

        if start_time >= end_time:
            return self.error("Start time must occur earlier than end time")

        info = {
            "title": data["title"],
            "description": data["description"],
            "start_time": start_time,
            "end_time": end_time,
            "password": data.get("password"),
            "visible": data["visible"],
            "created_by": user,
            "contest_type": data["contest_type"]
        }
        if info['contest_type'] == 'training':
            problem_set_id = data.get("problem_set_id")
            if problem_set_id is None:
                return self.error("Problem set must be provided for training contests.")

            try:
                problem_set = ProblemSet.objects.get(id=problem_set_id)
            except ProblemSet.DoesNotExist:
                return self.error("Problem set does not exist.")

        contest = Contest.objects.create(**info)
        problem_set.contest = contest
        problem_set.save()

        return self.success(CreateContestSerializer(contest).data)

    def put(self, request):
        user = request.user
        if not user.is_admin:
            return self.error("Normal user has no permission to start a contest.")

        data = request.data.copy()
        try:
            contest = Contest.objects.get(id=data['id'])
        except Contest.DoesNotExist:
            return self.error(f"Contest {data['id']} does not exist")

        if contest.created_by != user:
            return self.error("You are not the creator of this contest")
        if data.get("password") and data["password"] == "":
            data["password"] = None

        data["start_time"] = dateutil.parser.parse(data["start_time"])
        data["end_time"] = dateutil.parser.parse(data["end_time"])

        if data["start_time"] >= data["end_time"]:
            return self.error("Start time must occur earlier than end time")

        for k, v in data.items():
            setattr(contest, k, v)
        contest.save()

        return self.success(ContestAdminSerializer(contest).data)


class ContestRankAPI(APIView):

    def get(self, request):
        contest_id = request.GET.get('contest_id')
        if not contest_id:
            return self.error("contest_id is required")
        try:
            contest = Contest.objects.get(id=contest_id, visible=True)
            if contest.password:
                if request.GET.get('password') is None:
                    return self.error("Password is required")
                if contest.password != request.GET.get('password'):
                    return self.error("Password is incorrect")
            rule_type = contest.rule_type
            if rule_type == "ACM":
                ranks = ACMContestRank.objects.filter(
                    contest=contest).order_by('-accepted_number', 'total_time')
                serializers = ACMContestRankSerializer(ranks, many=True)
                return self.success(serializers.data)
            elif rule_type == "OI":
                ranks = OIContestRank.objects.filter(
                    contest=contest).order_by('-total_score')
                serializers = OIContestRankSerializer(ranks, many=True)
                return self.success(serializers.data)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
