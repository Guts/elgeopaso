# -*- coding: UTF-8 -*-
#! python3
#!/usr/bin/env python

# ###########################################################################
# ######### Libraries #############
# #################################
# Standard library
from functools import wraps
from django.views.decorators.cache import cache_page
from django.utils.decorators import available_attrs

# #############################################################################
# ######## Functions ##############
# #################################

# custom cache
def conditional_cache(decorator):
    """ Returns decorated view if user is not admin. Un-decorated otherwise """

    def _decorator(view):

        # This holds the view with cache decorator
        decorated_view = decorator(view)

        def _view(request, *args, **kwargs):

            if request.user.is_staff:     # If user is staff
                return view(request, *args, **kwargs)  # view without @cache
            else:
                # view with @cache
                return decorated_view(request, *args, **kwargs)

        return _view

    return _decorator

# managing cache according on authentication status
def cache_on_auth(timeout):
    """See: https://stackoverflow.com/q/11661503/2556577"""
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated():
                return view_func(request, *args, **kwargs)
            else:
                return cache_page(timeout)(view_func)(request, *args, **kwargs)
        return _wrapped_view
    return decorator
