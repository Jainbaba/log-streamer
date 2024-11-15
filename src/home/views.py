from datetime import datetime, timezone
from django.utils.timezone import make_aware
import hashlib
from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from django.core.cache import cache
from django.utils.http import quote_etag
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Level, Host, RequestMethod, LogEntry
from .serializers import (
    LevelSerializer,
    HostSerializer,
    RequestMethodSerializer,
    LogSerializer,
)


class HistoricalLogsView(APIView):
    def get(self, request):
        start = request.query_params.get("start")
        limit = int(request.query_params.get("limit", 50))
        try:
            if start:
                start_datetime = datetime.fromtimestamp(float(start))
            else:
                start_datetime = datetime.utcnow()

            start_datetime = make_aware(start_datetime)

            logs = LogEntry.objects.filter(date_time__lt=start_datetime).order_by(
                "-timestamp"
            )[:limit]

            serializer = LogSerializer(logs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response(
                {
                    "error": "Invalid date format. Please provide a valid Unix timestamp."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomLogsView(APIView):
    def get(self, request):
        end = request.query_params.get("end")
        try:
            if end:
                end_datetime = datetime.fromtimestamp(float(end))
            else:
               return Response(
                {
                    "error": "Date no found. Please add Date"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

            logs = LogEntry.objects.filter(date_time__gt=end_datetime).order_by(
                "-timestamp"
            )

            serializer = LogSerializer(logs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response(
                {
                    "error": "Invalid date format. Please provide a valid Unix timestamp."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class FilterTypeView(APIView):
    def get(self, request):
        try:

            cache_key = "filter_type_data"
            cache_timeout = 60

            cached_data = cache.get(cache_key)
            from_cache = False

            if cached_data:
                data = cached_data
                from_cache = True
            else:
                levels = LevelSerializer(Level.objects.all(), many=True).data
                hosts = HostSerializer(Host.objects.all(), many=True).data
                request_methods = RequestMethodSerializer(
                    RequestMethod.objects.all(), many=True
                ).data
                data = {
                    "levels": levels,
                    "hosts": hosts,
                    "request_methods": request_methods,
                }
                cache.set(cache_key, data, timeout=cache_timeout)

            data_str = str(data)
            etag = quote_etag(hashlib.md5(data_str.encode("utf-8")).hexdigest())

            if_none_match = request.headers.get("If-None-Match")
            if if_none_match == etag:
                return Response(status=status.HTTP_304_NOT_MODIFIED)

            response = Response(data, status=status.HTTP_200_OK)
            response["ETag"] = etag
            response["X-Cache"] = "HIT" if from_cache else "MISS"

            return response

        except ValueError:
            return Response(
                {"error": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"},
                status=status.HTTP_400_BAD_REQUEST,
            )


def health_check(request):
    db_conn_alive = True
    try:

        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
    except OperationalError:
        db_conn_alive = False

    health_status = {
        "database": db_conn_alive,
    }

    status_code = 200 if db_conn_alive else 503
    return JsonResponse(health_status, status=status_code)
