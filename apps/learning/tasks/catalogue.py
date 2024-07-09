from apps.common.tasks import BaseAppTask


class UpdateCatalogueLearningDataTask(BaseAppTask):
    """Task to to update the count of various learning items in the catalogue."""

    def run(self, catalogue_ids: list, db_name, **kwargs):
        """Run handler."""

        from apps.learning.models import Catalogue

        self.switch_db(db_name)
        self.logger.info("Executing UpdateCatalogueLearningDataTask")

        catalogue_instances = Catalogue.objects.filter(id__in=catalogue_ids)
        try:
            for catalogue_instance in catalogue_instances:
                skills = set()
                roles = set()
                categories = set()
                for course in catalogue_instance.course.all():
                    self.update_skill_role_category_sets(course, skills, roles, categories)
                for learning_path in catalogue_instance.learning_path.all():
                    self.update_skill_role_category_sets(learning_path, skills, roles, categories)
                for advanced_learning_path in catalogue_instance.advanced_learning_path.all():
                    self.update_skill_role_category_sets(advanced_learning_path, skills, roles, categories)
                for playground in catalogue_instance.playground.all():
                    self.update_skill_role_category_sets(playground, skills, roles, categories)
                for playground_group in catalogue_instance.playground_group.all():
                    self.update_skill_role_category_sets(playground_group, skills, roles, categories)
                for assignment in catalogue_instance.assignment.all():
                    self.update_skill_role_category_sets(assignment, skills, roles, categories)
                for assignment_group in catalogue_instance.assignment_group.all():
                    self.update_skill_role_category_sets(assignment_group, skills, roles, categories)
                for skill_traveller in catalogue_instance.skill_traveller.all():
                    skills.update(skill_traveller.skill.all())
                    categories.add(skill_traveller.category)
                # Add the gathered unique categories, skills, and roles to the catalogue instance
                catalogue_instance.category.set(categories)
                catalogue_instance.skill.set(skills)
                catalogue_instance.role.set(roles)
                catalogue_instance.update_catalogue_learning_counts()
        except Exception as e:
            self.logger.info(f"Error while executing UpdateCatalogueLearningDataTask: {e}")
        return True

    def update_skill_role_category_sets(self, obj, skills, roles, categories):
        """Function to update the skill category and role sets for the given object."""

        skills.update(obj.skill.all())
        roles.update(obj.role.all())
        categories.add(obj.category)
