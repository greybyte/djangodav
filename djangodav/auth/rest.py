# Portions (c) 2014, Alexander Klimenko <alex@erix.ru>
# All rights reserved.
#
# Copyright (c) 2011, SmartFile <btimby@smartfile.com>
# All rights reserved.
#
# This file is part of DjangoDav.
#
# DjangoDav is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DjangoDav is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with DjangoDav.  If not, see <http://www.gnu.org/licenses/>.
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from djangodav.responses import HttpResponseUnAuthorized
from rest_framework.exceptions import APIException


class RestAuthViewMixIn(object):
    authentications = NotImplemented

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() != 'options':
            user_auth_tuple = None
            authenticate_header = None
            for auth in self.authentications:
                try:
                    class RequestWrapper(object):
                        """ simulates django-rest-api request wrapper """
                        def __init__(self, request):
                            self._request = request
                        def __getattr__(self, attr):
                            return getattr(self._request, attr)

                    user_auth_tuple = auth.authenticate(RequestWrapper(request))

                    # did authentication succeed? if yes, don't try further
                    if user_auth_tuple:
                        break

                    # store authenticate header, for later use
                    if not authenticate_header:
                        authenticate_header = auth.authenticate_header(request)

                except APIException as e:
                    return HttpResponse(e.detail, status=e.status_code)

            if not user_auth_tuple is None:
                user, auth = user_auth_tuple
            else:
                resp = HttpResponseUnAuthorized("Not Authorised")
                resp['WWW-Authenticate'] = authenticate_header
                return resp

            request.user = user
            request.auth = auth
        return super(RestAuthViewMixIn, self).dispatch(request, *args, **kwargs)
