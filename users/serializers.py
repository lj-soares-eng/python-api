from rest_framework import serializers

from users.models import User


class UserCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=User.Role.choices)


class UserUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    role = serializers.ChoiceField(choices=User.Role.choices)


class UserResponseSerializer(serializers.ModelSerializer):
    passwordHash = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'passwordHash', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_passwordHash(self, obj):
        if obj.password.startswith('bcrypt$'):
            return obj.password.removeprefix('bcrypt$')
        return obj.password
