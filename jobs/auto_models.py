# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals
from django.db import models


class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    group_id = models.IntegerField()
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group_id', 'permission'),)


class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=50)
    content_type_id = models.IntegerField()
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type_id', 'codename'),)


class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user_id = models.IntegerField()
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user_id', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user_id = models.IntegerField()
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user_id', 'permission'),)


class Autres(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    langue = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'autres'


class Contrats(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    cdi = models.NullBooleanField()
    cdd = models.NullBooleanField()
    fpt = models.NullBooleanField()
    stage = models.NullBooleanField()
    apprentissage = models.NullBooleanField()
    vi = models.NullBooleanField()
    these = models.NullBooleanField()
    post_doc = models.NullBooleanField()
    mission = models.NullBooleanField()
    autres = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'contrats'


class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    action_time = models.DateTimeField()
    user_id = models.IntegerField()
    content_type_id = models.IntegerField(blank=True, null=True)
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DjangoSite(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    domain = models.CharField(max_length=100)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'django_site'


class Georezo(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    title = models.TextField(blank=True, null=True)  # This field type is a guess.
    content = models.TextField(blank=True, null=True)
    date_pub = models.DateTimeField(blank=True, null=True)
    source = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'georezo'
        unique_together = (('id', 'date_pub', 'source'),)


class GeorezoHisto(models.Model):
    idu = models.IntegerField(primary_key=True)
    id_forum = models.IntegerField(blank=True, null=True)
    id_rss = models.IntegerField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)  # This field type is a guess.
    published = models.DateTimeField(blank=True, null=True)
    contrat = models.TextField(blank=True, null=True)  # This field type is a guess.
    visites = models.IntegerField(blank=True, null=True)
    dpt1 = models.TextField(blank=True, null=True)  # This field type is a guess.
    dpt2 = models.TextField(blank=True, null=True)  # This field type is a guess.
    region = models.TextField(blank=True, null=True)  # This field type is a guess.
    region_typ = models.TextField(blank=True, null=True)  # This field type is a guess.
    summary = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'georezo_histo'


class JobsContrat(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    type = models.CharField(max_length=255)
    date_pub = models.DateTimeField()
    week_number = models.IntegerField()
    day_of_week = models.IntegerField()
    dept = models.CharField(max_length=3, blank=True, null=True)
    country = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jobs_contrat'


class JobsMonth(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    cdi = models.IntegerField(blank=True, null=True)
    cdd = models.IntegerField(blank=True, null=True)
    fpt = models.IntegerField(blank=True, null=True)
    stage = models.IntegerField(blank=True, null=True)
    apprentissage = models.IntegerField(blank=True, null=True)
    vi = models.IntegerField(blank=True, null=True)
    these = models.IntegerField(blank=True, null=True)
    post_doc = models.IntegerField(blank=True, null=True)
    mission = models.IntegerField(blank=True, null=True)
    autre = models.IntegerField(blank=True, null=True)
    month_milsec = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jobs_month'


class JobsPlacesDpts(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    dpt_name = models.CharField(max_length=200)
    dpt_code = models.CharField(unique=True, max_length=3)
    region_name = models.CharField(max_length=200)
    region_code = models.CharField(unique=True, max_length=200)
    centroid_x = models.FloatField()
    centroid_y = models.FloatField()

    class Meta:
        managed = False
        db_table = 'jobs_places_dpts'


class JobsPlacesGlobal(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    libelle = models.CharField(max_length=200)
    niveau_territorial = models.IntegerField()
    logs = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'jobs_places_global'


class JobsSemanticGlobal(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    word = models.CharField(max_length=200)
    occurrences = models.IntegerField()
    first_offer = models.IntegerField()
    first_time = models.DateTimeField()
    last_offer = models.IntegerField()
    last_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'jobs_semantic_global'


class JobsTechnosTypes(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    proprietaire = models.IntegerField()
    libre = models.IntegerField()
    sgbd = models.IntegerField()
    programmation = models.IntegerField()
    web = models.IntegerField()
    cao_dao = models.IntegerField()
    teledec = models.IntegerField()
    autres = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'jobs_technos_types'


class JobsWeek(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    year = models.IntegerField(blank=True, null=True)
    week = models.IntegerField(blank=True, null=True)
    first_day = models.DateTimeField(blank=True, null=True)
    cdi = models.IntegerField(blank=True, null=True)
    cdd = models.IntegerField(blank=True, null=True)
    fpt = models.IntegerField(blank=True, null=True)
    stage = models.IntegerField(blank=True, null=True)
    apprentissage = models.IntegerField(blank=True, null=True)
    vi = models.IntegerField(blank=True, null=True)
    these = models.IntegerField(blank=True, null=True)
    post_doc = models.IntegerField(blank=True, null=True)
    mission = models.IntegerField(blank=True, null=True)
    autre = models.IntegerField(blank=True, null=True)
    week_milsec = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jobs_week'


class JobsYear(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    year = models.IntegerField()
    cdi = models.IntegerField()
    cdd = models.IntegerField()
    fpt = models.IntegerField()
    stage = models.IntegerField()
    apprentissage = models.IntegerField()
    vi = models.IntegerField()
    these = models.IntegerField()
    post_doc = models.IntegerField()
    mission = models.IntegerField()
    autre = models.IntegerField()
    year_milsec = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jobs_year'


class Lieux(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    lieu_lib = models.TextField(blank=True, null=True)  # This field type is a guess.
    lieu_type = models.IntegerField(blank=True, null=True)
    log = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'lieux'


class Metiers(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    administrateur = models.IntegerField(blank=True, null=True)
    cartographe = models.IntegerField(blank=True, null=True)
    charge_etude = models.IntegerField(blank=True, null=True)
    charge_mission = models.IntegerField(blank=True, null=True)
    chef = models.IntegerField(blank=True, null=True)
    geometre = models.IntegerField(blank=True, null=True)
    ingenieur = models.IntegerField(blank=True, null=True)
    responsable = models.IntegerField(blank=True, null=True)
    sigiste = models.IntegerField(blank=True, null=True)
    technicien = models.IntegerField(blank=True, null=True)
    topographe = models.IntegerField(blank=True, null=True)
    geomaticien = models.IntegerField(blank=True, null=True)
    autres = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'metiers'
