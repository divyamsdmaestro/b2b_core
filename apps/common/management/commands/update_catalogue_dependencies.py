from django.apps import apps

from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Update category and skills to catalogue. Just a bugfix for data migration purpose only."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        from apps.tenant_service.middlewares import set_db_for_router

        DatabaseRouter = apps.get_model("tenant_service", "DatabaseRouter")
        Catalogue = apps.get_model("learning", "Catalogue")
        tenant_db_name = "some name"

        tracker = DatabaseRouter.objects.get(database_name=tenant_db_name)
        self.print_styled_message(f"\n** Executing Update Catalogue for {tracker.database_name}. **")
        tracker.add_db_connection()
        set_db_for_router(tracker.database_name)

        catalogue_instances = Catalogue.objects.all()
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
                for skill_traveller in catalogue_instance.skill_traveller.all():
                    skills.update(skill_traveller.skill.all())
                    categories.add(skill_traveller.category)
                # Add the gathered unique categories, skills, and roles to the catalogue instance
                catalogue_instance.category.set(categories)
                catalogue_instance.skill.set(skills)
                catalogue_instance.role.set(roles)
                catalogue_instance.update_catalogue_learning_counts()
            self.print_styled_message("\n** Catalogue's updated successfully. **")
        except Exception as e:
            self.print_styled_message(f"\n** Error while executing UpdateCatalogueLearningDataTask: {e}. **")

    @staticmethod
    def update_skill_role_category_sets(obj, skills, roles, categories):
        """Function to update the skill category and role sets for the given object."""

        skills.update(obj.skill.all())
        roles.update(obj.role.all())
        categories.add(obj.category)
