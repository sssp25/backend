# Generated migration to fix Actor.id field type

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('actor', '0003_alter_actor_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actor',
            name='id',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
