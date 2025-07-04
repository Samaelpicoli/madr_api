# 📚 MADR - Meu Acervo Digital de Romances

MADR é uma API desenvolvida com [FastAPI](https://fastapi.tiangolo.com/) para gerenciar um acervo digital de romances, permitindo cadastro, consulta, atualização e remoção de autores, livros e contas de usuários. O projeto utiliza autenticação JWT, banco de dados PostgreSQL, arquitetura assíncrona e está pronto para uso com Docker. O software foi desenvolvido como projeto de conclusão do curso [FastAPI do Zero](https://fastapidozero.dunossauro.com/estavel/) do canal [Eduardo Mendes](https://www.youtube.com/@dunossauro). 

---

## 🚀 Tecnologias Utilizadas

- **[FastAPI](https://fastapi.tiangolo.com/):** Framework web Python, rápido e assíncrono para APIs.
- **[SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html):** ORM assíncrono para manipulação do banco de dados.
- **[PostgreSQL](https://www.postgresql.org/):** Banco de dados relacional robusto.
- **[Docker](https://www.docker.com/):** Containerização da aplicação e banco de dados.
- **[PyJWT](https://pyjwt.readthedocs.io/):** Geração e validação de tokens JWT.
- **[Pydantic](https://docs.pydantic.dev/):** Validação e serialização de dados.
- **[pytest](https://docs.pytest.org/):** Testes automatizados.
- **[ruff](https://docs.astral.sh/ruff/):** Linter e formatador de código.

---

## 🗂️ Modelagem de Dados

### Conta de Usuário (`Account`)
- `id`: int
- `username`: str (único)
- `email`: str (único)
- `password`: str (hash)
- `created_at`: datetime
- `updated_at`: datetime

### Autor (`Author`)
- `id`: int
- `name`: str (único)
- `created_at`: datetime
- `updated_at`: datetime
- `books`: lista de livros associados - referência a `Book` (objeto relacionado)

### Livro (`Book`)
- `id`: int
- `title`: str (único)
- `year`: int
- `author_id`: int - referência ao autor
- `author`: Autor (objeto relacionado)
- `created_at`: datetime
- `updated_at`: datetime

---

## 🔒 Autenticação & Token JWT

A autenticação é feita via OAuth2 com JWT. O usuário obtém um token de acesso ao fazer login, que deve ser enviado no header `Authorization: Bearer <token>` para acessar rotas protegidas.

- **Endpoint de login:** `POST /auth/token`
- **Endpoint de refresh:** `POST /auth/refresh/token`

Exemplo de resposta:
```json
{
  "access_token": "<jwt_token>",
  "token_type": "Bearer"
}
```

---

## 🌐 Principais Rotas

### 📖 Livros

- `POST /books/` — Cria um novo livro (autenticado)
- `GET /books/` — Lista livros, com filtros por título e ano (autenticado)
- `GET /books/{book_id}` — Detalha um livro (autenticado)
- `PATCH /books/{book_id}` — Atualiza dados do livro (autenticado)
- `DELETE /books/{book_id}` — Remove um livro (autenticado)

### 👤 Autores

- `POST /authors/` — Cria um novo autor (autenticado)
- `GET /authors/` — Lista autores, com filtro por nome (autenticado)
- `GET /authors/{author_id}` — Detalha um autor (autenticado)
- `PATCH /authors/{author_id}` — Atualiza dados do autor (autenticado)
- `DELETE /authors/{author_id}` — Remove um autor (autenticado)

### 🧑 Contas

- `POST /accounts/` — Cria uma nova conta de usuário
- `GET /accounts/{account_id}` — Detalha uma conta (autenticado)
- `PUT /accounts/{account_id}` — Atualiza dados da conta (autenticado)
- `DELETE /accounts/{account_id}` — Remove uma conta (autenticado)

### 🔑 Autenticação

- `POST /auth/token` — Gera token de acesso
- `POST /auth/refresh/token` — Gera novo token de acesso

### 🏠 Endpoints Públicos

- `GET /` — Mensagem "Hello World!"
- `GET /hello` — Página HTML simples

---

## ⚡ Uso de Async

Toda a comunicação com o banco de dados é feita de forma assíncrona usando `async def` e `AsyncSession` do SQLAlchemy, garantindo alta performance e escalabilidade.

---

## 🐳 Docker

O projeto já está pronto para rodar com Docker, incluindo banco de dados PostgreSQL:

```sh
docker-compose up --build
```

- A aplicação estará disponível em `http://localhost:8000`
- O banco de dados estará disponível na porta `5434`

---

## 🧪 Testes

Os testes automatizados cobrem rotas, autenticação, regras de negócio e integração com o banco de dados. Para rodar os testes:

```sh
task test
```
ou
```sh
pytest -s -x --cov=madr -vv
```

- Cobertura de testes é gerada em `htmlcov/`
- Factories e fixtures garantem isolamento e reprodutibilidade dos testes

---

## 📦 Estrutura do Projeto

```
madr/
│
├── madr/
│   ├── app.py
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── security/
│   ├── settings/
│   └── utils/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── pyproject.toml
├── README.md
└── ...
```

---

## Desenvolvido por

Samael Muniz Picoli

---