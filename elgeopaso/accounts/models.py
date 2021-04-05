from django.contrib.auth.models import User
from django.db import models


# Users
class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    report_hour = models.BooleanField("Rapport horaire", blank=False, default=False)
    report_week = models.BooleanField(
        "Rapport hebdomadaire", blank=False, default=False
    )

    def __str__(self):
        if self.report_hour and self.report_week:
            return "Utilisateur.rice abonné.e aux rapports horaires" " et hebdomadaires"
        elif self.report_hour:
            return "Utilisateur.rice abonné.e aux rapports horaires"
        elif self.report_week:
            return "Utilisateur.rice abonné.e aux rapports hebdomadaires"
        else:
            return "L'utilisateur.rice n'est abonné.e à aucun rapport"

    class Meta:
        app_label = "accounts"
        verbose_name = "Abonnements mail"
