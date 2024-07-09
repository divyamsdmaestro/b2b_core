from django.core.files.storage import default_storage
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives


def app_send_mail(
    subject,
    message,
    from_email,
    recipient_list,
    fail_silently=False,
    auth_user=None,
    auth_password=None,
    host=None,
    connection=None,
    html_message=None,
    attachments: list[str] = None,
    **kwargs,
):
    """
    The replica of django.core.mail.send_mail(). The default django send_mail
    does not support cc and bcc options, so this is added here. Just a dry
    function that adds cc and bcc options.
    """

    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        host=host,
        fail_silently=fail_silently,
    )
    mail = EmailMultiAlternatives(
        subject,
        message,
        from_email,
        recipient_list,
        connection=connection,
        cc=kwargs.get("cc", None),
        reply_to=kwargs.get("reply_to", None),
    )
    if html_message:
        mail.attach_alternative(html_message, "text/html")

    # attachments consists of list of string with represents the full media path
    if attachments:
        for attachment in attachments:
            if kwargs.get("is_default_storage"):
                file_content = default_storage.open(attachment).read()
            else:
                file_content = open(attachment, "rb").read()
            mail.attach(
                attachment.split("/")[-1],
                file_content,
                "application/octet-stream",
            )

    return mail.send()
