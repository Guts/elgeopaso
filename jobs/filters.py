from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget, RangeWidget

from .models import Offer


class OfferFilter(filters.FilterSet):
    years = [i.year for i in Offer.objects.dates("pub_date", "year")]
    title = filters.CharFilter(lookup_expr="icontains",
                                      label="Le titre contient :")
    content = filters.CharFilter(lookup_expr="icontains",
                                 label="L'annonce contient :")
    date = filters.DateFromToRangeFilter("pub_date",
                                         label="Publication",
                                         lookup_expr='contains',
                                         widget=RangeWidget(attrs={'placeholder': 'DD/MM/YYYY'}))
    # contract = django_filters.ChoiceFilter("contract",
    #                         widget=forms.Select())
    raw_offer__to_update = filters.BooleanFilter(label="En attente",
                                                  widget=BooleanWidget())


    class Meta:
        model = Offer
        fields = ["contract", "place", "technologies",
                  "pub_date", "content", "title",
                  "raw_offer__to_update"]
