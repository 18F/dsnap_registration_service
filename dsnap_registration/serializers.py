from rest_framework import serializers
from .models import Registration

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = '__all__'

    def create(self, validated_data):
        """
        Set original_data (which is set to be not editable) to the latest_data
        on creation
        """
        return Registration.objects.create(original_data=validated_data['latest_data'], **validated_data)

    def to_internal_value(self, data):
        """
        Eliminate the need to have POST and other submissions to have the
        actual data under a "latest_data" key by ensuring it on deserialization
        """
        new_data = {
            "latest_data": data
        }
        return super().to_internal_value(new_data)
