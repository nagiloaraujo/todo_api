"""
Os models dizem como os dados ficam guardados no banco.

Neste projeto existe um único model: Task (uma tarefa da lista).
O usuário vem pronto do Django, não precisamos criar.
"""

from django.conf import settings
from django.db import models


class Task(models.Model):
    """Uma tarefa da lista: o item que o aluno cria, consulta, marca e apaga."""

    # Cada tarefa pertence a um usuário. É isso que impede um aluno de ver
    # (ou apagar) a tarefa do outro.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="dono",
    )

    title = models.CharField("título", max_length=200)

    # blank=True permite que a descrição fique vazia.
    description = models.TextField("descrição", blank=True, default="")

    # done = False significa "ainda não concluí".
    done = models.BooleanField("concluída", default=False)

    # auto_now_add preenche a data sozinho, na hora de criar.
    created_at = models.DateTimeField("criada em", auto_now_add=True)

    class Meta:
        # As mais novas aparecem primeiro na listagem.
        ordering = ["-created_at"]
        verbose_name = "tarefa"
        verbose_name_plural = "tarefas"

    def __str__(self):
        return self.title
