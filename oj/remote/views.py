from rest_framework.permissions import IsAuthenticated

from utils.token import JWTAuthTokenSerializer
from utils.api import APIView
from problem.serializers import ProblemSerializer
from .ojs.hdu import HDUSender

class RemoteProblemAPI(APIView):
    '''
        向数据库添加远程 oj 题目信息
    '''
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthTokenSerializer]

    def post(self, request):
        source = request.POST.get('source')
        remote_id = request.POST.get('remote_id')
        
        if source == 'HDU':
            client = HDUSender()
            problem = client.get_problem_info(remote_id)
            serializer = ProblemSerializer(problem)
            return self.success(data=serializer.data)
        elif source == 'Codeforces':
            # TODO
            pass
        else:
            return self.error(msg='暂不支持该远程 OJ')