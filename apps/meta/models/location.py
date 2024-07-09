from django.db import models

from apps.common.models import ArchivableModel, NameModel


class Country(NameModel):
    """
    Model to store country details.

    Model Fields -
        PK          - id,
        Fields      - uuid, name
        Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(ArchivableModel.Meta):
        default_related_name = "related_countries"


class State(NameModel):
    """
    Model to store state details.

    Model Fields -
        PK          - id,
        FK          - country
        Fields      - uuid, name
        Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(ArchivableModel.Meta):
        default_related_name = "related_states"

    country = models.ForeignKey(to=Country, on_delete=models.CASCADE)


class City(NameModel):
    """
    Model to store city details.

    Model Fields -
        PK          - id,
        FK          - state
        Fields      - uuid, name
        Datetime    - created_at, modified_at

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(ArchivableModel.Meta):
        default_related_name = "related_cities"

    state = models.ForeignKey(to=State, on_delete=models.CASCADE)
