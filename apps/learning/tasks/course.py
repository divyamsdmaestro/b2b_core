import csv
import json
import os

from apps.common.helpers import convert_date_format
from apps.common.tasks import BaseAppTask


class CourseBulkUploadTask(BaseAppTask):
    """Task to bulk upload the courses."""

    @staticmethod
    def read_csv_file(file_path):
        """Read CSV file and return list_of_course_details"""

        with open(file_path, encoding="utf-8", errors="ignore") as file:
            csv_reader = csv.DictReader(file)
            return list(csv_reader)

    @staticmethod
    def get_course_data(course_detail, category):
        """Function to get the course data."""

        from apps.learning.config import ProficiencyChoices
        from apps.learning.models import CourseImageModel
        from apps.meta.config import FacultyTypeChoices
        from apps.meta.models import Faculty, Language

        author = Faculty.objects.filter(name=course_detail["course_author"], type=FacultyTypeChoices.author).first()
        if not author:
            author = Faculty.objects.create(name=course_detail["course_author"], type=FacultyTypeChoices.author)
        language = Language.objects.filter(name=course_detail["course_language"]).first()
        if not language:
            language = Language.objects.create(name=course_detail["course_language"])
        proficiency = course_detail["course_proficiency"].strip().lower()
        if proficiency not in [
            ProficiencyChoices.basic,
            ProficiencyChoices.intermediate,
            ProficiencyChoices.advance,
        ]:
            proficiency = None
        course_image = course_highlight = None
        if course_detail["course_image_url"]:
            course_image = CourseImageModel.objects.filter(image=course_detail["course_image_url"]).first()
            if not course_image:
                course_image = CourseImageModel.objects.create(image=course_detail["course_image_url"])
        if highlight := course_detail["course_highlight"]:
            if highlight.startswith("•"):
                highlight = highlight[2:]
                highlight_list = highlight.strip().split("\n• ")
                course_highlight = json.dumps(highlight_list)
            else:
                course_highlight = highlight
        return {
            "name": course_detail["course_name"].strip(),
            "description": course_detail["course_description"],
            "category": category,
            "code": course_detail["course_code"],
            "image": course_image,
            "start_date": convert_date_format(course_detail["course_start_date"]),
            "end_date": convert_date_format(course_detail["course_end_date"]),
            "author": author,
            "language": language,
            "highlight": course_highlight,
            "prerequisite": course_detail["course_prerequisite"],
            "proficiency": proficiency,
            "rating": course_detail["course_rating"] or 0,
            "learning_points": course_detail["course_learning_points"] or 0,
            "mml_sku_id": course_detail.get("course_mml_sku_id") or None,
            "vm_name": course_detail["course_vm_name"],
            "is_feedback_enabled": course_detail["course_is_feedback_enabled"] or False,
            "is_feedback_mandatory": course_detail["course_is_feedback_mandatory"] or False,
            "is_rating_enabled": course_detail["course_is_rating_enabled"] or False,
            "is_dependencies_sequential": course_detail["course_is_dependencies_sequential"] or False,
            "is_popular": course_detail["course_is_popular"] or False,
            "is_trending": course_detail["course_is_trending"] or False,
            "is_recommended": course_detail["course_is_recommended"] or False,
            "is_certificate_enabled": course_detail["course_is_certificate_enabled"] or False,
            "certificate": course_detail["course_certificate_id"] or None,
            "is_draft": False,
        }

    @staticmethod
    def get_course_module_data(course_detail, course):
        """Function to get the course module data."""

        if not course_detail["course_module_position"]:
            max_position = (
                course.related_course_modules.order_by("-sequence").values_list("sequence", flat=True).first()
            )
            course_detail["course_module_position"] = max_position + 1 if max_position else 1
        return {
            "name": course_detail["course_module_name"].strip(),
            "description": course_detail["course_module_description"],
            "sequence": course_detail["course_module_position"],
            "start_date": convert_date_format(course_detail["course_module_start_date"]),
            "end_date": convert_date_format(course_detail["course_module_end_date"]),
            "is_mandatory": course_detail["course_module_is_mandatory"] or False,
        }

    @staticmethod
    def get_course_sub_module_data(course_detail, course_module):
        """Function to get the course sub module data."""

        from apps.learning.config import SubModuleTypeChoices
        from apps.learning.helpers import convert_hms_to_sec

        if not course_detail["course_sub_module_position"]:
            max_position = (
                course_module.related_course_sub_modules.order_by("-sequence")
                .values_list("sequence", flat=True)
                .first()
            )
            course_detail["course_sub_module_position"] = max_position + 1 if max_position else 1
        return {
            "name": course_detail["course_sub_module_name"].strip(),
            "description": course_detail["course_sub_module_description"],
            "sequence": course_detail["course_sub_module_position"],
            "duration": convert_hms_to_sec(course_detail["course_sub_module_duration"]),
            "type": SubModuleTypeChoices.custom_url,
            "custom_url": course_detail["course_sub_module_url"].strip().replace(" ", "%20")
            if course_detail.get("course_sub_module_url")
            else None,
        }

    @staticmethod
    def get_skill_role_hashtag_objects(skills, roles, category, hashtags):
        """Function to get or create skills, roles and hashtags."""

        from apps.learning.models import CategoryRole, CategorySkill
        from apps.meta.models import Hashtag

        skill_objs, role_objs, hashtag_objs = [], [], []
        for skill in skills.split(","):
            if skill:
                skill_obj = CategorySkill.objects.filter(name=skill.strip()).first()
                if not skill_obj:
                    skill_obj = CategorySkill.objects.create(name=skill.strip())
                skill_obj.category.add(category)
                skill_objs.append(skill_obj)
        for role in roles.split(","):
            if role:
                role_obj = CategoryRole.objects.filter(name=role.strip()).first()
                if not role_obj:
                    role_obj = CategoryRole.objects.create(name=role.strip())
                role_obj.category.add(category)
                role_objs.append(role_obj)
        for hashtag in hashtags.split(","):
            if hashtag:
                hashtag_obj = Hashtag.objects.filter(name=hashtag.strip()).first()
                if not hashtag_obj:
                    hashtag_obj = Hashtag.objects.create(name=hashtag.strip())
                hashtag_objs.append(hashtag_obj)
        return skill_objs, role_objs, hashtag_objs

    @staticmethod
    def process_course_assessment(course_detail, course, course_module=None):
        """Function to update or create course assessment."""

        from apps.learning.config import AssessmentProviderTypeChoices, AssessmentTypeChoices

        course_assessment_data = {
            "type": course_detail["course_assessment_type"].strip().lower(),
            "name": course_detail["course_assessment_name"].strip(),
            "assessment_uuid": course_detail["course_assessment_uuid"].strip(),
            "provider_type": AssessmentProviderTypeChoices.yaksha,  # TODO: Need to remove this hardcoded data
        }
        assessment_instance = None
        if course_assessment_data["type"] == AssessmentTypeChoices.final_assessment:
            assessment_instance = course
        elif course_module and course_assessment_data["type"] == AssessmentTypeChoices.dependent_assessment:
            assessment_instance = course_module
        if assessment_instance:
            assessment_qs = getattr(assessment_instance, "related_course_assessments")
            last_instance = assessment_qs.order_by("-sequence").first()
            course_assessment_data["sequence"] = last_instance.sequence + 1 if last_instance else 1
            assessment_obj = assessment_qs.filter(name=course_assessment_data["name"].strip()).first()
            if not assessment_obj:
                assessment_qs.create(**course_assessment_data)

    @staticmethod
    def process_course_assignment(course_detail, course, course_module=None):
        """Function to create course assignment."""

        from apps.learning.config import CommonLearningAssignmentTypeChoices
        from apps.learning.models import Assignment

        if assignment_instance := Assignment.objects.filter(code=course_detail["course_assignment_code"]).first():
            assignment_data = {
                "type": course_detail["course_assignment_type"].strip().lower(),
            }
            assignment_qs = None
            if course_module and assignment_data["type"] == CommonLearningAssignmentTypeChoices.dependent_assignment:
                assignment_qs = getattr(course_module, "related_course_assignments")
            elif assignment_data["type"] == CommonLearningAssignmentTypeChoices.final_assignment:
                assignment_qs = getattr(course, "related_course_assignments")
            if assignment_qs:
                last_assignment_instance = assignment_qs.order_by("-sequence").first()
                assignment_data["sequence"] = last_assignment_instance.sequence + 1 if last_assignment_instance else 1
                assignment_obj = assignment_qs.filter(assignment=assignment_instance).first()
                if not assignment_obj:
                    assignment_qs.create(assignment=assignment_instance, **assignment_data)

    def run(self, file_path, db_name, **kwargs):
        """Run handler."""

        from apps.learning.models import Category, Course
        from apps.meta.models import FeedbackTemplate

        self.switch_db(db_name)
        self.logger.info("Executing CourseBulkUploadTask.")
        list_of_course_details = self.read_csv_file(file_path)

        for course_detail in list_of_course_details:
            category_name = course_detail.get("course_category")
            if not category_name:
                continue
            try:
                category = Category.objects.filter(name=category_name).first()
                if not category:
                    category = Category.objects.create(name=category_name)
                course_data = self.get_course_data(course_detail, category)
                course, _ = Course.objects.update_or_create(code=course_data["code"], defaults=course_data)
                skill_objs, role_objs, hashtag_objs = self.get_skill_role_hashtag_objects(
                    course_detail["course_skill"],
                    course_detail["course_role"],
                    category,
                    course_detail["course_hashtag"],
                )
                if course_data["is_feedback_enabled"] and course_detail["course_feedback_template"]:
                    feedback_template = FeedbackTemplate.objects.filter(name=course_detail["course_feedback_template"])
                    if feedback_template.exists():
                        course.feedback_template.add(feedback_template.first())
                course.skill.set(skill_objs)
                course.role.set(role_objs)
                course.hashtag.set(hashtag_objs)
                course.role.all().role_course_count_update()
                course.skill.all().skill_course_count_update()
                course.category.category_course_count_update()
                course_module = None
                if course_detail.get("course_module_name"):
                    course_module_data = self.get_course_module_data(course_detail, course)
                    course_module, _ = course.related_course_modules.update_or_create(
                        name__iexact=course_module_data["name"],
                        defaults=course_module_data,
                    )
                    if course_detail.get("course_sub_module_name"):
                        course_sub_module_data = self.get_course_sub_module_data(course_detail, course_module)
                        course_sub_module, _ = course_module.related_course_sub_modules.update_or_create(
                            name__iexact=course_sub_module_data["name"],
                            defaults=course_sub_module_data,
                        )
                        course_sub_module.module.module_duration_update()
                        course_sub_module.module.course.course_duration_count_update()
                if course_detail.get("course_assessment_name"):
                    self.process_course_assessment(course_detail, course, course_module)
                if course_detail.get("course_assignment_code"):
                    self.process_course_assignment(course_detail, course, course_module)
            except Exception as e:
                self.logger.info(f"Error while processing {course_detail['course_name']}: {e}")
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

        return True
