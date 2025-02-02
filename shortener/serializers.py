from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ShortenedURL

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

# ✅ Serializador para CREAR URLs (solo recibe lo necesario)
class ShortenedURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortenedURL
        fields = ['original_url', 'is_private']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['owner'] = request.user  # 🔹 Asigna correctamente el usuario autenticado como owner
        return super().create(validated_data)

# ✅ Serializador SOLO para LISTAR/OBTENER URLs (ya no afecta la creación)
class ShortenedURLResponseSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        model = ShortenedURL
        fields = ['id', 'original_url', 'short_url', 'is_private', 'views', 'created_at', 'owner']

    def get_short_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f"/r/{obj.short_code}")
        return f"/r/{obj.short_code}"

    def get_owner(self, obj):
        if obj.owner is not None:
            request = self.context.get('request')
            if request and request.user.is_superuser:  # 🔹 Superusuarios ven más detalles
                return {
                    "id": obj.owner.id,
                    "username": obj.owner.username,
                    "email": obj.owner.email
                }
            return {"id": obj.owner.id}  # 🔹 Usuarios normales solo ven el ID
        return None  # Si no hay dueño, se devuelve None
