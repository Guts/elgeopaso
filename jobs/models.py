# -*- coding: utf-8 -*-
#! python3  # noqa: E265  # noqa E265

"""
    Application database models.
"""

# #############################################################################
# ########## Libraries #############
# ##################################


# Django
from django.db import models
from django.core.validators import MaxLengthValidator
from django.template.defaultfilters import truncatechars

# 3rd party
import arrow

# #############################################################################
# ########### Models ###############
# ##################################


class GeorezoRSS(models.Model):
    """GeoRezo RAW offers."""

    id_rss = models.IntegerField(
        "Identifiant du flux RSS", db_index=True, primary_key=True
    )
    title = models.CharField(
        "Titre de l'offre",
        blank=True,
        null=True,
        max_length=250,
        validators=[MaxLengthValidator(250)],
        help_text="Doit être de la forme [TYPE_CONTRAT]"
        " INTITULÉ - LIEU"
        " (CODE_DÉPARTEMENT_OU_PAYS)",
    )
    content = models.TextField("Contenu de l'offre", blank=True, null=True)
    pub_date = models.DateTimeField("Publiée le", db_index=True, blank=True, null=True)
    created = models.DateTimeField("Ajoutée le", db_index=True, auto_now_add=True)
    updated = models.DateTimeField("Modifiée le", db_index=True, auto_now=True)
    source = models.BooleanField()
    to_update = models.BooleanField(
        "Analyser de nouveau",
        db_index=True,
        help_text="Cocher cette case pour que "
        "l'offre soit de nouveau "
        "analysée à la prochaine "
        "mise à jour.",
        default=False,
    )

    class Meta:
        db_table = "georezo_rss"
        unique_together = (("id_rss", "pub_date", "source"),)
        verbose_name_plural = "Offres d'emploi brutes issues du RSS de GeoRezo"
        get_latest_by = "pub_date"

    @property
    def short_content(self):
        return truncatechars(self.content, 300)

    short_content.fget.short_description = "Contenu (aperçu)"

    @property
    def offre_traitee(self):
        return Offer.objects.get(id_rss=self.id_rss).id

    offre_traitee.fget.short_description = "Offre traitée"


class Contract(models.Model):
    abbrv = models.CharField(
        max_length=20,
        db_index=True,
        unique=True,
        primary_key=True,
        verbose_name="Abbréviation",
    )
    name = models.CharField(max_length=75, verbose_name="Intitulé complet")
    comment = models.TextField(blank=True, verbose_name="Commentaire")
    created = models.DateTimeField("Ajouté le", auto_now_add=True)
    updated = models.DateTimeField("Modifié le", auto_now=True)

    def __str__(self):
        return self.abbrv

    class Meta:
        verbose_name = "Type de contrat"
        verbose_name_plural = "Types de contrats"
        ordering = ["abbrv"]


class ContractVariations(models.Model):
    # VARIABLES
    ND = "UNDEFINED"
    # FIELDS
    label = models.CharField(
        max_length=200, default=ND, verbose_name="Variante du libellé"
    )
    name = models.ForeignKey(
        Contract,
        verbose_name="Type de contrat correspondant",
        default=ND,
        on_delete=models.SET_DEFAULT,
    )

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = "Variante du type de contrat"
        verbose_name_plural = "Variantes des types de contrats"


class Technology(models.Model):
    # LICENSE
    OSS = "OSS"
    PROPRIETARY = "PROPRIETARY"
    ND = "UNDEFINED"

    TYPE_LICENSE = (
        (OSS, "Libre"),
        (PROPRIETARY, "Propriétaire"),
        (ND, "Indéfini"),
    )

    # TYPE
    DEV = "LANGUAGE"
    SOFTWARE = "SOFTWARE"

    TYPE_SOFT = (
        (DEV, "Language de programmation"),
        (SOFTWARE, "Logiciel"),
        (ND, "Indéfini"),
    )

    # FIELDS
    name = models.CharField(
        max_length=200, db_index=True, unique=True, verbose_name="Nom"
    )
    license = models.CharField(
        max_length=20,
        choices=TYPE_LICENSE,
        default=ND,
        verbose_name="Licence principale",
    )

    type_soft = models.CharField(
        max_length=50, choices=TYPE_SOFT, default=ND, verbose_name="Catégorie"
    )
    created = models.DateTimeField("Ajoutée le", auto_now_add=True)
    updated = models.DateTimeField("Modifiée le", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Technologie"
        verbose_name_plural = "Technologies"
        ordering = [
            "name",
        ]


class TechnologyVariations(models.Model):
    # VARIABLES
    ND = "UNDEFINED"
    # FIELDS
    label = models.CharField(
        max_length=200, default=ND, verbose_name="Variante du libellé"
    )
    name = models.ForeignKey(
        Technology,
        verbose_name="Technologie correspondante",
        default=ND,
        on_delete=models.SET_DEFAULT,
    )

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = "Variante des technologies"
        verbose_name_plural = "Variantes des technologies"


class Place(models.Model):
    # SCALE
    DPT = "DEPARTEMENT"
    TOM = "TOM"
    COUNTRY = "COUNTRY"
    UNDEFINED = "UNDEFINED"

    SCALES = (
        (DPT, "Département français"),
        (TOM, "Territoire français"),
        (COUNTRY, "Pays"),
        (UNDEFINED, "Indéfini"),
    )

    # FIELDS
    name = models.CharField(
        max_length=100, unique=True, primary_key=True, verbose_name="Nom"
    )
    code = models.CharField(
        max_length=5,
        unique=True,
        verbose_name="Code",
        help_text="Code du département ou  <a href='https://fr.wikipedia.org/wiki/ISO_3166-1#Table_de_codage'>code ISO à 3 lettres pour un pays (voir sur Wikipédia)</a>.",
    )
    scale = models.CharField(
        max_length=50,
        choices=SCALES,
        default=DPT,
        db_index=True,
        blank=True,
        verbose_name="Echelle",
    )
    created = models.DateTimeField("Ajouté le", auto_now_add=True)
    updated = models.DateTimeField("Modifié le", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Lieu"
        verbose_name_plural = "Lieux"
        ordering = [
            "code",
        ]


class PlaceVariations(models.Model):
    # VARIABLES
    ND = "UNDEFINED"
    # FIELDS
    label = models.CharField(
        max_length=200, default=ND, verbose_name="Variante du libellé"
    )
    name = models.ForeignKey(
        Place,
        verbose_name="Lieu correspondant",
        default=ND,
        on_delete=models.SET_DEFAULT,
    )

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = "Variante de lieu"
        verbose_name_plural = "Variantes des lieux"


class JobPosition(models.Model):
    # FIELDS
    name = models.CharField(
        max_length=100, unique=True, primary_key=True, verbose_name="Intitulé"
    )
    comment = models.CharField(max_length=5, blank=True, verbose_name="Description")
    created = models.DateTimeField("Créé le", auto_now_add=True)
    updated = models.DateTimeField("Modifié le", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Métier"
        verbose_name_plural = "Métiers"
        ordering = [
            "name",
        ]


class JobPositionVariations(models.Model):
    # VARIABLES
    ND = "UNDEFINED"
    # FIELDS
    label = models.CharField(
        max_length=200, default=ND, verbose_name="Variante du libellé"
    )
    name = models.ForeignKey(
        JobPosition,
        verbose_name="Métier correspondant",
        default=ND,
        on_delete=models.SET_DEFAULT,
    )

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = "Variante de métier"
        verbose_name_plural = "Variantes des métiers"


class Source(models.Model):
    # FIELDS
    name = models.CharField(
        max_length=50,
        db_index=True,
        unique=True,
        default="GEOREZO_RSS",
        verbose_name="Nom",
    )
    url = models.URLField(blank=True, verbose_name="Adresse web")
    comment = models.TextField(blank=True, verbose_name="Commentaire")
    created = models.DateTimeField("Ajoutée le", auto_now_add=True)
    updated = models.DateTimeField("Modifiée le", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Source de l'offre"
        verbose_name_plural = "Sources"


class Offer(models.Model):
    id_rss = models.IntegerField(blank=True, db_index=True, unique=True)

    raw_offer = models.OneToOneField(
        GeorezoRSS, null=True, on_delete=models.SET_NULL, related_name="clean_offer"
    )

    title = models.CharField(
        "Titre", max_length=200, validators=[MaxLengthValidator(200)]
    )
    content = models.TextField("Contenu", null=True)
    pub_date = models.DateTimeField("Date de publication sur le RSS", null=True,)
    week = models.IntegerField(
        verbose_name="Semaine de publication",
        null=True,
        help_text="Format : <em>YYYYSS</em>.",
    )
    contract = models.ForeignKey(
        Contract,
        db_index=True,
        verbose_name="Type de contrat",
        null=True,
        default="ND",
        on_delete=models.SET_DEFAULT,
    )
    technologies = models.ManyToManyField(Technology, verbose_name="Technologies",)

    jobs_positions = models.ManyToManyField(JobPosition, verbose_name="Métiers",)
    place = models.ForeignKey(
        Place,
        verbose_name="Lieu",
        null=True,
        default="ND",
        on_delete=models.SET_DEFAULT,
    )
    source = models.ForeignKey(
        Source, verbose_name="Source", null=True, on_delete=models.SET_NULL
    )
    created = models.DateTimeField("Ajoutée le", auto_now_add=True)
    updated = models.DateTimeField("Modifiée le", auto_now=True)

    def __str__(self):
        return self.title

    def get_week_from_date_pub(self):
        if self.pub_date:
            return "{}{}".format(
                arrow.get(self.pub_date).isocalendar()[0],
                str(arrow.get(self.pub_date).isocalendar()[1]).zfill(2),
            )
        else:
            self.week.help_text

    @property
    def short_content(self):
        return truncatechars(self.content, 300)

    short_content.fget.short_description = "Contenu (aperçu)"

    @property
    def offre_brute(self):
        return GeorezoRSS.objects.get(id_rss=self.id_rss).id_rss

    class Meta:
        verbose_name = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"
        get_latest_by = "pub_date"
        ordering = [
            "id_rss",
        ]
