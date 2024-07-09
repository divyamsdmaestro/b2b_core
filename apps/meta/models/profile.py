from apps.common.models import UniqueNameModel


class IdentificationType(UniqueNameModel):
    """
    Model to store identification type.
    Model Fields -
        PK          - id,
        Fields      - uuid, name
        Datetime    - created_at, modified_at
    App QuerySet Manager Methods -
        get_or_none
    """

    pass


class EducationType(UniqueNameModel):
    """
    Model to store education type.
    Model Fields -
        PK          - id,
        Fields      - uuid, name
        Datetime    - created_at, modified_at
    App QuerySet Manager Methods -
        get_or_none
    """

    pass


class JobDescription(UniqueNameModel):
    """
    Model to store Job Code.
    Model Fields -
        PK          - id,
        Fields      - uuid, name
        Datetime    - created_at, modified_at
    App QuerySet Manager Methods -
        get_or_none
    """

    pass


class JobTitle(UniqueNameModel):
    """
    Model to store Job Title.
    Model Fields -
        PK          - id,
        Fields      - uuid, name
        Datetime    - created_at, modified_at
    App QuerySet Manager Methods -
        get_or_none
    """

    pass


class DepartmentCode(UniqueNameModel):
    """
    Model to store Department Code.
    Model Fields -
        PK          - id,
        Fields      - uuid, name
        Datetime    - created_at, modified_at
    App QuerySet Manager Methods -
        get_or_none
    """

    pass


class DepartmentTitle(UniqueNameModel):
    """
    Model to store Department Title.
    Model Fields -
        PK          - id,
        Fields      - uuid, name
        Datetime    - created_at, modified_at
    App QuerySet Manager Methods -
        get_or_none
    """

    pass


class EmploymentStatus(UniqueNameModel):
    """
    Model to store Employment Status.
    Model Fields -
        PK          - id,
        Fields      - uuid, name, type
        Datetime    - created_at, modified_at
    App QuerySet Manager Methods -
        get_or_none
    """

    pass
