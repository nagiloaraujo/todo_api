# API de Tarefas (TO-DO)

API REST simplificada de lista de tarefas, criada como **avaliação final da turma**.
Ela é propositalmente pequena: **1 app**, **1 modelo** e **poucos endpoints**, para
que qualquer aluno consiga ler o código inteiro e entender como uma API funciona.

Recursos usados:

| Biblioteca | Para que serve |
|---|---|
| Django 5 | framework web |
| Django REST Framework | transforma os models em uma API JSON |
| SimpleJWT | gera o token devolvido no login |
| django-cors-headers | deixa o front-end (outra porta) acessar a API |
| drf-spectacular | documentação automática (Swagger / ReDoc) |

O banco é o **SQLite**: um único arquivo (`db.sqlite3`) criado na pasta do projeto.
Não é preciso instalar nem configurar banco de dados.

---

## API publicada na nuvem (demo)

A mesma API também está publicada, de graça, no **Render**. É o código deste
repositório rodando na internet — só muda o endereço.

| Ambiente | Endereço base |
|---|---|
| Local (seu computador) | `http://127.0.0.1:8000` |
| Nuvem (Render) | `https://todo-api-0hhb.onrender.com` |

Documentação interativa online:

- **Swagger UI:** https://todo-api-0hhb.onrender.com/api/docs/
- **ReDoc:** https://todo-api-0hhb.onrender.com/api/redoc/
- **Schema OpenAPI:** https://todo-api-0hhb.onrender.com/api/schema/
- **Código-fonte (GitHub):** https://github.com/nagiloaraujo/todo_api

> **Avisos do plano gratuito:**
> - O serviço "dorme" depois de cerca de 15 minutos sem uso. A primeira chamada
>   pode demorar 30-50 segundos para "acordar" — é normal, basta tentar de novo.
> - O banco é o SQLite e, na nuvem, é **temporário**: cada novo deploy recomeça
>   com o banco zerado. Serve para demonstração, não para guardar dados reais.
> - Para testar online, use o mesmo roteiro do Swagger trocando apenas o
>   endereço local pelo endereço da nuvem.

---

## 1. Estrutura de pastas

```
todo_api/
├── manage.py               # comandos do Django (migrate, runserver...)
├── requirements.txt        # bibliotecas necessárias
├── db.sqlite3              # banco de dados (criado ao rodar "migrate")
├── todo/                   # configuração do projeto
│   ├── settings.py         # painel central (banco, autenticação, CORS...)
│   ├── urls.py             # rotas principais (/api/..., /api/docs/...)
│   ├── wsgi.py / asgi.py   # arquivos de inicialização
└── tasks/                  # o NOSSO app (tudo o que interessa está aqui)
    ├── models.py           # modelo Task (uma tarefa da lista)
    ├── serializers.py      # validação e conversão para JSON
    ├── views.py            # cadastro, login e CRUD das tarefas
    ├── urls.py             # rotas do app (/api/tasks/...)
    ├── admin.py            # tarefas visíveis no /admin/
    └── migrations/         # histórico do banco
```

---

## 2. Como executar (passo a passo)

Pré-requisito: ter o **Python 3.10+** instalado.

Abra o terminal **na pasta do projeto** (`todo_api`) e rode:

```powershell
# 1) Criar o ambiente virtual (só na primeira vez)
python -m venv venv

# 2) Ativar o ambiente virtual
#    Windows PowerShell:
.\venv\Scripts\Activate.ps1
#    (se der erro de política, rode antes: Set-ExecutionPolicy -Scope Process RemoteSigned)
#    Linux/Mac:  source venv/bin/activate

# 3) Instalar as bibliotecas
pip install -r requirements.txt

# 4) Criar as tabelas no banco
python manage.py migrate

# 5) Ligar o servidor
python manage.py runserver
```

O servidor sobe em **http://127.0.0.1:8000**.

Acesse a documentação interativa (Swagger) em:

**http://127.0.0.1:8000/api/docs/**

> Observação (Windows + Python 3.15): se o `pip install` reclamar do PyYAML
> querendo compilar C++, rode antes:
> `$env:PYYAML_FORCE_LIBYAML="0"; pip install pyyaml`

---

## 3. Autenticação (simplificada, de propósito)

O fluxo tem **duas etapas**:

1. O aluno **cria a conta** (`POST /api/register/`) **ou** faz **login** (`POST /api/login/`).
2. A API devolve um **token**. O front-end guarda esse token no `localStorage`
   e o envia em todas as requisições seguintes.

O token **vale 30 dias** e **não tem "refresh"**. Ou seja: o aluno faz o login
**uma única vez** e continua logado — se quiser sair, basta apagar o token do
`localStorage`. É uma simplificação consciente para a aula (uma API de produção
usaria refresh token e tempo de vida curto).

**Como o token é enviado** — no cabeçalho `Authorization`:

```
Authorization: Bearer <cole-o-token-aqui>
```

---

## 4. Endpoints

Base: `http://127.0.0.1:8000`

| Método | Rota | Precisa de token? | O que faz |
|---|---|---|---|
| POST | `/api/register/` | não | cria a conta e devolve o token |
| POST | `/api/login/` | não | confere usuário/senha e devolve o token |
| GET | `/api/tasks/` | sim | lista as **minhas** tarefas |
| POST | `/api/tasks/` | sim | cria uma tarefa |
| GET | `/api/tasks/<id>/` | sim | vê uma tarefa |
| PUT | `/api/tasks/<id>/` | sim | atualiza **todos** os campos |
| PATCH | `/api/tasks/<id>/` | sim | atualiza **só** os campos enviados |
| DELETE | `/api/tasks/<id>/` | sim | apaga a tarefa |
| GET | `/api/schema/` | não | schema OpenAPI (JSON/YAML) |
| GET | `/api/docs/` | não | Swagger UI |
| GET | `/api/redoc/` | não | ReDoc |

**Regra de ouro:** cada usuário só enxerga, edita e apaga **as próprias tarefas**.
O campo `owner` é preenchido automaticamente pelo servidor (quem está logado).

### O objeto "tarefa"

| Campo | Tipo | Regras |
|---|---|---|
| `id` | inteiro | gerado pelo servidor (só leitura) |
| `title` | texto | **obrigatório**, até 200 caracteres |
| `description` | texto | opcional (pode ficar vazio) |
| `done` | booleano | `false` = pendente, `true` = concluída |
| `created_at` | data/hora | gerado pelo servidor (só leitura) |

---

## 5. Exemplos de requisição e resposta

### 5.1. Criar conta — `POST /api/register/`

Requisição:

```http
POST /api/register/
Content-Type: application/json

{
  "username": "ana",
  "email": "ana@teste.com",
  "password": "segredo123"
}
```

Resposta `201 Created`:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "ana",
    "email": "ana@teste.com"
  }
}
```

Se o usuário já existir → `400 Bad Request`:

```json
{ "username": ["Um usuário com este nome já existe."] }
```

### 5.2. Login — `POST /api/login/`

Requisição:

```http
POST /api/login/
Content-Type: application/json

{ "username": "ana", "password": "segredo123" }
```

Resposta `200 OK`:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": { "id": 1, "username": "ana", "email": "ana@teste.com" }
}
```

Senha errada → `401 Unauthorized`:

```json
{ "detail": "Usuário ou senha inválidos." }
```

### 5.3. Criar tarefa — `POST /api/tasks/`

Requisição (repare no cabeçalho `Authorization`):

```http
POST /api/tasks/
Authorization: Bearer eyJhbGciOi...cole-seu-token...
Content-Type: application/json

{
  "title": "Estudar Django",
  "description": "revisar o CRUD",
  "done": false
}
```

Resposta `201 Created`:

```json
{
  "id": 1,
  "title": "Estudar Django",
  "description": "revisar o CRUD",
  "done": false,
  "created_at": "2026-11-16T14:30:00-03:00"
}
```

### 5.4. Listar tarefas — `GET /api/tasks/`

```http
GET /api/tasks/
Authorization: Bearer <token>
```

Resposta `200 OK`:

```json
[
  {
    "id": 2,
    "title": "Comprar pão",
    "description": "",
    "done": true,
    "created_at": "2026-11-16T15:00:00-03:00"
  },
  {
    "id": 1,
    "title": "Estudar Django",
    "description": "revisar o CRUD",
    "done": false,
    "created_at": "2026-11-16T14:30:00-03:00"
  }
]
```

> As tarefas mais novas aparecem primeiro.

### 5.5. Ver uma tarefa — `GET /api/tasks/1/`

```http
GET /api/tasks/1/
Authorization: Bearer <token>
```

Resposta `200 OK`: o mesmo objeto do exemplo 5.3.

### 5.6. Atualizar (parcial) — `PATCH /api/tasks/1/`

Basta enviar o campo que mudou. Exemplo: marcar como concluída.

```http
PATCH /api/tasks/1/
Authorization: Bearer <token>
Content-Type: application/json

{ "done": true }
```

Resposta `200 OK`:

```json
{
  "id": 1,
  "title": "Estudar Django",
  "description": "revisar o CRUD",
  "done": true,
  "created_at": "2026-11-16T14:30:00-03:00"
}
```

### 5.7. Atualizar (completo) — `PUT /api/tasks/1/`

No `PUT` enviamos **todos** os campos editáveis:

```http
PUT /api/tasks/1/
Authorization: Bearer <token>
Content-Type: application/json

{ "title": "Estudar DRF", "description": "capítulo 3", "done": false }
```

### 5.8. Apagar — `DELETE /api/tasks/1/`

```http
DELETE /api/tasks/1/
Authorization: Bearer <token>
```

Resposta `204 No Content` (sem corpo). Depois disso, `GET /api/tasks/1/` responde `404`.

---

## 6. Testando sem front-end (alguns exemplos de terminal)

### PowerShell

```powershell
# Login e guarda o token na variável $token
$resposta = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/login/ `
  -ContentType "application/json" `
  -Body '{"username":"ana","password":"segredo123"}'
$token = $resposta.token

# Criar uma tarefa
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/tasks/ `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"title":"Estudar Django","description":"revisar o CRUD"}'

# Listar as tarefas
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/api/tasks/ `
  -Headers @{ Authorization = "Bearer $token" }
```

### curl

```bash
# Login
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"ana","password":"segredo123"}'

# Criar tarefa (troque <TOKEN> pelo valor devolvido no login)
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Estudar Django"}'
```

### Swagger (o jeito mais fácil em aula)

1. Abra **http://127.0.0.1:8000/api/docs/**.
2. Use `POST /api/login/` → **Try it out** → **Execute**.
3. Copie o valor de `token` da resposta.
4. Clique em **Authorize** (cadeado no topo) e cole o token → **Authorize**.
5. Agora qualquer endpoint de tarefas pode ser testado direto pela página.

---

## 7. Usando no front-end (guardando no localStorage)

O ponto central da autenticação simplificada: **o token fica no navegador**.

```javascript
// 1) LOGIN — guarda o token e o usuário
const resposta = await fetch("http://127.0.0.1:8000/api/login/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ username: "ana", password: "segredo123" }),
});
const dados = await resposta.json();

localStorage.setItem("token", dados.token);
localStorage.setItem("usuario", JSON.stringify(dados.user));

// 2) LISTAR as minhas tarefas — usa o token guardado
const token = localStorage.getItem("token");
const tarefas = await fetch("http://127.0.0.1:8000/api/tasks/", {
  headers: { Authorization: `Bearer ${token}` },
}).then((r) => r.json());

// 3) CRIAR uma tarefa
await fetch("http://127.0.0.1:8000/api/tasks/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({ title: "Nova tarefa" }),
});

// 4) SAIR — basta apagar o token
localStorage.removeItem("token");
```

Como o token dura 30 dias, ao reabrir a página o aluno continua logado
sem precisar digitar a senha de novo.

---

## 8. Tratamento de erros

A API responde sempre em JSON. Códigos mais comuns:

| Código | Quando acontece | Exemplo de corpo |
|---|---|---|
| `400` | dados inválidos ou faltando | `{"title": ["Este campo é obrigatório."]}` |
| `401` | sem token, token inválido ou login errado | `{"detail": "Usuário ou senha inválidos."}` |
| `404` | tarefa não existe (ou é de outro usuário) | `{"detail": "No Task matches the given query."}` |
| `204` | exclusão bem-sucedida (sem corpo) | — |

> Dica de aula: repare que a tarefa de outro usuário responde **404**, e não
> "403 proibido". Assim a API não revela nem que aquela tarefa existe.

---

## 9. Roteiro sugerido para a avaliação

1. `python manage.py runserver` e abrir `/api/docs/`.
2. Criar a conta em `POST /api/register/` e copiar o token.
3. Autorizar no Swagger e criar 2 ou 3 tarefas.
4. Listar, marcar uma como `done: true` (PATCH) e apagar outra (DELETE).
5. Fazer logout e login de novo em `POST /api/login/`.
6. (Opcional) Entrar com outra conta e mostrar que as tarefas **não** aparecem.
