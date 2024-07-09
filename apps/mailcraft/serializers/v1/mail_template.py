from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.mailcraft.config import MAIL_DYNAMIC_FIELDS, MailTypeChoices
from apps.mailcraft.models import MailTemplate


class MailTemplateRetrieveModelSerializer(AppReadOnlyModelSerializer):
    """`MailTemplate` Detail serializer."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = MailTemplate
        fields = [
            "id",
            "uuid",
            "name",
            "type",
            "subject",
            "is_active",
            "created_at",
            "modified_at",
            "content",
        ]


class MailTemplateCUDModelSerializer(AppWriteOnlyModelSerializer):
    """CUD serializer class for `MailTemplate`."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = MailTemplate
        fields = [
            "name",
            "type",
            "subject",
            "is_active",
            "content",
        ]

    def validate(self, attrs):
        """Validate if all the required fields are present based on type."""

        mail_type, is_active, content = attrs["type"], attrs["is_active"], attrs["content"]
        dynamic_variables = MAIL_DYNAMIC_FIELDS[mail_type]["required"]
        for dynamic_variable in dynamic_variables:
            if dynamic_variable not in content:
                message = f"Please include {dynamic_variable} variable in the mail body."
                note = "Note: Variables are case sensitive."
                raise serializers.ValidationError({"content": f"{message} {note}"})

        existing_active_template = MailTemplate.objects.active().filter(type=mail_type)
        if (self.instance and is_active and existing_active_template.exclude(id=self.instance.id).exists()) or (
            not self.instance and is_active and existing_active_template.exists()
        ):
            mail_type_label = MailTypeChoices.get_choice(mail_type).label
            raise serializers.ValidationError(
                {"content": f"There is already an Active Template exists for the Type {mail_type_label}."}
            )
        return attrs

    def get_meta(self) -> dict:
        """Get meta data."""

        return {"type": self.serialize_dj_choices(MailTypeChoices.choices), "dynamic_variables": MAIL_DYNAMIC_FIELDS}
