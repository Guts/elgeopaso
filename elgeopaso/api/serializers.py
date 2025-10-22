from rest_framework import serializers

from elgeopaso.jobs.models import (
    Contract,
    JobPosition,
    Offer,
    Place,
    PlaceVariations,
    Technology,
)


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"
        # fields = ('abbrv', 'name', 'comment')
        ref_name = "Contract"


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosition
        fields = "__all__"
        # fields = ('abbrv', 'name', 'comment')
        ref_name = "Job"

class PlaceVariationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceVariations
        # fields = '__all__'
        fields = ("label",)
        ref_name = "PlaceVariation"


class PlaceSerializer(serializers.ModelSerializer):
    variations = PlaceVariationsSerializer(source="label", read_only=True, many=True)

    class Meta:
        model = Place
        # fields = '__all__'
        # depth = 1
        ref_name = "Place"
        fields = ("name", "code", "scale", "variations")


class OfferSerializer(serializers.ModelSerializer):
    place = PlaceSerializer(read_only=True)
    contract = ContractSerializer(read_only=True)

    class Meta:
        model = Offer
        #FIX: depth = 1
        ref_name = "Offer"
        fields = (
            "id",
            "id_rss",
            "title",
            "pub_date",
            "contract",
            "place",
            "technologies",
            "jobs_positions",
            "source",
            "content",
            "raw_offer",
        )

class TechnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = "__all__"
        ref_name = "Techno"
        # fields = ('abbrv', 'name', 'comment')
