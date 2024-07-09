import threading
from copy import copy

from django.conf import settings
from django.db import DEFAULT_DB_ALIAS

THREAD_LOCAL = threading.local()


def get_current_tenant_idp_id():
    """
    Returns the current tenant idp_id involved from the thread.
    The `Tenant` is from the default database.
    """

    from apps.tenant_service.models import DatabaseRouter

    db = get_current_db_name()
    if not db or db == settings.DATABASES[DEFAULT_DB_ALIAS]["NAME"]:
        return settings.IDP_B2B_TENANT_ID

    tenant_idp_id_qs = (
        DatabaseRouter.objects.using(DEFAULT_DB_ALIAS)
        .filter(database_name=get_current_db_name())
        .values_list("tenant__idp_id", flat=True)
    )

    return tenant_idp_id_qs[0]


def get_current_tenant_mml_id():
    """
    Returns the current tenant mml_id involved from the thread.
    The `Tenant` is from the default database.
    """

    from apps.tenant.models import Tenant
    from apps.tenant_service.models import DatabaseRouter

    db = get_current_db_name()
    if not db or db == settings.DATABASES[DEFAULT_DB_ALIAS]["NAME"]:
        return Tenant.objects.get(tenancy_name=settings.APP_DEFAULT_TENANT_NAME).mml_id

    tenant_mml_id_qs = (
        DatabaseRouter.objects.using(DEFAULT_DB_ALIAS)
        .filter(database_name=get_current_db_name())
        .values_list("tenant__mml_id", flat=True)
    )

    return tenant_mml_id_qs[0]


def get_current_tenant_name():
    """
    Returns the current tenancy_name involved from the thread.
    The `Tenant` is from the default database.
    """

    from apps.tenant_service.models import DatabaseRouter

    db = get_current_db_name()
    if not db or db == settings.DATABASES[DEFAULT_DB_ALIAS]["NAME"]:
        return settings.APP_DEFAULT_TENANT_NAME

    tenancy_name_qs = (
        DatabaseRouter.objects.using(DEFAULT_DB_ALIAS)
        .filter(database_name=get_current_db_name())
        .values_list("tenant__tenancy_name", flat=True)
    )
    return list(tenancy_name_qs)[0]


def get_current_tenant_details():
    """
    Returns the current tenancy details involved from the thread. Use this function to get any information
    related to the current tenant. Add or remove fields as per necessary.
    The `Tenant` is from the default database.
    """

    from apps.tenant.models import Tenant
    from apps.tenant_service.models import DatabaseRouter

    db = get_current_db_name()
    if not db or db == settings.DATABASES[DEFAULT_DB_ALIAS]["NAME"]:
        tenant = Tenant.objects.get(idp_id=settings.IDP_B2B_TENANT_ID)
    else:
        set_db_for_router()
        tenant = DatabaseRouter.objects.using(DEFAULT_DB_ALIAS).filter(database_name=db).first().tenant
    tenant_details = copy(tenant.tenant_details)
    set_db_for_router(db)
    return tenant_details


def get_current_sender_email():
    """
    Returns the current sender email involved from the thread.
    The `Tenant` is from the default database.
    """

    tenant_config = get_current_tenant_details()
    if tenant_config["sender_email"]:
        return f"'{tenant_config['name'].capitalize()}' <{tenant_config['sender_email']}>"
    return settings.DEFAULT_FROM_EMAIL


def get_current_db_name():
    """Gets which db for the user, from the thread."""

    return getattr(THREAD_LOCAL, "use_db", None)


def set_db_for_router(db=None):
    """Sets which db for user, to the thread."""

    # pre-processing | cookie convention
    if not db:
        db = ""

    setattr(THREAD_LOCAL, "use_db", db)  # noqa
