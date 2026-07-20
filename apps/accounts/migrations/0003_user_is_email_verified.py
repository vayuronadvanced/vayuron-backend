# Generated for the password-reset / email-verification feature.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_email_verified',
            field=models.BooleanField(
                default=False,
                help_text='Set once the user clicks the verification link sent to their email.',
            ),
        ),
    ]
