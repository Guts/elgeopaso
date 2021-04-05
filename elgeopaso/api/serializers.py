from elgeopaso.jobs.models import (
    Contract,
    JobPosition,
    Offer,
    Place,
    PlaceVariations,
    Technology,
)
from rest_framework import serializers


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"
        # fields = ('abbrv', 'name', 'comment')


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosition
        fields = "__all__"
        # fields = ('abbrv', 'name', 'comment')


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        depth = 1
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


class PlaceVariationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceVariations
        # fields = '__all__'
        fields = ("label",)


class PlaceSerializer(serializers.ModelSerializer):
    variations = PlaceVariationsSerializer(source="label", read_only=True, many=True)

    class Meta:
        model = Place
        # fields = '__all__'
        # depth = 1
        fields = ("name", "code", "scale", "variations")


class TechnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = "__all__"
        # fields = ('abbrv', 'name', 'comment')
