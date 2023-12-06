from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse

import stripe
from django.conf import settings

from telegram_bot.messages import payment_paid_notification
from .serializers import PaymentSerializer, PaymentDetailSerializer, OrderSuccessSerializer, OrderCancelSerializer
from .models import Payment
from .utils import create_new_checkout_session


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

        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
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

            payment = Payment.objects.get(session_id=session_id)
            payment.status = "PAID"
            payment.save()

        # Passed signature verification
        return HttpResponse(status=200)

    @action(
        detail=True, methods=["POST"],
        permission_classes=[IsAuthenticated],
        url_path="payment-renew",
        url_name="payment_renew"
    )
    def payment_renew(self, request, *args, **kwargs):
        payment = self.get_object()

        if payment.status == "EXPIRED":
            borrowing = payment.borrowing
            price = payment.money_to_pay

            new_checkout_session = create_new_checkout_session(borrowing, price)

            payment.session_id = new_checkout_session.id
            payment.session_url = new_checkout_session.url
            payment.status = "PENDING"

            payment.save()

            return HttpResponse(status=200)

        return Response({"message": "Payment is not expired"}, status=status.HTTP_400_BAD_REQUEST)


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

        payment = Payment.objects.get(session_id=session.id)
        payment_paid_notification(payment)

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
