"""
Os serializers fazem a ponte entre os models (Python) e o JSON da API.

Eles têm duas tarefas:
1. Validar os dados que chegam (ex.: o título é obrigatório?).
2. Transformar o objeto em JSON na hora de responder.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Task

Usuario = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Os dados do usuário que a API devolve. Repare: a senha nunca aparece."""

    class Meta:
        model = Usuario
        fields = ["id", "username", "email"]


class RegisterSerializer(serializers.ModelSerializer):
    """Valida e cria uma conta nova."""

    password = serializers.CharField(
        write_only=True,
        min_length=6,
        style={"input_type": "password"},
        help_text="Mínimo de 6 caracteres.",
    )

    class Meta:
        model = Usuario
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        # create_user guarda a senha criptografada, nunca em texto puro.
        return Usuario.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Os dois campos necessários para entrar na API."""

    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )


class TokenResponseSerializer(serializers.Serializer):
    """O que a API devolve depois do cadastro ou do login.

    O "user" vem primeiro e traz o username em texto puro. O "token" é a
    chave de acesso: aquela string longa que começa com "eyJ" (não é o
    username). Ela deve ser guardada e enviada nas próximas chamadas, no
    cabeçalho: Authorization: Bearer <token>
    """

    user = UserSerializer(read_only=True)
    token = serializers.CharField(
        read_only=True,
        help_text=(
            "Chave de acesso (não é o username). Envie nas outras chamadas: "
            "Authorization: Bearer <token>"
        ),
    )


class TaskSerializer(serializers.ModelSerializer):
    """Uma tarefa, com os campos que podem ser lidos e escritos."""

    class Meta:
        model = Task
        fields = ["id", "title", "description", "done", "created_at"]
        # Estes dois são preenchidos pelo servidor: o aluno não os envia.
        read_only_fields = ["id", "created_at"]
