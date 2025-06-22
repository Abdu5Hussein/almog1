from functools import wraps
from django.http import Http404
from django.contrib.auth.decorators import user_passes_test

def permission_required_404(perm, login_url=None):
    """
    Like @permission_required but raises 404 instead of 403 if the permission is denied.
    """
    def check_perms(user):
        if user.has_perm(perm):
            return True
        raise Http404("Page not found")

    return user_passes_test(check_perms, login_url=login_url)