from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from challenge.models import JoinCode


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                if 'code' in request.POST:
                    code = JoinCode.objects.get(key=request.POST['code'])
                    if code:
                        user.groups.add(code.group_id)
                return user
        return None
