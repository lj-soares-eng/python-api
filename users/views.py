from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.response import Response

from users import services
from users.models import User
from users.serializers import (
    UserCreateSerializer,
    UserResponseSerializer,
    UserUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=['Users'], responses=UserResponseSerializer(many=True)),
    retrieve=extend_schema(tags=['Users'], responses=UserResponseSerializer),
    create=extend_schema(
        tags=['Users'],
        request=UserCreateSerializer,
        responses={201: UserResponseSerializer},
    ),
    update=extend_schema(
        tags=['Users'],
        request=UserUpdateSerializer,
        responses=UserResponseSerializer,
    ),
    destroy=extend_schema(tags=['Users'], responses={204: None}),
)
class UserViewSet(viewsets.ViewSet):
    lookup_value_regex = r'[0-9]+'

    def list(self, request):
        users = User.objects.all()
        serializer = UserResponseSerializer(users, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserResponseSerializer(user)
        return Response(serializer.data)

    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = services.create_user(**serializer.validated_data)
        except services.DuplicateEmailError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(
            UserResponseSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, pk=None):
        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = services.update_user(pk, **serializer.validated_data)
        except services.UserNotFoundError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except services.DuplicateEmailError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(UserResponseSerializer(user).data)

    def destroy(self, request, pk=None):
        try:
            services.delete_user(pk)
        except services.UserNotFoundError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
