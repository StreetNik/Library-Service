from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import PaymentSerializer, PaymentDetailSerializer
from .models import Payment


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Payment.objects.all()

        return Payment.objects.filter(borrowing__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentSerializer

        return PaymentDetailSerializer
