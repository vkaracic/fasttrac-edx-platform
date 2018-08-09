import json
import logging

import requests
from django.conf import settings

LOG = logging.getLogger(__name__)


class FTSlackErrorMiddleware(object):
    """Intercepts an error and send the error message with additional information to slack."""
    def process_exception(self, request, exception):
        if settings.SLACK_WEBHOOK_URL:
            response = requests.post(
                settings.SLACK_WEBHOOK_URL, data=json.dumps({
                    'attachments': [
                        {
                            'fallback': str(exception),
                            'pretext': 'New error on {}'.format(request.META.get('HTTP_HOST')),
                            'color': 'danger',
                            'fields': [
                                {'title': 'path', 'value': request.META.get('PATH_INFO')},
                                {'title': 'method', 'value': request.method, 'short': True},
                                {
                                    'title': 'data',
                                    'value': request.GET if request.method == 'GET' else request.POST,
                                    'short': True
                                },
                                {'title': 'user', 'value': request.user.username, 'short': True},
                                {'title': 'user agent', 'value': request.META.get('HTTP_USER_AGENT')},
                                {'title': 'exception', 'value': '`{}`'.format(str(exception))},
                            ]
                        }
                    ],
                    'username': 'FT Server Error',
                    'icon_emoji': ':x:',
                }), headers={'Content-Type': 'application/json'}
            )

            if response.status_code != 200:
                LOG.error(
                    'Request to Slack returned an error %s, response: \n%s',
                    response.status_code, response.text
                )
        return None