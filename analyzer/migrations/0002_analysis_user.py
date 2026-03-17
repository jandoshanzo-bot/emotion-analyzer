from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('analyzer', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='analysishistory',
            name='user',
            field=models.ForeignKey(
                related_name='analysis_histories',
                on_delete=django.db.models.deletion.CASCADE,
                null=True,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                verbose_name='Пайдаланушы'
            ),
        ),
    ]
