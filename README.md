
#Para iniciar

docker-compose up --build  

# API de Tickets e Usuários

Este projeto fornece uma API para gerenciar tickets e usuários, permitindo a criação, atualização e visualização de tickets e a criação e autenticação de usuários.

## Endpoints Disponíveis

### 1. Retornar Lista de Tickets Abertos
- **URL**: `/tickets/open`
- **Método HTTP**: `GET`
- **Descrição**: Retorna uma lista de tickets com status "aberto" (`status = 0`), ordenados por prioridade decrescente.
- **Resposta**:
  - `200 OK`: Lista de tickets abertos.
  - **Erro**: Código de status HTTP correspondente e mensagem de erro.

---

### 2. Criar um Usuário
- **URL**: `/register`
- **Método HTTP**: `POST`
- **Descrição**: Cria um novo usuário após verificar se o login já não está em uso.
- **Corpo da Requisição (JSON)**:
  ```json
  {
    "Login": "nome_do_usuario",
    "Senha": "senha_segura",
    "ADM": false
  }
  ```
- **Resposta**:
  - `200 OK`: Mensagem de sucesso.
  - `400 Bad Request`: Usuário já existe.
  - **Erro**: Código de status HTTP correspondente e mensagem de erro.

---

### 3. Autenticar Usuário
- **URL**: `/login`
- **Método HTTP**: `POST`
- **Descrição**: Autentica um usuário com base no login e senha fornecidos.
- **Corpo da Requisição (JSON)**:
  ```json
  {
    "login": "nome_do_usuario",
    "senha": "senha_segura"
  }
  ```
- **Resposta**:
  - `200 OK`: Dados do usuário autenticado.
  - `401 Unauthorized`: Credenciais inválidas.
  - **Erro**: Código de status HTTP correspondente e mensagem de erro.

---

### 4. Atribuir um Ticket a um Usuário
- **URL**: `/tickets/assign`
- **Método HTTP**: `PUT`
- **Descrição**: Atribui um ticket a um usuário e atualiza o status para "em andamento" (`status = 1`).
- **Parâmetros de Consulta (Query Parameters)**:
  - `ticket_id`: ID do ticket a ser atribuído.
  - `user_id`: ID do usuário ao qual o ticket será atribuído.
- **Resposta**:
  - `200 OK`: Mensagem de sucesso.
  - **Erro**: Código de status HTTP correspondente e mensagem de erro.

---

### 5. Ver Tickets Atribuídos a um Usuário
- **URL**: `/tickets/user/{user_id}`
- **Método HTTP**: `GET`
- **Descrição**: Retorna todos os tickets atribuídos a um usuário específico.
- **Parâmetros da URL**:
  - `user_id`: ID do usuário.
- **Resposta**:
  - `200 OK`: Lista de tickets do usuário.
  - **Erro**: Código de status HTTP correspondente e mensagem de erro.

---

### 6. Mostrar Todos os Tickets
- **URL**: `/tickets`
- **Método HTTP**: `GET`
- **Descrição**: Retorna todos os tickets, independentemente do status.
- **Resposta**:
  - `200 OK`: Lista de todos os tickets.
  - **Erro**: Código de status HTTP correspondente e mensagem de erro.

---

### 7. Criar um Ticket
- **URL**: `/tickets`
- **Método HTTP**: `POST`
- **Descrição**: Cria um novo ticket.
- **Corpo da Requisição (JSON)**:
  ```json
  {
    "Titulo": "Título do Ticket",
    "Descricao": "Descrição detalhada do problema",
    "Prioridade": 1
  }
  ```
- **Resposta**:
  - `200 OK`: Mensagem de sucesso.
  - **Erro**: Código de status HTTP correspondente e mensagem de erro.

---

### 8. Finalizar um Ticket
- **URL**: `/tickets/complete/{ticket_id}`
- **Método HTTP**: `PUT`
- **Descrição**: Finaliza um ticket, alterando o status para "completo" (`status = 2`).
- **Parâmetros da URL**:
  - `ticket_id`: ID do ticket a ser finalizado.
- **Resposta**:
  - `200 OK`: Mensagem de sucesso.
  - **Erro**: Código de status HTTP correspondente e mensagem de erro.

---

## Observações

- Para endpoints que requerem parâmetros na URL, substitua `{parametro}` pelo valor apropriado.
- Certifique-se de enviar as requisições no formato JSON, conforme descrito.
- As respostas de erro retornarão um código HTTP correspondente e uma mensagem explicativa.

---

## Licença

Este projeto é licenciado sob a [MIT License](LICENSE).
