import logging

from celery import Task
from django.conf import settings
from kombu.exceptions import OperationalError

from apps.common.helpers import create_log
from apps.tenant_service.middlewares import set_db_for_router


class BaseAppTask(Task):
    """
    Base celery task class for the entire application. This is inherited by the other
    defined tasks. We use class based tasks to take advantage for OOPS concepts.
    """

    name = None  # for identifying the task
    perform_run_task = True  # to switch/toggle run tasks | send_email etc etc
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        """Overridden to set the name dynamically on runtime."""

        if not self.name:
            self.name = f"{self.__module__}.{self.__class__.__name__}"

        super().__init__(*args, **kwargs)

    def switch_db(self, db_name=None):
        """Function to switch the database."""

        from apps.tenant_service.models import DatabaseRouter

        set_db_for_router()
        if db_name:
            self.logger.info(f"Switching database to {db_name}")
            if router := DatabaseRouter.objects.get_or_none(database_name=db_name):
                router.add_db_connection()
            return set_db_for_router(db_name)
        return True

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def run_task(self, **kwargs):
        """
        The main entrypoint for running any app defined task.
        Use case:
            1. To run the task even if redis/celery is not running.
            2. When not available, this runs as a sync task itself.
        """

        if self.perform_run_task:
            if settings.APP_SWITCHES["CELERY_WORKER_DEBUG_MODE"]:
                # use django thread | local debugging | breakpoints might be used
                self.run(**kwargs)
            else:
                try:
                    # use celery if available
                    self.delay(**kwargs)
                except OperationalError:
                    # use django thread
                    self.run(**kwargs)

        self.post_run_task(**kwargs)

    def post_run_task(self, **kwargs):
        """
        Called at the end of/after self.run_task is executed.
        Used for console logging.
        """

        pass


class BaseOutboundAppTask(BaseAppTask):
    """
    The base class for any outbound tasks like sending emails and sms etc.
    Made common to add logging support and stuff.
    """

    def run(self, *args, **kwargs):
        raise NotImplementedError

    outbound_log_category = None

    def __init__(self, *args, **kwargs):
        assert self.outbound_log_category, f"self.outbound_log_category must be provided for {self.__class__}."
        super().__init__(*args, **kwargs)

    def post_run_task(self, **kwargs):
        """Overridden to create the log object."""

        super().post_run_task(**kwargs)
        create_log(category=self.outbound_log_category, data=kwargs)
