import json
import logging

from django.utils import timezone

logger = logging.getLogger('user_activity')


class UserActivityLoggingMiddleware:
    """
    Логирует каждое обращение пользователя к сайту
    с минимально необходимыми данными и маскировкой чувствительных полей.
    """

    SENSITIVE_KEYS = {'password', 'passwd', 'pwd', 'token', 'csrfmiddlewaretoken'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._log_activity(request, response)
        return response

    def _log_activity(self, request, response):
        try:
            payload = {
                'timestamp': timezone.now().isoformat(),
                'user': request.user.get_username() if request.user.is_authenticated else 'anonymous',
                'method': request.method,
                'path': request.get_full_path(),
                'status': getattr(response, 'status_code', None),
                'ip': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }

            if request.GET:
                payload['query'] = self._sanitize_querydict(request.GET)

            if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'} and request.POST:
                payload['body'] = self._sanitize_querydict(request.POST)

            logger.info(json.dumps(payload, ensure_ascii=False))
        except Exception:
            logger.exception('Не удалось записать лог пользовательской активности')

    def _sanitize_querydict(self, querydict):
        cleaned = {}
        for key, values in querydict.lists():
            if key.lower() in self.SENSITIVE_KEYS:
                cleaned[key] = '***'
            else:
                cleaned[key] = values if len(values) > 1 else values[0]
        return cleaned

    def _get_client_ip(self, request):
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

