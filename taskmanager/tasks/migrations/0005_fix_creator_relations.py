# tasks/migrations/0005_fix_all_user_relations.py
from django.db import migrations, models
from django.db.migrations.operations.special import RunSQL, RunPython
from django.conf import settings


def clean_invalid_references(apps, schema_editor):
    """Clean up invalid user references in both models"""
    Sprint = apps.get_model("tasks", "Sprint")
    Epic = apps.get_model("tasks", "Epic")
    TaskManagerUser = apps.get_model("accounts", "TaskManagerUser")

    valid_user_ids = set(TaskManagerUser.objects.values_list("id", flat=True))

    # Clean Sprint creators
    for sprint in Sprint.objects.exclude(creator__isnull=True):
        if sprint.creator_id not in valid_user_ids:
            sprint.creator = None
            sprint.save()

    # Clean Epic creators
    for epic in Epic.objects.exclude(creator__isnull=True):
        if epic.creator_id not in valid_user_ids:
            epic.creator = None
            epic.save()


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0004_force_fk_to_custom_user"),
        ("accounts", "0004_authtoken"),
    ]

    operations = [
        # ===== EPIC MODEL =====
        # 1. Make Epic.creator nullable
        migrations.AlterField(
            model_name="epic",
            name="creator",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                on_delete=models.SET_NULL,
                null=True,
                blank=True,
                db_column="creator_id",
            ),
        ),
        # 2. Make Sprint.creator nullable
        migrations.AlterField(
            model_name="sprint",
            name="creator",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                on_delete=models.SET_NULL,
                null=True,
                blank=True,
                db_column="creator_id",
            ),
        ),
        # 3. Clean up invalid references
        RunPython(
            code=clean_invalid_references,
            reverse_code=lambda apps, schema_editor: None,
        ),
        # ===== CONSTRAINT UPDATES =====
        # 4. Remove old constraints
        RunSQL(
            sql="""
            ALTER TABLE tasks_epic 
            DROP CONSTRAINT IF EXISTS tasks_epic_creator_id_12a9b5cf_fk_auth_user_id;
            
            ALTER TABLE tasks_sprint 
            DROP CONSTRAINT IF EXISTS tasks_sprint_creator_id_392a36d7_fk_auth_user_id;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # 5. Add new constraints
        RunSQL(
            sql="""
            ALTER TABLE tasks_epic 
            ADD CONSTRAINT tasks_epic_creator_fk 
            FOREIGN KEY (creator_id) REFERENCES accounts_taskmanageruser(id)
            DEFERRABLE INITIALLY DEFERRED;
            
            ALTER TABLE tasks_sprint 
            ADD CONSTRAINT tasks_sprint_creator_fk 
            FOREIGN KEY (creator_id) REFERENCES accounts_taskmanageruser(id)
            DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
            ALTER TABLE tasks_epic 
            ADD CONSTRAINT tasks_epic_creator_id_12a9b5cf_fk_auth_user_id 
            FOREIGN KEY (creator_id) REFERENCES auth_user(id)
            DEFERRABLE INITIALLY DEFERRED;
            
            ALTER TABLE tasks_sprint 
            ADD CONSTRAINT tasks_sprint_creator_id_392a36d7_fk_auth_user_id 
            FOREIGN KEY (creator_id) REFERENCES auth_user(id)
            DEFERRABLE INITIALLY DEFERRED;
            """,
        ),
    ]
