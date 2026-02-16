import datetime
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from ..services import RoleService


class ChangeUserRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        new_role = request.data.get("role")

        if not new_role:
            return Response({"error": "role field is mandatory"}, status=400)

        try:
            user = RoleService.change_user_role(request.user, user_id, new_role)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=403)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        return Response(
            {"msg": f"{user.username}, Role {user.user_role}, ga o'zgartirildi"},
            status=200,
        )


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
