from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action, api_view, renderer_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse

import stripe
from django.conf import settings

from .serializers import PaymentSerializer, PaymentDetailSerializer, OrderSuccessSerializer, OrderCancelSerializer
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

    # Check if Stripe session was paid
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def success(self, request, *args, **kwargs):
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        payload = request.body

        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        # Handle checkout.session.completed event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            session_id = session["id"]

            # customer_email = session["customer_details"]["email"]
            # book_id = session["metadata"]["book_id"]

            payment = Payment.objects.get(session_id=session_id)
            payment.status = "PAID"
            payment.save()

        # Passed signature verification
        return HttpResponse(status=200)


class OrderSuccess(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        session = stripe.checkout.Session.retrieve(request.GET["session_id"])

        customer_email = session.customer_details.email

        amount = session.amount_total
        payment_status = session.payment_status

        response_data = {
            "customer_email": customer_email,
            "amount": amount / 100,  # Amount is in cents, convert to dollars
            "payment_status": payment_status,
        }

        serializer = OrderSuccessSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.data

        return Response(response_data, status=status.HTTP_200_OK)


class OrderCancel(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        session = stripe.checkout.Session.retrieve(request.GET["session_id"])

        amount = session.amount_total
        payment_status = session.payment_status
        payment_url = session.url

        response_data = {
            "amount": amount / 100,  # Amount is in cents, convert to dollars
            "payment_status": payment_status,
            "payment_url": payment_url,
        }

        serializer = OrderCancelSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.data

        return Response(response_data, status=status.HTTP_200_OK)
