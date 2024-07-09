from django.apps import apps

from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Remove Duplicate records. Just a bugfix for data migration purpose only."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        from apps.tenant_service.middlewares import set_db_for_router

        Category = apps.get_model("learning", "Category")
        CategorySkill = apps.get_model("learning", "CategorySkill")
        Course = apps.get_model("learning", "Course")
        LearningPath = apps.get_model("learning", "LearningPath")
        AdvancedLearningPath = apps.get_model("learning", "AdvancedLearningPath")
        DatabaseRouter = apps.get_model("tenant_service", "DatabaseRouter")
        tenant_db_name = "some name"

        tracker = DatabaseRouter.objects.get(database_name=tenant_db_name)
        self.print_styled_message(f"\n** Removing Duplicates for {tracker.database_name}. **")
        tracker.add_db_connection()
        set_db_for_router(tracker.database_name)

        self.remove_duplicate_skills(Category, CategorySkill, Course, LearningPath, AdvancedLearningPath)
        self.remove_duplicate_categories(Category, CategorySkill, Course, LearningPath, AdvancedLearningPath)

    def remove_duplicate_categories(self, Category, CategorySkill, Course, LearningPath, AdvancedLearningPath):
        """Remove Duplicate for Category Model."""

        categories = Category.objects.all()
        self.print_styled_message(f"\n** Total Count of Categories = {categories.count()}. **")
        if not categories:
            self.print_styled_message("\n** Finished Removing Duplicates. **\n", "SUCCESS")
            return True

        processed_categories = []
        duplicate_categories = []
        for category in categories:
            if category.name in processed_categories:
                duplicate_categories.append(category.id)
                continue
            processed_categories.append(category.name)
            # process skill
            skills = CategorySkill.objects.filter(category__name=category.name)
            for skill in skills:
                skill.category.set([category.id])
            # process course
            Course.objects.filter(category__name=category.name).update(category=category)
            # process learning_path
            LearningPath.objects.filter(category__name=category.name).update(category=category)
            # process course
            AdvancedLearningPath.objects.filter(category__name=category.name).update(category=category)
        Category.objects.filter(id__in=duplicate_categories).hard_delete()
        self.print_styled_message(
            f"\n** Processed Duplicates Count For Category {len(duplicate_categories)}. **\n", "SUCCESS"
        )
        self.print_styled_message("\n** Finished Processed Duplicates For Category. **\n", "SUCCESS")

    def remove_duplicate_skills(self, Category, CategorySkill, Course, LearningPath, AdvancedLearningPath):
        """Remove duplicates for CategorySkill model."""

        self.print_styled_message("\n** Removing Duplicates For Skills. **\n", "SUCCESS")
        processed_skills = []
        duplicate_skills = []
        skills = CategorySkill.objects.all()
        self.print_styled_message(f"\n** Total Count of Skills = {skills.count()}. **")
        if not skills:
            self.print_styled_message("\n** Finished Removing Duplicates No Skills present. **\n", "SUCCESS")
            return True

        for skill in skills:
            if skill.name in processed_skills:
                duplicate_skills.append(skill.id)
                continue
            processed_skills.append(skill.name)
            category = Category.objects.filter(related_category_skills__name=skill.name)
            courses = Course.objects.filter(skill__name=skill.name)
            lps = LearningPath.objects.filter(skill__name=skill.name)
            alps = AdvancedLearningPath.objects.filter(skill__name=skill.name)
            skill.category.set(list(category.values_list("id", flat=True)))
            for course in courses:
                course.skill.set([skill.id])
            for lp in lps:
                lp.skill.set([lp.id])
            for alp in alps:
                alp.skill.set([alp.id])
        CategorySkill.objects.filter(id__in=duplicate_skills).hard_delete()
        self.print_styled_message(
            f"\n** Processed Duplicates Count For Skills = {len(duplicate_skills)}. **\n", "SUCCESS"
        )
        self.print_styled_message("\n** Finished Processed Duplicates For Skills. **\n", "SUCCESS")
