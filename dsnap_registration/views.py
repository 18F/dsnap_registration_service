from rest_framework import generics
from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticated)

from .models import Registration
from .serializers import RegistrationSerializer, RegistrationStatusSerializer

REGISTRATION_SEARCH_PARAMS = (
    ('state_id', True),
)
REGISTRANT_SEARCH_PARAMS = (
    ('ssn', False),
    ('dob', False),
    ('last_name', True)
)


class AnonymousPost(BasePermission):
    def has_permission(self, request, view):
        return request.method == 'POST'


class RegistrationList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated | AnonymousPost,)
    serializer_class = RegistrationSerializer

    def get_queryset(self):
        queryset = Registration.objects.all()

        search_filters = self.get_search_filters()
        queryset = queryset.filter(**search_filters)

        return queryset

    def get_search_filters(self):
        search_filters = {}
        for param, case_insensitive_search in REGISTRATION_SEARCH_PARAMS:
            value = self.request.query_params.get(param)
            if value is not None:
                if case_insensitive_search:
                    search_filters[f'latest_data__{param}__iexact'] = value
                else:
                    search_filters[f'latest_data__{param}'] = value
        for param, case_insensitive_search in REGISTRANT_SEARCH_PARAMS:
            # The registrant is always the 1st memmber of the household
            value = self.request.query_params.get(f'registrant_{param}')
            if value is not None:
                if case_insensitive_search:
                    search_filters[f'latest_data__household__0__{param}__iexact'] = value
                else:
                    search_filters[f'latest_data__household__0__{param}'] = value
        return search_filters


class RegistrationDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

class RegistrationStatusUpdate(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Registration.objects.all()
    serializer_class = RegistrationStatusSerializer

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save(approved_by=self.request.user)
