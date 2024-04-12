# ref: https://github.com/QingdaoU/OnlineJudge/blob/master/utils/api/api.py
import functools
import json
import logging

from django.http import HttpResponse, QueryDict
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

logger = logging.getLogger("")


class APIError(Exception):
    def __init__(self, msg, err=None):
        self.err = err
        self.msg = msg
        super().__init__(err, msg)


class ContentType(object):
    '''
        可接受的 Content-Type 类型
        
        1. application/json: 用于请求的 JSON 数据
        2. application/json;charset=UTF-8: 同上, 支持 UTF-8 编码
        3. application/x-www-form-urlencoded: 表单数据
        4. application/octet-stream: 二进制数据流
    '''
    json_request = "application/json"
    json_response = "application/json;charset=UTF-8"
    url_encoded_request = "application/x-www-form-urlencoded"
    binary_response = "application/octet-stream"


class JSONParser(object):
    content_type = ContentType.json_request

    @staticmethod
    def parse(body):
        return json.loads(body.decode("utf-8"))


class URLEncodedParser(object):
    content_type = ContentType.url_encoded_request

    @staticmethod
    def parse(body):
        return QueryDict(body)


class JSONResponse(object):
    content_type = ContentType.json_response

    @classmethod
    def response(cls, data):
        resp = HttpResponse(json.dumps(data, indent=4),
                            content_type=cls.content_type)
        resp.data = data
        return resp


class APIView(APIView):
    '''
        对 rest_framework.views.APIView 的重载,
        
        1. 添加了 success 和 error 方法,
        使得返回数据格式统一 { "error" : err, "data" : data }.
        
        2. 约定了请求数据类型只能是 Content-Type 中的几类.
        3. 优化了内部错误的 HTTP 响应.
    '''
    request_parsers = (JSONParser, URLEncodedParser)
    response_class = JSONResponse

    def _get_request_data(self, request):
        if request.method not in ["GET", "DELETE"]:
            body = request.body
            content_type = request.META.get("CONTENT_TYPE")
            if not content_type:
                raise ValueError("content_type is required")
            for parser in self.request_parsers:
                if content_type.startswith(parser.content_type):
                    break
            # else means the for loop is not interrupted by break
            else:
                raise ValueError("unknown content_type '%s'" % content_type)
            if body:
                return parser.parse(body)
            return {}
        return request.GET

    def response(self, data):
        return self.response_class.response(data)

    def success(self, data=None) -> HttpResponse:
        '''
            返回请求成功响应.
        '''
        return self.response({"error": None, "data": data})

    def error(self, msg="error", err="error") -> HttpResponse:
        '''
            返回请求失败响应.
        '''
        return self.response({"error": err, "data": msg})

    def extract_errors(self, errors, key="field"):
        if isinstance(errors, dict):
            if not errors:
                return key, "Invalid field"
            key = list(errors.keys())[0]
            return self.extract_errors(errors.pop(key), key)
        elif isinstance(errors, list):
            return self.extract_errors(errors[0], key)

        return key, errors

    def invalid_serializer(self, serializer):
        key, error = self.extract_errors(serializer.errors)
        if key == "non_field_errors":
            msg = error
        else:
            msg = f"{key}: {error}"
        return self.error(err=f"invalid-{key}", msg=msg)

    def server_error(self):
        return self.error(err="server-error", msg="server error")

    def paginate_data(self, request, query_set, object_serializer=None):
        """
        :param request: django 的 request
        :param query_set: django model 的 query set或者其他list like objects
        :param object_serializer: 用来序列化 query set, 如果为 None, 则直接对 query set 切片
        :return:
        """
        try:
            limit = int(request.GET.get("limit", "10"))
        except ValueError:
            limit = 10
        if limit < 0 or limit > 250:
            limit = 10
        try:
            offset = int(request.GET.get("offset", "0"))
        except ValueError:
            offset = 0
        if offset < 0:
            offset = 0
        results = query_set[offset:offset + limit]
        if object_serializer:
            count = query_set.count()
            results = object_serializer(results, many=True).data
        else:
            count = query_set.count()
        data = {"results": results,
                "total": count}
        return data

    def dispatch(self, request, *args, **kwargs):
        if self.request_parsers:
            try:
                request.data = self._get_request_data(self.request)
            except ValueError as e:
                return self.error(err="invalid-request", msg=str(e))
        try:
            return super(APIView, self).dispatch(request, *args, **kwargs)
        except APIError as e:
            ret = {"msg": e.msg}
            if e.err:
                ret["err"] = e.err
            return self.error(**ret)
        except Exception as e:
            logger.exception(e)
            return self.server_error()


class CSRFExemptAPIView(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CSRFExemptAPIView, self).dispatch(request, *args, **kwargs)


def validate_serializer(serializer):
    """
    @validate_serializer(TestSerializer)
    def post(self, request):
        return self.success(request.data)
    """
    def validate(view_method):
        @functools.wraps(view_method)
        def handle(*args, **kwargs):
            self = args[0]
            request = args[1]
            s = serializer(data=request.data)
            if s.is_valid():
                request.data = s.data
                request.serializer = s
                return view_method(*args, **kwargs)
            else:
                return self.invalid_serializer(s)

        return handle

    return validate
