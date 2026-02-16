import datetime
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


class ChangeUserRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        new_role = request.data.get("role")

        pass


class SessionTestAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        token = request.auth

        if hasattr(token, "payload"):
            exp_timestamp = token.payload.get("exp")  # integer
        else:
            exp_timestamp = None

        if exp_timestamp:
            exp_datetime = datetime.datetime.fromtimestamp(exp_timestamp)
        else:
            exp_datetime = None

        return Response(
            {
                "user": str(user),
                "token_expires_at": exp_datetime,
            }
        )
