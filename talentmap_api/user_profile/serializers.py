from django.core.exceptions import ValidationError
from django.db.models import Q
from django.apps import apps
from rest_framework import serializers
from rest_framework.reverse import reverse

from talentmap_api.common.common_helpers import resolve_path_to_view, validate_filters_exist
from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.language.serializers import LanguageQualificationSerializer
from talentmap_api.position.serializers import PositionSerializer

from django.contrib.auth.models import User
from talentmap_api.user_profile.models import UserProfile, Sharable, SavedSearch
from talentmap_api.position.models import Position


class UserSerializer(PrefetchedSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class SharableSerializer(PrefetchedSerializer):
    sharing_user = serializers.StringRelatedField(read_only=True)
    receiving_user = serializers.StringRelatedField(read_only=True)

    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        model = apps.get_model(obj.sharable_model)
        instance = model.objects.get(id=obj.sharable_id)

        return {
            "representation": f"{instance}",
            "url": reverse(f'{obj.sharable_model}-detail', kwargs={"pk": obj.sharable_id}, request=self.context.get("request"))
        }

    class Meta:
        model = Sharable
        fields = ["id", "sharing_user", "receiving_user", "content", "read"]


class UserProfileSerializer(PrefetchedSerializer):

    class Meta:
        model = UserProfile
        fields = "__all__"
        nested = {
            "user": {
                "class": UserSerializer,
                "kwargs": {
                    "read_only": True
                }
            },
            "language_qualifications": {
                "class": LanguageQualificationSerializer,
                "kwargs": {
                    "override_fields": [
                        "id",
                        "representation"
                    ],
                    "many": True,
                    "read_only": True,
                }
            },
            "favorite_positions": {
                "class": PositionSerializer,
                "kwargs": {
                    "override_fields": [
                        "id",
                        "representation"
                    ],
                    "many": True,
                    "read_only": True
                }
            },
            "received_shares": {
                "class": SharableSerializer,
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            }
        }


class UserProfileWritableSerializer(PrefetchedSerializer):

    class Meta:
        model = UserProfile
        fields = ["language_qualifications", "favorite_positions"]


class SavedSearchSerializer(PrefetchedSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    def validate(self, data):
        # We'll need the endpoint to validate our filters, so determine if our
        # datasource is an instance or a fresh object (in which case we use initial data)
        datasource = self.initial_data
        if self.instance:
            datasource = self.instance.__dict__

        # The endpoint to test our filters against is either the one stored, or the incoming endpoint
        endpoint = data.get("endpoint", datasource.get("endpoint"))
        # Likewise for the filters
        filters = data.get("filters", datasource.get("filters"))

        # Get our viewset using the endpoint
        try:
            view = resolve_path_to_view(endpoint)
        except:
            view = None
        finally:
            if not view:
                # Raise a validation error if the endpoint isn't good
                raise ValidationError(f"Endpoint {endpoint} is not a valid API path")

        # Get our list of filters, and verify that the specified filters are valid
        if hasattr(view, "filter_class"):
            validate_filters_exist(filters, view.filter_class)
        else:
            raise ValidationError("Specified endpoint does not support filters")

        return data

    class Meta:
        model = SavedSearch
        fields = "__all__"
