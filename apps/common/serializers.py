from rest_framework import serializers
from rest_framework.fields import SkipField
from rest_framework.serializers import ModelSerializer, Serializer

from apps.common import model_fields
from apps.common.config import CUSTOM_ERRORS_MESSAGES
from apps.common.helpers import get_display_name_for_slug, get_first_of, unpack_dj_choices
from apps.common.model_fields import AppFileField, AppImageField
from apps.common.models import BaseUploadModel


class CustomErrorMessagesMixin:
    """
    Overrides the constructor of the serializer to add meaningful error
    messages to the serializer output. Also used to hide security
    related messages to the user.
    """

    def get_display(self, field_name):
        return field_name.replace("_", " ")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # adding custom error messages
        for field_name, field in getattr(self, "fields", {}).items():
            if field.__class__.__name__ == "ManyRelatedField":
                # many-to-many | uses foreign key field for children
                field.error_messages.update(CUSTOM_ERRORS_MESSAGES["ManyRelatedField"])
                field.child_relation.error_messages.update(CUSTOM_ERRORS_MESSAGES["PrimaryKeyRelatedField"])
            elif field.__class__.__name__ == "PrimaryKeyRelatedField":
                # foreign-key
                field.error_messages.update(CUSTOM_ERRORS_MESSAGES["PrimaryKeyRelatedField"])
            else:
                # other input-fields
                field.error_messages.update(
                    {
                        "blank": f"Please enter your {self.get_display(field_name)}",
                        "null": f"Please enter your {self.get_display(field_name)}",
                    }
                )


class AppSerializer(CustomErrorMessagesMixin, Serializer):
    """
    The app's version for the Serializer class. Just to implement common and
    other verifications and schema. Used only for light weight stuff.
    """

    def get_initial_data(self, key, expected_type):
        """
        Central function to get the initial data without breaking. We might
        expect a string, but user gave None. The given expected_type
        is what the type of data the caller is expecting.
        """

        _data = self.initial_data.get(key)

        if type(_data) != expected_type:
            raise SkipField()

        return _data

    def get_user(self):
        """Return the user from the request."""

        return self.get_request().user

    def get_request(self):
        """Returns the request."""

        return self.context["request"]


class AppModelSerializer(AppSerializer, ModelSerializer):
    """
    Applications version of the ModelSerializer. There are separate serializers
    defined for handling the read and write operations separately.

    Note:
        Never mix the `read` and `write` serializers, handle them separate.
    """

    class Meta:
        pass

    def serialize_dj_choices(self, choices: dict):
        """
        Given a list of choices like:
            {'open': <Choice[1]:Open>, 'in_progress': <Choice[2]:In Progress>, ...}

        This will return the following:
            [{'id': 'open', 'identity': 'Open'}, ...]

        This will be convenient for the front end to integrate. Also
        this is considered as a standard.
        """

        return unpack_dj_choices(choices)

    def serialize_for_meta(self, queryset, fields=None):
        """Central serializer for the `get_meta`. Just a dry function."""

        if not fields:
            fields = ["id"]

        return simple_serialize_queryset(fields=fields, queryset=queryset)


class AppWriteOnlyModelSerializer(AppModelSerializer):
    """
    Write only version of the `AppModelSerializer`. Does not support read
    operations and to_representations. Validations are implemented here.

    Note:
        Never mix the `read` and `write` serializers, handle them separate.
    """

    def create(self, validated_data):
        """Overridden to set the `created_by` field."""

        instance = super().create(validated_data=validated_data)

        # setting the anonymous fields
        if hasattr(instance, "created_by") and not instance.created_by:
            user = self.get_user()

            instance.created_by = user if user and user.is_authenticated else None
            instance.save()

        return instance

    def update(self, instance, validated_data):
        """Overridden to set the `modified_by` field."""

        instance = super().update(instance, validated_data)

        # setting the anonymous fields
        if hasattr(instance, "modified_by"):
            user = self.get_user()

            instance.modified_by = user if user and user.is_authenticated else None
            instance.save()

        return instance

    def get_validated_data(self, key=None):
        """Central function to return the validated data."""

        return self.validated_data[key] if key else self.validated_data

    def __init__(self, *args, **kwargs):
        # all fields are required
        for field in self.Meta.fields:
            self.Meta.extra_kwargs.setdefault(field, {})
            self.Meta.extra_kwargs[field]["required"] = True

        super().__init__(*args, **kwargs)

    class Meta(AppModelSerializer.Meta):
        model = None
        fields = []
        extra_kwargs = {}

    def to_internal_value(self, data):
        """Overridden to pre-process inbound data."""

        data = super().to_internal_value(data=data)

        # blank values are not allowed in our application | convert to null
        for k, v in data.items():
            if not v and v not in [False, 0, []]:
                data[k] = None

        return data

    def to_representation(self, instance):
        """Always show the updated data from instance back to the front-end."""

        return self.get_meta_initial()

    def serialize_choices(self, choices: list):
        """
        Given a list of choices like:
            ['active', ...]

        This will return the following:
            [{'id': 'active', 'identity': 'Active'}, ...]

        This will be convenient for the front end to integrate. Also
        this is considered as a standard.
        """

        from apps.common.helpers import get_display_name_for_slug

        return [{"id": _, "identity": get_display_name_for_slug(_)} for _ in choices]

    def get_dynamic_render_config(self):
        """
        Returns a config that can be used by the front-end to dynamically
        render and handle the form fields. This improves delivery speed.
        """

        from django.db import models

        from apps.common.models import BaseUploadModel

        model = self.Meta.model
        render_config = []

        for _ in self.get_fields():
            model_field = model.get_model_field(_, fallback=None)

            field_type = "UNKNOWN_CONTACT_DEVELOPER"
            other_config = {}

            if model_field:
                # type
                try:
                    if isinstance(model_field, models.ForeignKey) and issubclass(
                        model_field.related_model, BaseUploadModel
                    ):
                        if "image" in _:
                            field_type = "ImageUpload"
                        else:
                            field_type = "FileUpload"
                    elif isinstance(model_field, models.CharField) and model_field.choices:
                        field_type = "ChoiceField"
                    else:
                        field_type = model_field.__class__.__name__

                except Exception as e:
                    print(e)  # noqa

                # other render config
                try:
                    other_config["label"] = get_display_name_for_slug(get_first_of(model_field.verbose_name, _))
                    other_config["help_text"] = get_first_of(model_field.help_text)
                    other_config["allow_null"] = model_field.null
                except Exception as e:
                    print(e)  # noqa

            render_config.append(
                {
                    "key": _,
                    "type": field_type,
                    "other_config": other_config,
                }
            )

        return render_config

    def get_meta(self) -> dict:
        """
        Returns the meta details for `get_meta_for_create` & `get_meta_for_update`.
        This is just a centralized function.
        """

        return {}

    def get_meta_for_create(self):
        """
        Returns the necessary meta details for front-end. Overridden
        on the child classes. Called from view.
        """

        return {
            "meta": self.get_meta(),
            "initial": {},
            "render_config": self.get_dynamic_render_config(),
        }

    def get_meta_for_update(self):
        """
        Returns the necessary meta details for front-end. Overridden
        on the child classes. Called from view.
        """

        return {
            "meta": self.get_meta(),
            "initial": self.get_meta_initial(),
            "render_config": self.get_dynamic_render_config(),
        }

    def get_meta_initial(self):
        """
        Returns the `initial` data for `self.get_meta_for_update`. This is
        used by the front-end for setting initial values.
        """

        instance = self.instance
        initial = {}
        for field_name in ["id", *self.fields.keys()]:
            if field_name == "password":
                initial[field_name] = None
            else:
                initial[field_name] = getattr(instance, field_name, None)

        # simplify for FE
        for k, v in initial.items():
            # foreignkey
            if hasattr(initial[k], "pk"):
                initial[k] = v.pk

            # not a model field
            if not instance.__class__.get_model_field(k, None):
                continue

            field = self.Meta.model.get_model_field(k)
            related_model = field.related_model

            field_instance = getattr(self.instance, k)

            # file url for fk instance
            if related_model and issubclass(related_model, BaseUploadModel) and getattr(self.instance, k):
                file_model_fields = related_model._meta.fields
                for file_model_field in file_model_fields:
                    if related_model._meta.get_field(file_model_field.name).__class__ in [AppImageField, AppFileField]:
                        initial[k] = {
                            "id": field_instance.id,
                            file_model_field.name: getattr(field_instance, file_model_field.name).url,
                        }

            # file or image
            if instance.__class__.get_model_field(k).__class__ in [AppImageField, AppFileField]:
                initial[k] = getattr(instance, k).url if getattr(instance, k) else None

            # many-to-many
            if instance.__class__.get_model_field(k).many_to_many:
                initial[k] = getattr(instance, k).values_list("pk", flat=True)

            if instance.__class__.get_model_field(k).__class__ == model_fields.AppPhoneNumberField:
                initial[k] = getattr(instance, k).raw_input if getattr(instance, k) else None

        return initial


class AppCreateModelSerializer(AppWriteOnlyModelSerializer):
    """
    Applications version of the CreateModelSerializer which supports only model creation.
    """

    class Meta(AppWriteOnlyModelSerializer.Meta):
        pass

    def update(self, instance, validated_data):
        """This serializer is only for creation."""

        raise NotImplementedError


class AppUpdateModelSerializer(AppWriteOnlyModelSerializer):
    """
    Applications version of the UpdateModelSerializer which supports only model updates.
    """

    class Meta(AppWriteOnlyModelSerializer.Meta):
        pass

    def create(self, validated_data):
        """This serializer is only for updating."""

        raise NotImplementedError


class AppReadOnlyModelSerializer(AppModelSerializer):
    """
    Read only version of the `AppModelSerializer`. Does not
    support write operations.

    Note:
        Never mix the `read` and `write` serializers, handle them separate.
    """

    class Meta(AppModelSerializer.Meta):
        pass

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


def get_app_read_only_serializer(
    meta_model,
    meta_fields=None,
    init_fields_config=None,
):
    """
    Generates a `AppReadOnlyModelSerializer` on the runtime and returns the same.
    Just used for creating a light weigth stuff.
    """

    if meta_fields is None:
        meta_fields = ["id"]

    if meta_fields != "__all__":
        meta_fields = [*meta_fields] if type(meta_fields) == list else meta_fields

    class _Serializer(AppReadOnlyModelSerializer):
        class Meta(AppReadOnlyModelSerializer.Meta):
            model = meta_model
            fields = (
                meta_fields
                if meta_fields == "__all__"
                else [_ for _ in meta_fields if meta_model.get_model_field(_, None)]
            )

        def __init__(self, *args, **kwargs):
            """
            Overridden to set the custom fields passed on init_fields_config on init.
            Ex: { "logo": ImageDataSerializer() }
            """

            super().__init__(*args, **kwargs)
            if init_fields_config:
                for field, value in init_fields_config.items():
                    self.fields[field] = value

    return _Serializer


def simple_serialize_queryset(fields, queryset):
    """Lightweight queryset serializer. Also implements performance booster."""

    if "id" in fields:
        # performance booster
        return [{**_, "id": str(_["id"])} for _ in queryset.only(*fields).values(*fields)]

    return queryset.only(*fields).values(*fields)


def simple_serialize_instance(instance, keys: list, parent_data: dict = None, display=None) -> dict:
    """
    Given a single object/instance, this will serialize the same.

    Params:
        -> instance         : Instance for serialization
        -> keys             : Serializable fields
        -> parent_data      : Inherited and returned
        -> display          : Display fields for the passed keys
    """

    def _serialize_value(_v):
        """Serialize objects for the front-end."""

        if type(_v) in [int, float]:
            return _v

        return str(_v) if _v else _v

    if not parent_data:
        parent_data = {}

    if not display:
        display = {}

    for key in keys:
        if "." in key:
            # eg: '__class__.__name__'
            _keys, _inter_value = key.split("."), None
            for _k in _keys:
                if not _inter_value:
                    _inter_value = getattr(instance, _k, None)
                else:
                    _inter_value = getattr(_inter_value, _k, None)
            parent_data[key] = _serialize_value(_inter_value)
        else:
            # eg: 'identity'
            parent_data[key] = _serialize_value(getattr(instance, key, None))

    # custom display for fields
    for k, d in display.items():
        parent_data[d] = parent_data.pop(k)

    return parent_data


class FileModelToURLField(serializers.Field):
    """
    Converts a given `FileUpload` instance to url directly.
    Used only as a read only serializer.
    """

    def to_internal_value(self, data):
        """Writeable method, not applicable."""

        raise NotImplementedError

    def to_representation(self, value):
        """Return the url."""

        return value.file_url


class BaseIDNameSerializer(serializers.Serializer):
    """Simple serializer for to retrieve id and name details."""

    id = serializers.IntegerField()
    name = serializers.CharField()


class AppSpecificImageFieldSerializer(serializers.Serializer):
    """Simple serializer for calling the image function."""

    id = serializers.IntegerField()
    image = serializers.CharField(source="get_image")


class BaseIDNameImageSerializer(BaseIDNameSerializer):
    """Simple serializer for to retrieve id, name and image details."""

    image = AppSpecificImageFieldSerializer(read_only=True)
