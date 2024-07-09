# import datetime
# import random
#
# from django.conf import settings
# from django.db import models as django_models
# from django_tenants.utils import get_tenant_model, schema_context
# from faker import Faker
#
# from apps.common.management.commands.base import AppBaseCommand
# from apps.course.models.categories import CourseCategory, CourseCategoryImageModel
# from apps.learning.models import Course, CourseImageModel
# from apps.course.models.modules import CourseModule
# from apps.course.models.roles import CourseRole, CourseRoleImageModel
# from apps.course.models.skills import CourseSkill, CourseSkillImageModel
# from apps.course.models.sub_modules import CourseSubModule
# from apps.my_learning.models.tracker.course import (
#     UserCourseModuleTrackingModel,
#     UserCourseSubModuleTrackingModel,
#     UserCourseTrackingModel,
# )
# from apps.tenant_service.models import DatabaseRouter
#
#
# class Command(AppBaseCommand):
#     help = "Initializes the app by running the necessary initial commands."
#
#     # number of fake instances
#     FAKE_INSTANCES_COUNT = 5
#
#     # fake image paths
#     FAKE_IMAGE_PATHS = [
#         "files/vendor/image/data_science.jpg",
#     ]
#
#     FAKE_VIDEO_URL = "https://www.youtube.com/watch?v=tOwjEOt1zYU"
#
#     IMAGE_MODELS_TO_FAKE = [
#         CourseCategoryImageModel,
#         CourseRoleImageModel,
#         CourseSkillImageModel,
#         CourseImageModel,
#     ]
#
#     # other / regular
#     OTHER_MODELS_TO_FAKE = [
#         CourseCategory,
#         CourseRole,
#         CourseSkill,
#         Course,
#         CourseModule,
#         CourseSubModule,
#         UserCourseTrackingModel,
#         UserCourseModuleTrackingModel,
#         UserCourseSubModuleTrackingModel,
#     ]
#
#     def handle(self, *args, **kwargs):  # noqa
#         """Used to load fake data into our application for testing and development."""
#
#         schema_names = get_tenant_model().objects.only("schema_name").values_list("schema_name", flat=True)
#
#         for schema_name in schema_names:
#             if schema_name == "public":
#                 self.print_styled_message("** Skipping the public schema **")
#                 continue
#             with schema_context(schema_name):
#                 self.print_styled_message(f"\n** Loading fake data for {schema_name}. **")
#
#                 faker = Faker()
#
#                 for model in self.IMAGE_MODELS_TO_FAKE:
#                     print(f"Faking: {model}")  # noqa
#
#                     for _ in range(self.FAKE_INSTANCES_COUNT):
#                         path = random.choice(self.FAKE_IMAGE_PATHS)
#                         if model.get_model_field("image"):
#                             instance = model(image=path)
#                             instance.save()
#                         else:
#                             instance = model(file=path)
#                             instance.save()
#
#                 for model in self.OTHER_MODELS_TO_FAKE:
#                     print(f"Faking: {model}")  # noqa
#
#                     for _ in range(self.FAKE_INSTANCES_COUNT):
#                         instance_regular_data = {}
#                         instance_m2m_data = {}
#
#                         for field in model.get_all_model_fields():
#                             field_class = field.__class__
#                             field_name = field.name
#
#                             if field_name in ["id", "uuid", "deleted_by"] or field_class in [
#                                 django_models.fields.reverse_related.ManyToOneRel,
#                                 django_models.fields.reverse_related.ManyToManyRel,
#                             ]:
#                                 pass
#
#                             elif field_class in [
#                                 django_models.CharField,
#                                 django_models.TextField,
#                             ]:
#                                 instance_regular_data[field_name] = faker.name()
#
#                             elif field_class == django_models.ForeignKey:
#                                 instance_regular_data[field_name] = random.choice(field.related_model.objects.all())
#
#                             elif field_class == django_models.BooleanField:
#                                 instance_regular_data[field_name] = random.choice([True, False])
#
#                             elif field_class in [
#                                 django_models.IntegerField,
#                                 django_models.PositiveIntegerField,
#                                 django_models.PositiveBigIntegerField,
#                                 django_models.PositiveSmallIntegerField,
#                                 django_models.FloatField,
#                                 django_models.DecimalField,
#                             ]:
#                                 instance_regular_data[field_name] = random.randint(5, 2000)
#
#                             elif field_class == django_models.fields.related.ManyToManyField:
#                                 instance_m2m_data[field_name] = random.choices(
#                                     field.related_model.objects.all(), k=random.randint(2, 4)
#                                 )
#
#                             elif field_class == django_models.URLField:
#                                 instance_regular_data[field_name] = random.choice([self.FAKE_VIDEO_URL])
#
#                             elif field_class == django_models.DateField:
#                                 instance_regular_data[field_name] = datetime.date.today()
#
#                             else:
#                                 # Something is not handled
#                                 print(f"Field Class {field_class} For {field_name} Not Handled!")  # noqa
#
#                         # regular data
#                         instance = model(**instance_regular_data)
#                         self.print_styled_message(f"\n**{instance} Data loaded. **\n", "SUCCESS")
#                         instance.save()
#
#                         # m2m data
#                         for m2m_key, m2m_data in instance_m2m_data.items():
#                             getattr(instance, m2m_key).set(m2m_data)
#
#                 self.print_styled_message("\n** Data loaded. **\n", "SUCCESS")
#
#         self.print_styled_message("** Loading completed **")
