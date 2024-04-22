# Generated by Django 5.0.4 on 2024-04-22 19:47

import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=999, null=True)),
                ('is_direct_chat', models.BooleanField(blank=True, default=False, null=True)),
                ('custom_json', jsonfield.fields.JSONField(default=dict)),
                ('members_ids', models.CharField(default='[]', editable=False, max_length=999)),
                ('access_key', models.CharField(default='', max_length=999)),
                ('is_authenticated', models.BooleanField(default=True, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='your_chats', to='projects.person')),
                ('project', models.ForeignKey(db_column='public_key', on_delete=django.db.models.deletion.CASCADE, related_name='chats', to='projects.project')),
            ],
            options={
                'ordering': ('project', '-id'),
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_username', models.CharField(blank=True, default=None, max_length=1000, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('custom_json', jsonfield.fields.JSONField(default=dict)),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('chat', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chats.chat')),
                ('sender', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='messages', to='projects.person')),
            ],
            options={
                'ordering': ['chat', '-id'],
            },
        ),
        migrations.CreateModel(
            name='ChatPerson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='people', to='chats.chat')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats', to='projects.person')),
                ('last_read', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_reads', to='chats.message')),
            ],
            options={
                'ordering': ['chat', 'person'],
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, max_length=5000, null=True, upload_to='attachments')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='chats.chat')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='chats.message')),
            ],
            options={
                'ordering': ['chat', '-created'],
            },
        ),
        migrations.AddIndex(
            model_name='chat',
            index=models.Index(fields=['project', '-id'], name='chats_chat_public__1b5c82_idx'),
        ),
        migrations.AddIndex(
            model_name='chat',
            index=models.Index(fields=['project', 'members_ids'], name='chats_chat_public__2cff09_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='chat',
            unique_together={('project', 'id')},
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['chat', '-id'], name='chats_messa_chat_id_68f403_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='message',
            unique_together={('chat', 'id')},
        ),
        migrations.AddIndex(
            model_name='chatperson',
            index=models.Index(fields=['chat', 'person'], name='chats_chatp_chat_id_c48c01_idx'),
        ),
        migrations.AddIndex(
            model_name='chatperson',
            index=models.Index(fields=['person', '-chat_updated'], name='chats_chatp_person__1ff51d_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='chatperson',
            unique_together={('chat', 'person')},
        ),
    ]
