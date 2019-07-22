# Generated by Django 2.0.4 on 2019-05-17 20:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('position', '0023_positionbidstatistics_has_handshake_accepted'),
        ('bidding', '0011_auto_20190410_1921'),
    ]

    operations = [
        migrations.CreateModel(
            name='CyclePosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_string_representation', models.TextField(blank=True, help_text='The string representation of this object', null=True)),
                ('ted', models.DateTimeField(help_text='The ted date for the cycle position', null=True)),
                ('_cp_id', models.TextField(null=True)),
                ('bidcycle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cycle_position_cycle', to='bidding.BidCycle')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cycle_position_position', to='position.Position')),
            ],
            options={
                'ordering': ['bidcycle__cycle_start_date'],
                'managed': True,
            },
        ),
        migrations.AlterModelOptions(
            name='biddingstatus',
            options={'managed': True},
        ),
        migrations.RemoveField(
            model_name='biddingstatus',
            name='bidcycle',
        ),
        migrations.AlterField(
            model_name='biddingstatus',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bid_cycle_statuses', to='bidding.CyclePosition'),
        ),
    ]