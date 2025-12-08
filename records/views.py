from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import LimitOffsetPagination
from django.utils.dateparse import parse_date
from .models import Record
from .serializers import RecordSerializer
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)


class StandardResultsSetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="typeRecord",
                description="Filter by record type (exact match).",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="date",
                description="Filter by exact date (YYYY-MM-DD) using the date part of `date_time`.",
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="date_from",
                description="Filter by start date (YYYY-MM-DD).",
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="date_to",
                description="Filter by end date (YYYY-MM-DD).",
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
)
class RecordViewSet(viewsets.ModelViewSet):
    """ViewSet para Record.

    - Restringe queryset a los records del usuario autenticado.
    - Ordena por `date_time` descendente (más nuevo -> más viejo).
    - Añade paginación y búsqueda por título/descripcion.
    - Permite filtrar por `typeRecord`, `date` (YYYY-MM-DD), `date_from`, `date_to`.
    - Asigna `user` en create.
    """

    serializer_class = RecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description"]

    def get_queryset(self):
        user = self.request.user
        qs = Record.objects.filter(user=user)

        # Filter by typeRecord exact match
        type_record = self.request.query_params.get("typeRecord")
        if type_record:
            qs = qs.filter(typeRecord=type_record)

        # Date filters: date (exact day), date_from, date_to (YYYY-MM-DD)
        date = self.request.query_params.get("date")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if date:
            parsed = parse_date(date)
            if parsed:
                qs = qs.filter(date_time__date=parsed)

        if date_from:
            parsed = parse_date(date_from)
            if parsed:
                qs = qs.filter(date_time__date__gte=parsed)

        if date_to:
            parsed = parse_date(date_to)
            if parsed:
                qs = qs.filter(date_time__date__lte=parsed)

        # Order newest first; fallback to created_at for deterministic order
        return qs.order_by("-date_time", "-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
