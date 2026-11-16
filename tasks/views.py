"""
As views são o cérebro da API: recebem a requisição, conversam com o banco
de dados e devolvem a resposta em JSON.

O arquivo tem duas partes:
1. Autenticação: cadastro e login.
2. Tarefas: o CRUD completo da lista.
"""

from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .models import Task
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    TaskSerializer,
    TokenResponseSerializer,
    UserSerializer,
)

Usuario = get_user_model()


# ======================================================================
# 1. AUTENTICAÇÃO
# ======================================================================
@extend_schema(tags=["Autenticação"])
class RegisterView(APIView):
    """Cria uma conta nova e já devolve o token.

    Assim o front-end não precisa fazer o login logo depois do cadastro.
    """

    # Qualquer pessoa pode se cadastrar, mesmo sem estar logada.
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: TokenResponseSerializer},
        summary="Criar conta",
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        # Se algum campo estiver errado, o DRF responde 400 com os detalhes.
        serializer.is_valid(raise_exception=True)

        usuario = serializer.save()

        # O token é o "crachá" que o front-end vai guardar e enviar depois.
        token = AccessToken.for_user(usuario)

        return Response(
            {"token": str(token), "user": UserSerializer(usuario).data},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Autenticação"])
class LoginView(APIView):
    """Confere usuário e senha e devolve o token."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: TokenResponseSerializer},
        summary="Entrar (login)",
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # O authenticate compara a senha digitada com a senha criptografada.
        usuario = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if usuario is None:
            return Response(
                {"detail": "Usuário ou senha inválidos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = AccessToken.for_user(usuario)

        return Response({"token": str(token), "user": UserSerializer(usuario).data})


# ======================================================================
# 2. TAREFAS (CRUD)
# ======================================================================
@extend_schema(tags=["Tarefas"])
class TaskViewSet(viewsets.ModelViewSet):
    """CRUD completo das tarefas.

    O ModelViewSet já entrega de uma vez as cinco operações:

        GET    /api/tasks/         listar as minhas tarefas
        POST   /api/tasks/         criar uma tarefa
        GET    /api/tasks/<id>/    ver uma tarefa
        PUT    /api/tasks/<id>/    atualizar tudo
        PATCH  /api/tasks/<id>/    atualizar só o que for enviado
        DELETE /api/tasks/<id>/    apagar

    Cada usuário só enxerga as próprias tarefas.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Quando o Swagger monta a documentação, não existe usuário logado.
        # Esta linha evita um erro nesse momento.
        if getattr(self, "swagger_fake_view", False):
            return Task.objects.none()

        # Aqui está o segredo: filtramos pelo dono. Assim um aluno nunca vê
        # a tarefa do outro.
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # O dono é sempre quem está logado. O aluno não escolhe isso pelo
        # JSON, e é por isso que o campo "owner" não aparece no serializer.
        serializer.save(owner=self.request.user)
