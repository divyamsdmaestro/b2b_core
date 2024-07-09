class DisableCSRFMiddleware:
    """
    Disables the applications csrf checking. Used in the MIDDLEWARES in the settings.py.

    This is implemented because at some cases when the user takes long time to submit
    forms, it causes errors. So since that use case is necessary in the app
    CSRF token is removed.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, "_dont_enforce_csrf_checks", True)  # noqa
        return self.get_response(request)
