import re
from urllib.parse import urlparse
import requests

from django.conf import settings
from django.core.mail import mail_managers
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin


class DiscordNotificationMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        """Send broken link emails for relevant 404 NOT FOUND responses."""

        if response.status_code >= 500 and not settings.DEBUG:
            domain = request.get_host()
            path = request.get_full_path()
            referer = request.META.get('HTTP_REFERER', '')

            if not self.is_ignorable_request(request, path, domain, referer):
                ua = request.META.get('HTTP_USER_AGENT', '<none>')
                ip = request.META.get('REMOTE_ADDR', '<none>')

                content = "```Broken %slink on %s \nReferrer: %s\nRequested URL: %s\nUser agent: %s\nIP address: %s\n```" %\
                        (('INTERNAL ' if self.is_internal_request(domain, referer) else ''), domain, referer, path, ua, ip)

                print(requests.post(settings.DISCORD_WEBHOOK_URL, json={'content': content}))
        return response

    def is_internal_request(self, domain, referer):
        """
        Return True if the referring URL is the same domain as the current
        request.
        """
        # Different subdomains are treated as different domains.
        return bool(re.match("^https?://%s/" % re.escape(domain), referer))

    def is_ignorable_request(self, request, uri, domain, referer):
        """
        Return True if the given request *shouldn't* notify the site managers
        according to project settings or in situations outlined by the inline
        comments.
        """
        # The referer is empty.
        if not referer:
            return True

        # APPEND_SLASH is enabled and the referer is equal to the current URL
        # without a trailing slash indicating an internal redirect.
        if settings.APPEND_SLASH and uri.endswith('/') and referer == uri[:-1]:
            return True

        # A '?' in referer is identified as a search engine source.
        if not self.is_internal_request(domain, referer) and '?' in referer:
            return True

        # The referer is equal to the current URL, ignoring the scheme (assumed
        # to be a poorly implemented bot).
        parsed_referer = urlparse(referer)
        if parsed_referer.netloc in ['', domain] and parsed_referer.path == uri:
            return True

        return any(pattern.search(uri) for pattern in settings.IGNORABLE_404_URLS)


class AllowOnlyStaffMiddleware(MiddlewareMixin):
    '''
    This middleware used after authenticating middlewares, 
    to block non-staff users from some urls.
    '''
    
    
    def process_response(self, request, response):
        ALLOWED_PATHS = [
            '/account/login/',
            '/endpoint/',
        ]

        if request.user.is_staff:
            return response

        else:
            if request.path in ALLOWED_PATHS:
                return response
            return HttpResponseForbidden('Forbidden 403')