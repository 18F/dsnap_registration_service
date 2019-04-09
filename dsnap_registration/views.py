from rest_framework import generics
from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticated)

from .models import Registration
from .serializers import RegistrationSerializer

REGISTRATION_SEARCH_PARAMS = ('state_id',)
REGISTRANT_SEARCH_PARAMS = ('ssn', 'dob', 'last_name',)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class RegistrationList(generics.ListCreateAPIView):
    serializer_class = RegistrationSerializer

    def get_queryset(self):
        queryset = Registration.objects.all()

        search_filters = self.get_search_filters()
        queryset = queryset.filter(**search_filters)

        return queryset

    def get_search_filters(self):
        search_filters = {}
        for param in REGISTRATION_SEARCH_PARAMS:
            value = self.request.query_params.get(param)
            if value is not None:
                search_filters[f'latest_data__{param}'] = value
        for param in REGISTRANT_SEARCH_PARAMS:
            # The registrant is always the 1st memmber of the household
            value = self.request.query_params.get(f'registrant_{param}')
            if value is not None:
                search_filters[f'latest_data__household__0__{param}'] = value
        return search_filters


class RegistrationDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated | ReadOnly,)
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)
