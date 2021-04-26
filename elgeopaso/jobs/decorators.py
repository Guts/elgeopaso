#! python3  # noqa: E265

# #############################################################################
# ######## Functions ##############
# #################################


# custom cache
def conditional_cache(decorator):
    """Returns decorated view if user is not admin. Un-decorated otherwise"""

    def _decorator(view):

        # This holds the view with cache decorator
        decorated_view = decorator(view)

        def _view(request, *args, **kwargs):

            if request.user.is_staff:  # If user is staff
                return view(request, *args, **kwargs)  # view without @cache
            else:
                # view with @cache
                return decorated_view(request, *args, **kwargs)

        return _view

    return _decorator
