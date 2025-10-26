from authentication.api.serializers import UserSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view that:
    - Returns the access token in JSON
    - Places the refresh token in an HttpOnly cookie
    """

    def post(self, request, *args, **kwargs):
        # Use TokenObtainPairView to generate tokens
        response = super().post(request, *args, **kwargs)

        # Get refresh token in response
        refresh_token = response.data.get("refresh")

        if refresh_token:
            # Add HttpOnly cookie with refresh token in response
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                max_age=604800,  # 7 days
                httponly=True,  # No JS Access
                secure=True,  # Only if HTTPS
                samesite="Strict",  # CSRF Protection
            )
            # Remove refresh token from response
            response.data.pop("refresh")

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Custom refresh view that:
    - Reads the refresh token from the cookie (instead of the JSON body)
    - Returns a new access token in JSON
    """

    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Missing refresh token in cookies."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Create the serializer manually with the token from cookie
        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except InvalidToken:
            return Response(
                {"detail": "Refresh token invalid or expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
