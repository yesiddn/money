from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import LimitOffsetPagination
from django.utils.dateparse import parse_date, parse_datetime
from django.utils import timezone
import datetime
from .models import Record
from .serializers import RecordSerializer
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiExample,
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
                enum=["expense", "transfer", "income", "investment"],
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
    ),
    create=extend_schema(
        description="""
        Crea un nuevo registro financiero.
        
        **Nota importante:** Los campos de tipo decimal como `amount` deben enviarse como strings 
        para mantener precisión exacta y evitar errores de redondeo. Ejemplo: `"1500.75"` en lugar de `1500.75`.
        """,
        examples=[
            OpenApiExample(
                "Ejemplo de Gasto",
                value={
                    "title": "Compra supermercado",
                    "description": "Compras mensuales",
                    "amount": "150000.50",
                    "account": 1,
                    "typeRecord": "expense",
                    "category": 1,
                    "paymentType": "card",
                    "currency": 1,
                    "date_time": "2025-12-14T22:00:00-05:00",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Ejemplo de Ingreso",
                value={
                    "title": "Salario",
                    "description": "Pago mensual",
                    "amount": "3500000.00",
                    "account": 1,
                    "typeRecord": "income",
                    "category": 2,
                    "paymentType": "transfer",
                    "currency": 1,
                    "date_time": "2025-12-01T08:00:00-05:00",
                },
                request_only=True,
            ),
        ],
    ),
    update=extend_schema(
        description="""
        Actualiza un registro financiero existente.
        
        **Nota:** El campo `amount` debe enviarse como string. Ejemplo: `"1500.75"`.
        """,
    ),
    partial_update=extend_schema(
        description="""
        Actualiza parcialmente un registro financiero.
        
        **Nota:** Si actualizas el campo `amount`, debe enviarse como string. Ejemplo: `"1500.75"`.
        """,
    ),
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

        # Date filters: accept YYYY-MM-DD or full ISO datetimes with timezone
        date = self.request.query_params.get("date")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if date:
            # try YYYY-MM-DD first
            parsed_date = parse_date(date)
            if parsed_date:
                qs = qs.filter(date_time__date=parsed_date)
            else:
                # try full ISO datetime
                parsed_dt = parse_datetime(date)
                if parsed_dt:
                    dt_utc = to_utc(parsed_dt)
                    # filter by the UTC date of the provided datetime
                    qs = qs.filter(date_time__date=dt_utc.date())

        if date_from:
            # accept date or full datetime
            parsed_date = parse_date(date_from)
            if parsed_date:
                qs = qs.filter(date_time__date__gte=parsed_date)
            else:
                parsed_dt = parse_datetime(date_from)
                if parsed_dt:
                    dt_utc = to_utc(parsed_dt)
                    qs = qs.filter(date_time__gte=dt_utc)

        if date_to:
            parsed_date = parse_date(date_to)
            if parsed_date:
                qs = qs.filter(date_time__date__lte=parsed_date)
            else:
                parsed_dt = parse_datetime(date_to)
                if parsed_dt:
                    dt_utc = to_utc(parsed_dt)
                    qs = qs.filter(date_time__lte=dt_utc)

        # Order newest first; fallback to created_at for deterministic order
        return qs.order_by("-date_time", "-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


def to_utc(dt):
    # dt is a datetime; return timezone-aware UTC datetime
    if timezone.is_naive(dt):
        # assume current server timezone if naive
        aware = timezone.make_aware(dt, timezone.get_current_timezone())
    else:
        aware = dt
    return aware.astimezone(datetime.timezone.utc)
