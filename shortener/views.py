from django.shortcuts import redirect
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import ShortenedURL
from .serializers import UserSerializer, ShortenedURLSerializer, ShortenedURLResponseSerializer
from .permissions import IsOwnerOrAdmin

# ✅ Redirección de URLs acortadas
class ShortenedURLRedirectView(APIView):
    """🔓 Módulo de Redirección de URLs (Público)."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="🔓 Redirige a la URL original desde la URL acortada (Público).",
        tags=["Redirección de URLs"],
    )
    def get(self, request, short_code):
        try:
            url_instance = ShortenedURL.objects.get(short_code=short_code)
            url_instance.views += 1
            url_instance.save()
            return redirect(url_instance.original_url)
        except ShortenedURL.DoesNotExist:
            return Response({"error": "URL no encontrada"}, status=404)

# ✅ Autenticación y Registro
class AuthViewSet(viewsets.ViewSet):
    """🔓 Módulo de Autenticación (Registro y Login)."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="🔓 Registrar un nuevo usuario (Público).",
        request_body=UserSerializer,
        responses={201: "Registro exitoso", 400: "Error en los datos"},
        tags=["Autenticación"],
    )
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Registro exitoso."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="🔓 Iniciar sesión y obtener token JWT (Público).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Correo electrónico'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Contraseña'),
            },
            required=['email', 'password'],
        ),
        responses={200: "Tokens generados", 400: "Credenciales inválidas"},
        tags=["Autenticación"],
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(username=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"error": "Credenciales inválidas"}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
    operation_description="🔒 Cerrar sesión (Usuario autenticado).",
    responses={200: "Sesión cerrada exitosamente", 401: "No autorizado"},
    tags=["Autenticación"],
)
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        🔒 Cierra la sesión del usuario autenticado sin validaciones adicionales.
        """
        return Response({"message": "Sesión cerrada exitosamente"}, status=status.HTTP_200_OK)


# ✅ URLs Acortadas
class ShortenedURLViewSet(viewsets.ModelViewSet):
    """🔒 Módulo de Gestión de URLs Acortadas (Usuario autenticado)."""
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ShortenedURLResponseSerializer
        return ShortenedURLSerializer   

    @swagger_auto_schema(
        operation_description="🔒 Subir múltiples URLs en un JSON para acortar.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'urls': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="Lista de URLs a acortar"
                ),
                'response_type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Formato de respuesta (json o file)",
                    default="json"
                ),
            },
            required=['urls'],  # ✅ Ahora 'urls' es obligatorio
        ),
        responses={200: "URLs acortadas correctamente"},
        tags=["Gestión de URLs Acortadas"],
    )
    @action(detail=False, methods=['post'], url_path="bulk-upload", url_name="bulk_upload")
    def bulk_upload(self, request):
        """🔒 Recibe una lista de URLs en formato JSON y las acorta."""
        urls = request.data.get("urls", [])
        response_type = request.data.get("response_type", "json")

        if not urls or not isinstance(urls, list):
            return Response({"error": "Se requiere una lista de URLs"}, status=status.HTTP_400_BAD_REQUEST)

        shortened_urls = []
        for url in urls:
            serializer = ShortenedURLSerializer(data={'original_url': url, 'is_private': False}, context={'request': request})
            if serializer.is_valid():
                instance = serializer.save()
                short_url = request.build_absolute_uri(f"/r/{instance.short_code}")
                shortened_urls.append({"id": instance.id, "short_url": short_url})
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if response_type == "file":
            content = "\n".join(f"{item['id']},{item['short_url']}" for item in shortened_urls)
            response = Response(content, content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename="shortened_urls.txt"'
            return response

        return Response(shortened_urls, status=status.HTTP_201_CREATED)
    
    
    
    
    @swagger_auto_schema(
        operation_description="🔒 Obtener todas las URLs acortadas del usuario autenticado o todas si es admin.",
        responses={200: ShortenedURLResponseSerializer(many=True)},
        tags=["Gestión de URLs Acortadas"],
    )
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ShortenedURL.objects.none()

        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                return ShortenedURL.objects.all()  # ✅ Devuelve todas las URLs (incluso las que no tienen dueño)
            return ShortenedURL.objects.filter(owner=self.request.user)  # Usuarios normales solo ven sus URLs
        return ShortenedURL.objects.none()

    @swagger_auto_schema(
    operation_description="🔒 Crear una nueva URL acortada (Usuario autenticado).",
    request_body=ShortenedURLSerializer,  # ✅ Esto define correctamente la entrada
    responses={201: openapi.Schema(  # ✅ Define correctamente la salida en Swagger
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de la URL acortada'),
            'short_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL acortada generada'),
        },
    )},
    tags=["Gestión de URLs Acortadas"],
)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()  # 🔹 Ya no es necesario pasar owner aquí, el serializador lo maneja
        short_url = request.build_absolute_uri(f"/r/{instance.short_code}")
        return Response({"id": instance.id, "short_url": short_url}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="🔐 Actualizar la URL original sin modificar la URL acortada (Solo admin o dueño).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'original_url': openapi.Schema(type=openapi.TYPE_STRING, description='Nueva URL original'),
            },
            required=['original_url'],
        ),
        responses={200: "URL actualizada con éxito"},
        tags=["Gestión de URLs Acortadas"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="🔐 Modificar parcialmente la URL (ej. cambiar privacidad, Solo admin o dueño).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'is_private': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Marcar como privada o pública'),
            },
            required=['is_private'],
        ),
        responses={200: "Actualización parcial exitosa"},
        tags=["Gestión de URLs Acortadas"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
