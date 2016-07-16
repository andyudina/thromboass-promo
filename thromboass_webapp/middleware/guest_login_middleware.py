import time

from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from thromboass_webapp.utils import generate_random_sequence

class GuestLoginMiddleware(object):
    def _guest_login(self, request, username):
        User.objects.create_user(*([username, ] * 3))
        user = authenticate(username=username, password=username)
        login(request, user)
        
    def process_request(self, request):
        if 'admin' in request.path: return #no guests in admin 
        if request.user.is_authenticated(): return 
        username = '{}_{}'.format(generate_random_sequence(8), time.time())
        self._guest_login(request, username)
