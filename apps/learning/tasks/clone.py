import json

from apps.common.tasks import BaseAppTask
from apps.my_learning.config import AssignmentLearningTypeChoices


class LearningCloneTask(BaseAppTask):
    """Task to clone the various learning instance."""

    request_headers = None

    @staticmethod
    def get_common_learning_data(data):
        """Function to return the common learning data."""

        from apps.learning.models import Category
        from apps.meta.models import Language

        category_name = data["category"]["name"]
        category, _ = Category.objects.get_or_create(name__iexact=category_name, defaults={"name": category_name})
        if data.get("language"):
            language, _ = Language.objects.get_or_create(
                name=data["language"]["name"],
            )
            language_id = language.id
        else:
            language_id = None
        return {
            "name": data["name"].strip(),
            "description": data["description"],
            "category": category,
            "start_date": data["start_date"],
            "end_date": data["end_date"],
            "language_id": language_id,
            "highlight": json.dumps(data["highlight"]),
            "prerequisite": data["prerequisite"],
            "proficiency": data["proficiency"],
            "rating": data["rating"],
            "learning_points": data["learning_points"],
            "duration": data["duration"],
            "is_feedback_enabled": data["is_feedback_enabled"],
            "is_feedback_mandatory": data["is_feedback_mandatory"],
            "is_rating_enabled": data["is_rating_enabled"],
            "is_dependencies_sequential": data["is_dependencies_sequential"],
            "is_popular": data["is_popular"],
            "is_trending": data["is_trending"],
            "is_recommended": data["is_recommended"],
            "is_technical_support_enabled": data["is_technical_support_enabled"],
            "is_assign_expert": data["is_assign_expert"],
            "is_help_section_enabled": data["is_help_section_enabled"],
            "is_active": True,
        }

    def get_lp_data(self, data):
        """Function to return the learning path data."""

        from apps.learning.models import LearningPathImageModel

        if data.get("image"):
            image = LearningPathImageModel.objects.create(image=data["image"]["image"])
            image_id = image.id
        else:
            image_id = None
        lp_data = self.get_common_learning_data(data)
        lp_data.update(
            {
                "image_id": image_id,
                "learning_type": data["learning_type"],
                "no_of_courses": data["no_of_courses"],
            }
        )
        return lp_data

    def get_course_data(self, data):
        """Function to return the course data."""

        from apps.learning.models import CourseImageModel

        if data.get("image"):
            image = CourseImageModel.objects.create(image=data["image"]["image"])
            image_id = image.id
        else:
            image_id = None
        course_data = self.get_common_learning_data(data)
        course_data.update(
            {
                "image_id": image_id,
                "total_modules": data["total_modules"],
                "total_sub_modules": data["total_sub_modules"],
            }
        )
        return course_data

    @staticmethod
    def get_module_data(data):
        """Function to return the module data."""

        return {
            "name": data["name"],
            "description": data["description"],
            "start_date": data["start_date"],
            "end_date": data["end_date"],
            "is_mandatory": data["is_mandatory"],
            "sequence": data["sequence"],
            "duration": data["duration"],
        }

    @staticmethod
    def get_sub_module_data(data):
        """Function to return the sub module data."""

        return {
            "name": data["name"],
            "description": data["description"],
            "sequence": data["sequence"],
            "duration": data["duration"],
            "type": data["type"]["id"],
            "custom_url": data["custom_url"],
            "file_url": data["file_url"],
            "evaluation_type": data["evaluation_type"],
        }

    @staticmethod
    def set_skill_role_hashtag(instance, skills, roles, category, hashtags):
        """Function to get or create skills and roles."""

        from apps.learning.models import CategoryRole, CategorySkill
        from apps.meta.models import Hashtag

        skill_objs, role_objs = [], []
        for skill in skills:
            skill, _ = CategorySkill.objects.get_or_create(name=skill.strip())
            skill.category.add(category)
            skill_objs.append(skill)
        for role in roles:
            role, _ = CategoryRole.objects.get_or_create(name=role.strip())
            role.category.add(category)
            role_objs.append(role)
        instance.skill.set(skill_objs)
        instance.role.set(role_objs)
        hashtag_objs = [Hashtag.objects.get_or_create(name=hashtag)[0] for hashtag in hashtags]
        instance.hashtag.set(hashtag_objs)
        return True

    def clone_course(self, learning_id, is_ccms_obj, **kwargs):
        """Function to clone course information."""

        from apps.learning.helpers import get_ccms_retrieve_details
        from apps.learning.models import Course
        from apps.my_learning.helpers import get_ccms_list_details

        self.logger.info("Cloning Course is in progress...")
        if is_ccms_obj:
            course_success, course_details = get_ccms_retrieve_details(
                learning_type="course",
                instance_id=learning_id,
                request=self.request_headers,
            )
            module_success, module_details = get_ccms_list_details(
                learning_type="course_module",
                params={"course": learning_id},
                request=self.request_headers,
            )
            sub_module_success, sub_module_details = get_ccms_list_details(
                learning_type="course_submodule",
                params={"module__course__uuid": learning_id},
                request=self.request_headers,
            )
            if not course_success or not module_success or not sub_module_success:
                return False
            course_data = self.get_course_data(course_details["data"])
            cloned_course = Course.objects.create(**course_data)
            self.set_skill_role_hashtag(
                cloned_course,
                course_details["data"]["skill"],
                course_details["data"]["role"],
                course_data["category"],
                course_details["data"]["hashtag"],
            )
            cloned_course.skill.all().skill_course_count_update()
            cloned_course.role.all().role_course_count_update()
            cloned_course.category.category_course_count_update()
            module_objs = {}
            for data in module_details["data"]["results"]:
                module_data = self.get_module_data(data)
                module_objs[data["id"]] = cloned_course.related_course_modules.create(**module_data)
            for data in sub_module_details["data"]["results"]:
                sub_mod_data = self.get_sub_module_data(data)
                module_objs[data["module"]].related_course_sub_modules.create(**sub_mod_data)
            cloned_course.register_course_in_chat_service(request_headers=self.request_headers)
        else:
            cloned_course = Course.objects.get(id=learning_id)
            cloned_course.clone(request_headers=self.request_headers)
        self.logger.info(f"Course cloned successfully - {cloned_course.name}")
        return cloned_course.id

    def clone_learning_path(self, learning_id, is_ccms_obj, **kwargs):
        """Function to clone learning path."""

        from apps.learning.helpers import get_ccms_retrieve_details
        from apps.learning.models import LearningPath
        from apps.my_learning.helpers import get_ccms_list_details

        self.logger.info("Cloning Learning Path is in progress...")
        if is_ccms_obj:
            lp_success, lp_details = get_ccms_retrieve_details(
                learning_type="learning_path",
                instance_id=learning_id,
                request=self.request_headers,
            )
            lp_course_success, lp_course_details = get_ccms_list_details(
                learning_type="lp_course",
                request=self.request_headers,
                params={"learning_path__uuid": learning_id},
            )
            if not lp_success or not lp_course_success:
                return False
            lp_data = self.get_lp_data(lp_details["data"])
            cloned_lp = LearningPath.objects.create(**lp_data)
            self.set_skill_role_hashtag(
                cloned_lp,
                lp_details["data"]["skill"],
                lp_details["data"]["role"],
                lp_data["category"],
                lp_details["data"]["hashtag"],
            )
            cloned_lp.skill.all().skill_learning_path_count_update()
            cloned_lp.role.all().role_learning_path_count_update()
            cloned_lp.category.category_learning_path_count_update()
            for lp_course_data in lp_course_details["data"]["results"]:
                cloned_course_id = self.clone_course(lp_course_data["course"]["uuid"], True, **kwargs)
                lp_course = {
                    "course_id": cloned_course_id,
                    "sequence": lp_course_data["sequence"],
                    "course_unlock_date": lp_course_data["course_unlock_date"],
                    "is_mandatory": lp_course_data["is_mandatory"],
                    "is_locked": lp_course_data["is_locked"],
                }
                cloned_lp.related_learning_path_courses.create(**lp_course)
        else:
            cloned_lp = LearningPath.objects.get(id=learning_id)
            cloned_lp.clone()
        self.logger.info(f"Learning Path cloned successfully - {cloned_lp.name}")
        return cloned_lp.id

    def clone_skill_traveller(self, learning_id):
        """Function to clone skill traveller."""

        from apps.learning.models import SkillTraveller

        self.logger.info("Cloning Skill Traveller is in progress...")
        cloned_st = SkillTraveller.objects.get(id=learning_id)
        cloned_st.clone()
        self.logger.info(f"Skill Traveller cloned successfully - {cloned_st.name}")
        return cloned_st.id

    def run(self, learning_type, learning_id, is_ccms_obj, db_name, **kwargs):
        """Run handler."""

        self.switch_db(db_name)
        self.logger.info("Executing LearningCloneTask")
        self.request_headers = kwargs.get("request_headers", None)

        try:
            match learning_type:
                case AssignmentLearningTypeChoices.course:
                    for course_id in learning_id:
                        self.clone_course(course_id, is_ccms_obj, **kwargs)
                case AssignmentLearningTypeChoices.learning_path:
                    for learning_path_id in learning_id:
                        self.clone_learning_path(learning_path_id, is_ccms_obj, **kwargs)
                case AssignmentLearningTypeChoices.skill_traveller:
                    for skill_traveller_id in learning_id:
                        self.clone_skill_traveller(skill_traveller_id)
        except Exception as e:
            self.logger.error(e)
            return False

        return True
