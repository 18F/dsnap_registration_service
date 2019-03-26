from jsonschema import Draft7Validator
from rest_framework import serializers

from .models import Registration

SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",

    "definitions": {
        "nonzero_money": {
            "anyOf": [
                {"type": "number", "minimum": 0},
                {"type": "null"}
            ]
        },
        "address": {
            "type": "object",
            "properties": {
                "street1": {"type": "string"},
                "street2": {"type": "string"},
                "city": {"type": "string"},
                "state": {"type": "string"},
                "zipcode": {"type": "string"}
            }
        },
    },

    "type": "object",

    "properties": {
        "disaster_id": {"type": "number", "minimum": 0},
        "preferred_language": {"type": "string"},
        "phone": {"type": "string", "pattern": r"^\d{10}$"},
        "email": {"type": "string"},
        "residential_address": {"$ref": "#/definitions/address"},
        "mailing_address": {"$ref": "#/definitions/address"},
        "county": {"type": "string"},
        "state_id": {"type": "string"},
        "has_inaccessible_liquid_resources": {"type": "boolean"},
        "has_lost_or_inaccessible_income": {"type": "boolean"},
        "purchased_or_plans_to_purchase_food": {"type": "boolean"},
        "disaster_expenses": {
            "type": "object",
            "properties": {
                "food_loss": {
                    "$ref": "#/definitions/nonzero_money"},
                "home_or_business_repairs": {
                    "$ref": "#/definitions/nonzero_money"},
                "temporary_shelter_expenses": {
                    "$ref": "#/definitions/nonzero_money"},
                "evacuation_expenses": {
                    "$ref": "#/definitions/nonzero_money"},
                "other": {
                    "$ref": "#/definitions/nonzero_money"},
            },
            "additionalProperties": False
        },
        "household": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string"},
                    "middle_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "dob": {"type": "string"},
                    "sex": {"enum": ["male", "female", None]},
                    "ssn": {"type": "string", "pattern": r"^\d{9}$"},
                    "race": {
                        "enum": [
                            "American Indian or Alaskan Native",
                            "Asian",
                            "Black or African American",
                            "Native Hawaiian or Other Pacific Islander",
                            "White",
                            None
                        ]
                    },
                    "ethnicity": {
                        "enum": [
                            "Hispanic or Latino",
                            "Not Hispanic or Latino",
                            None
                        ]
                    },
                    "has_food_assistance": {"type": "boolean"},
                    "money_on_hand": {"$ref": "#/definitions/nonzero_money"},
                    "income": {
                        "type": "object",
                        "properties": {
                            "self_employed": {
                                "$ref": "#/definitions/nonzero_money"},
                            "unemployment":
                                {"$ref": "#/definitions/nonzero_money"},
                            "cash_assistance": {
                                "$ref": "#/definitions/nonzero_money"},
                            "disability": {
                                "$ref": "#/definitions/nonzero_money"},
                            "social_security": {
                                "$ref": "#/definitions/nonzero_money"},
                            "veterans_benefits": {
                                "$ref": "#/definitions/nonzero_money"},
                            "alimony": {
                                "$ref": "#/definitions/nonzero_money"},
                            "child_support": {
                                "$ref": "#/definitions/nonzero_money"},
                            "other_sources": {
                                "$ref": "#/definitions/nonzero_money"}
                        },
                        "additionalProperties": False
                    },
                    "jobs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "employer_name": {"type": "string"},
                                "pay": {"$ref": "#/definitions/nonzero_money"},
                                "is_dsnap_agency": {"type": "boolean"}
                            },
                            "additionalProperties": False
                         }
                    }
                },
                "additionalProperties": False
            }
        }
    },
    "required": [
        "disaster_id",
    ],
    "additionalProperties": False
}


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = '__all__'

    def create(self, validated_data):
        """
        Set original_data (which is set to be not editable) to the latest_data
        on creation
        """
        return Registration.objects.create(
            original_data=validated_data['latest_data'], **validated_data)

    def to_internal_value(self, data):
        """
        Eliminate the need to have POST and other submissions to have the
        actual data under a "latest_data" key by ensuring it on deserialization
        """
        new_data = {
            "latest_data": data
        }
        return super().to_internal_value(new_data)

    def validate(self, data):
        errors = [e.message for e in
                  Draft7Validator(SCHEMA).iter_errors(data['latest_data'])]
        if errors:
            raise serializers.ValidationError(f"Validation failed: {errors}")
        return data
