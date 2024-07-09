import datetime
import json
import logging
import random
import secrets
import string
import time
import typing
from datetime import datetime as dt

from dateutil import tz
from django.conf import settings
from django.db import DEFAULT_DB_ALIAS
from requests import request

from apps.tenant_service.middlewares import get_current_db_name, get_current_tenant_details, set_db_for_router
from config.settings import IDP_CONFIG

logger = logging.getLogger(__name__)


def create_log(data: typing.Any, category: str):
    """
    A centralized function to create the app logs. Just in case some
    extra pre-processing are to be added in the future.
    """

    # assert data and category, "The passed parameters cannot be None while creating log."
    # apps.get_model("common.Log").objects.create(data=data, category=category)

    if settings.DEBUG:
        print("Log: ", data, category)  # noqa


def get_display_name_for_slug(slug: str):
    """
    For a given string slug this generates the display name for the given slug.
    This generated display name will be displayed on the front end.
    """

    try:
        return slug.replace("_", " ").title()
    except:  # noqa
        return slug


def flatten(value):
    return [item for sublist in value for item in sublist]


def random_n_digits(n):
    """Returns a random number with `n` length."""

    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return str(random.randint(range_start, range_end))


def random_n_token(n=10):
    """Generate a random string with numbers and characters with `n` length."""

    allowed_characters = string.ascii_letters + string.digits  # contains char and digits
    return "".join(secrets.choice(allowed_characters) for _ in range(n))


def random_n_strong_token(n=10):
    """Generate a random string with numbers, punctuations and characters with `n` length."""

    allowed_characters = string.ascii_letters + string.digits + r"""!#$()*+-:;<=>@[]^_{}"""
    return "".join(secrets.choice(allowed_characters) for _ in range(n))


def random_letters(n=10):
    """Generate a random letters characters with `n` length."""

    allowed_characters = string.ascii_letters
    return "".join(secrets.choice(allowed_characters) for _ in range(n))


def make_http_request(url: str, method="GET", headers={}, data={}, params={}, auth=None, files=None, **kwargs):  # noqa
    """
    Function that makes a third party http request to any given url based on the passed params.
    This is similar to triggerSimpleAjax/Axios function. This is defined here just to make things DRY.
    """

    response = request(
        method=method,
        url=url,
        headers=headers,
        data=stringify(data) if data else data,
        files=files,
        params=params,
        auth=auth,
        **kwargs,
    )
    try:
        response_data = response.json()
    except json.decoder.JSONDecodeError:
        response_data = None

    _output = {
        "data": response_data,
        "status_code": response.status_code,
        "reason": None if response_data else response.text,  # fallback for the data
    }

    # logging action
    log = {
        "request_data": data,
        "params": params,
        "headers": headers,
        "method": method,
        "response_data": _output,
    }
    # log_outbound_message(stringify(log), url, "make_http_request")

    if settings.LOG_DEBUG:
        logger.debug(f"make_http_request: {log}")

    return _output


def stringify(data, fallback=None):  # noqa
    """Stringify a given data."""

    try:
        return json.dumps(data)
    except:  # noqa
        return fallback


def convert_utc_to_local_timezone(
    input_datetime: datetime.date | datetime.datetime,
    inbound_request,  # noqa
):
    """
    Given a UTC datetime or date object, this will convert it to the
    user's local timezone based on the request.
    """

    from_zone = tz.gettz(settings.TIME_ZONE)

    # TODO: from `inbound_request`
    to_zone = tz.gettz("Asia/Kolkata")

    input_datetime = input_datetime.replace(tzinfo=from_zone)

    return input_datetime.astimezone(to_zone)


def is_any_or_list1_in_list2(list1: list, list2: list):
    """Given two lists, this will check if any element of list1 is in list2."""

    return any(v in list2 for v in list1)


def get_first_of(*args):
    """For _ in args, returns the first value whose value is valid."""

    for _ in args:
        if _:
            return _

    return None


def get_file_field_url(instance, field="image"):
    """Given any instance and a linked File, returns the url."""

    if getattr(instance, field, None):
        return getattr(instance, field).file.url

    return None


def get_image_field_url(instance, field="image"):
    """Given any instance and an Image field, returns the url."""

    return getattr(instance, field).file_url if getattr(instance, field) else None


def pause_thread(seconds):
    """Pause the tread for the given seconds."""

    time.sleep(seconds)


def unpack_dj_choices(choices):
    """Return value and corresponding label for that choice."""

    return [{"id": key, "name": str(value)} for key, value in choices]


def file_upload_path(instance, filename):
    """Returns file upload path. Includes db name for folder level isolation."""

    db_name = get_current_db_name()
    return f"files/{db_name}/{instance.__class__.__name__}/{filename}".lower()


def custom_capitalize(s):
    """Split and convert values to capitalize case and create the dictionary"""

    return " ".join(word.capitalize() for word in s.split("_"))


def get_user_session_agent(request) -> str:
    """
    For a given request, returns the savable user agent string. This is used while creating
    the Session object. This uses, django-user-agent for getting the agent. If in case the
    library fails, this uses the default request.HTTP_USER_AGENT.

    Format:
        browser(version) - device - os(version)
    """

    user_agent = request.user_agent

    if user_agent.browser.family in ["Other"]:
        # user logged in using postman or some other thing like that
        user_session_agent = request.headers["user-agent"]
    else:
        user_session_agent = (
            f"{user_agent.browser.family}({user_agent.browser.version_string}) - "
            f"{user_agent.device.family} - {user_agent.os.family}({user_agent.os.version_string})"
        )

    return user_session_agent


def get_sorting_meta(sorting_options: dict):
    """Return value and corresponding label for sorting the list."""

    return [{"id": key, "name": value} for key, value in sorting_options.items()]


def convert_date_format(date_str):
    """Convert a date string in the format 'dd/mm/yyyy' to a datetime object."""

    return dt.strptime(date_str, "%d/%m/%Y") if date_str else None


def get_tenant_website_url(db_name):
    """Return the tenant's website URL."""

    from apps.tenant_service.models import DatabaseRouter

    previous_db = get_current_db_name()
    set_db_for_router()
    url = f"https://{settings.SITE_ADDRESS}"
    if db_name and db_name != settings.DATABASES[DEFAULT_DB_ALIAS]["NAME"]:
        tenant = DatabaseRouter.objects.using(DEFAULT_DB_ALIAS).filter(database_name=db_name).first().tenant
        if domain := tenant.related_tenant_domains.active().first():
            domain_name = domain.name
            url = f"https://{domain_name}.{settings.SITE_ADDRESS}"
    set_db_for_router(previous_db)
    return url


def process_request_headers(request):
    """Returns the issuer & issuer_url based on the request headers."""

    headers = request.get("headers")
    tenant_id, kc_token = headers.get("Tenant-Id", None), headers.get("Kc-Token", None)
    sso_token = headers.get("Sso-Token", None)
    idp_token = headers.get("Idp-Token", None)

    tenant_detail = get_current_tenant_details()

    if idp_token:
        headers = {"Token": idp_token, "Issuer": "IDP", "Issuer-Url": IDP_CONFIG["host"]}
    elif tenant_id and sso_token:
        headers = {
            "Token": sso_token,
            "Issuer": "SSO",
            "Issuer-Url": tenant_detail["issuer_url"],
        }
    elif tenant_id and kc_token:
        headers = {
            "Token": kc_token,
            "Issuer": "KC",
            "Issuer-Url": tenant_detail["issuer_url"],
        }
    else:
        headers = {}
    return headers


class GeneratorWithLen:
    """Generator that includes len and count for given queryset"""

    def __init__(self, generator, length):
        self.generator = generator
        self.length = length

    def __len__(self):
        return self.length

    def __iter__(self):
        return self.generator

    def __getitem__(self, item):
        return self.generator.__getitem__(item)

    def next(self):
        return next(self.generator)

    def count(self):
        return self.__len__()


def batch(queryset, batch_size=1024):
    """
    returns a generator that does not cache results on the QuerySet
    Aimed to use with expected HUGE/ENORMOUS data sets, no caching, no memory used more than batch_size

    :param queryset: Queryset to be chunked based on batch_size.
    :param batch_size: Size for the maximum chunk of data in memory
    :return: generator
    """

    total = queryset.count()

    def batch_qs(_qs, _batch_size=batch_size):
        """Returns a (start, end, total, queryset) tuple for each batch in the given queryset."""

        for start in range(0, total, _batch_size):
            end = min(start + _batch_size, total)
            yield start, end, total, _qs[start:end]

    def generate_items():
        """Yields the batched qs."""

        queryset.order_by("id")  # Clearing... ordering by id if PK autoincremental
        for start, end, total, qs in batch_qs(queryset):
            yield from qs

    return GeneratorWithLen(generate_items(), total)
