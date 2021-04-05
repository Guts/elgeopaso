#! python3  # noqa: E265

# ############################################################################
# ########## Libraries #############
# ##################################
# Standard library
import logging

# Django
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

# 3rd party modules
import arrow

# Django project
from elgeopaso.accounts.models import Subscription
from elgeopaso.jobs.models import (
    JobPosition,
    JobPositionVariations,
    Offer,
    Place,
    PlaceVariations,
    Technology,
    TechnologyVariations,
)

# ############################################################################
# ########### Classes #############
# #################################


class Command(BaseCommand):
    args = "<foo bar ...>"
    help = """
                Commands to manage weekly report
           """

    # attributes
    now = arrow.now(settings.TIME_ZONE)

    # Parsing options ------------------------------------------------------

    def handle(self, *args, **options):
        """
        TO DO
        """
        # self.dt_prev = self.now.shift(days=-1).datetime
        self.dt_prev = self.now.shift(weeks=-1).datetime
        # ANALISIS SCORES
        # -- WHOLE DB
        offers_all = Offer.objects.count()
        no_place_all = Offer.objects.filter(place="ND").count()
        no_contract_all = Offer.objects.filter(contract="ND").count()
        base_msg = (
            "BASE GLOBALE DES {} OFFRES\n"
            "\t- {} ({}%) offres sans lieu reconnu (https://elgeopaso.georezo.net/jobs/search/?place=ND)\n"
            "\t- {} ({}%) offres sans contrat reconnu (https://elgeopaso.georezo.net/jobs/search/?contract=ND)\n"
            "\n=====================================================\n".format(
                offers_all,
                no_place_all,
                int(100 * no_place_all / offers_all),
                no_contract_all,
                int(100 * no_contract_all / offers_all),
            )
        )
        # -- NEW OFFERS
        # get offers added since previous execution
        new_offers = Offer.objects.filter(pub_date__gte=self.dt_prev)
        ct_added = new_offers.count()
        # Offers without place
        no_place = new_offers.filter(place="ND")
        if no_place.count():
            edit_url = [
                "- {}/admin/jobs/georezorss/{}/change/".format(settings.BASE_URL, i)
                for i in no_place.values_list("id_rss", flat=True)
            ]
            place_msg = "{} offre(s) sans lieu : \n\t{}".format(
                no_place.count(), "\n\t".join(edit_url)
            )
        else:
            place_msg = (
                "RAS : un lieu a été trouvé pour toutes les"
                " nouvelles offres publiées."
            )
        # Offer without contract
        no_contract = new_offers.filter(contract="ND")
        if no_contract.count():
            edit_url = [
                "- {}/admin/jobs/georezorss/{}/change/".format(settings.BASE_URL, i)
                for i in no_contract.values_list("id_rss", flat=True)
            ]
            contract_msg = "{} offre(s) sans contrat : \n\t{}".format(
                no_contract.count(), "\n\t".join(edit_url)
            )
        else:
            contract_msg = (
                "RAS : un type de contrat a été trouvé pour"
                " toutes les nouvelles offres publiées."
            )
        # DB checks
        ct_broken_places = PlaceVariations.objects.exclude(
            name__in=Place.objects.all()
        ).count()
        ct_broken_techs = TechnologyVariations.objects.exclude(
            name__in=Technology.objects.all()
        ).count()

        ct_broken_jobs = JobPositionVariations.objects.exclude(
            name__in=JobPosition.objects.all()
        ).count()

        if ct_broken_places + ct_broken_techs + ct_broken_jobs:
            db_msg = (
                "\n{} relations cassées dans les lieux"
                "\n{} relations cassées dans les technologies"
                "\n{} relations cassées dans les métiers".format(
                    ct_broken_places, ct_broken_techs, ct_broken_jobs
                )
            )
        else:
            db_msg = "Aucun problème trouvé dans la base de données."

        # Mail report
        dest = settings.REPORT_RECIPIENTS
        dest.extend(
            Subscription.objects.select_related()
            .filter(report_week=True)
            .values_list("user__email", flat=True)
        )
        if not settings.DEBUG:
            send_mail(
                "El Géo Paso - Rapport hebdomadaire - {} semaine {}".format(
                    self.now.year, self.now.week
                ),
                base_msg + "{} NOUVELLES OFFRES\n\n"
                "ANALYSE\n\nLIEUX\n{}\n_______\n"
                "\nCONTRATS\n{}\n_______\n"
                "\nSANTE\n{} ".format(ct_added, place_msg, contract_msg, db_msg),
                settings.EMAIL_HOST_USER,
                dest,
                fail_silently=False,
            )
        else:
            # send_mail(
            #           "El Géo Paso - Rapport hebdomadaire - {} semaine {}"
            #           .format(self.now.year, self.now.week),
            #           base_msg +
            #           "{} NOUVELLES OFFRES\n\n"
            #           "ANALYSE\n\nLIEUX\n{}\n_______\n"
            #           "\nCONTRATS\n{}\n_______\n"
            #           "\nSANTE\n{} "
            #           .format(ct_added,
            #                   place_msg,
            #                   contract_msg,
            #                   db_msg),
            #           settings.EMAIL_HOST_USER,
            #           dest,
            #           fail_silently=False,
            #           )
            pass
        logging.info("Metrics retrieved and sent")
