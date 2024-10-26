# main.py
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from enum import Enum
import httpx

app = FastAPI()

# Configuração do cliente HTTP
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:3000")  # Alterado para 'backend'

# Modelos Pydantic
class Status(int, Enum):
    Pending = 0
    InProgress = 1
    Resolved = 2

class Ticket(BaseModel):
    id: Optional[int] = Field(default=None, alias="ID")
    titulo: str = Field(alias="Titulo")
    descricao: str = Field(alias="Descricao")
    prioridade: int = Field(alias="Prioridade")
    id_pessoa: Optional[int] = Field(default=None, alias="ID_pessoa")
    status: Status = Field(default=Status.Pending, alias="Status")

    class Config:
        allow_population_by_field_name = True

class Pessoa(BaseModel):
    id: Optional[int] = Field(default=None, alias="ID")
    login: str = Field(alias="Login")
    senha: str = Field(alias="Senha")
    adm: bool = Field(default=False, alias="ADM")

    class Config:
        allow_population_by_field_name = True

# Cliente HTTP assíncrono
async def get_http_client():
    async with httpx.AsyncClient(base_url=BACKEND_URL) as client:
        yield client

# Endpoints

# 1. Retornar lista de tickets abertos, ordenados por prioridade (maior primeiro)
@app.get("/tickets/open", response_model=List[Ticket])
async def get_open_tickets(client: httpx.AsyncClient = Depends(get_http_client)):
    print("\n[GET /tickets/open] Enviando requisição GET para o backend:")
    print(f"URL: {BACKEND_URL}/tickets/abertos")
    response = await client.get("/tickets/abertos")
    print("[GET /tickets/open] Resposta recebida do backend:")
    print(f"Código de status: {response.status_code}")
    print(f"Conteúdo da resposta: {response.text}\n")
    if response.status_code == 200:
        tickets_data = response.json()
        tickets = [Ticket(**item) for item in tickets_data]
        # Ordenar por prioridade decrescente
        tickets_sorted = sorted(tickets, key=lambda x: x.prioridade, reverse=True)
        return tickets_sorted
    raise HTTPException(status_code=response.status_code, detail="Erro ao obter tickets abertos")

# 2. Criar um usuário com validação
@app.post("/register")
async def create_user(pessoa: Pessoa, client: httpx.AsyncClient = Depends(get_http_client)):
    # Verificar se o usuário já existe
    print("\n[POST /register] Verificando se o usuário existe:")
    print(f"GET {BACKEND_URL}/usuarios/login/{pessoa.login}")
    response = await client.get(f"/usuarios/login/{pessoa.login}")
    print(f"Código de status: {response.status_code}")
    print(f"Conteúdo da resposta: {response.text}\n")
    if response.status_code == 200:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    elif response.status_code != 204:
        # Se o status não for 204 (No Content), pode indicar um erro
        raise HTTPException(status_code=response.status_code, detail="Erro ao verificar usuário")
    # Criar o usuário
    user_data = pessoa.dict(by_alias=True)
    print("[POST /register] Criando novo usuário:")
    print(f"POST {BACKEND_URL}/usuarios")
    print(f"Dados enviados: {user_data}")
    response = await client.post("/usuarios", json=user_data)
    print(f"Código de status: {response.status_code}")
    print(f"Conteúdo da resposta: {response.text}\n")
    if response.status_code == 201:
        return {"message": "Usuário criado com sucesso"}
    raise HTTPException(status_code=response.status_code, detail="Erro ao criar usuário")

# 3. Autenticar usuário e retornar dados
@app.post("/login")
async def authenticate_user(login: str, senha: str, client: httpx.AsyncClient = Depends(get_http_client)):
    print("\n[POST /login] Autenticando usuário:")
    print(f"GET {BACKEND_URL}/usuarios/login/{login}")
    response = await client.get(f"/usuarios/login/{login}")
    print(f"Código de status: {response.status_code}")
    print(f"Conteúdo da resposta: {response.text}\n")
    if response.status_code == 200:
        pessoa_data = response.json()
        pessoa = Pessoa(**pessoa_data)
        if pessoa.senha == senha:
            return pessoa
        else:
            raise HTTPException(status_code=401, detail="Senha incorreta")
    elif response.status_code == 204:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    else:
        raise HTTPException(status_code=response.status_code, detail="Erro ao autenticar usuário")

# 4. Atribuir um ticket a um usuário e atualizar o status
@app.put("/tickets/assign")
async def assign_ticket(ticket_id: int, user_id: int, client: httpx.AsyncClient = Depends(get_http_client)):
    print("\n[PUT /tickets/assign] Atribuindo ticket:")
    print(f"Obtendo ticket {ticket_id}")
    print(f"GET {BACKEND_URL}/tickets/{ticket_id}")
    response = await client.get(f"/tickets/{ticket_id}")
    print(f"Código de status: {response.status_code}")
    print(f"Conteúdo da resposta: {response.text}\n")
    if response.status_code == 200:
        ticket_data = response.json()
        ticket_data["ID_pessoa"] = user_id
        ticket_data["Status"] = Status.InProgress.value
        print("Atualizando ticket com novos dados:")
        print(f"PUT {BACKEND_URL}/tickets/{ticket_id}")
        print(f"Dados enviados: {ticket_data}")
        update_response = await client.put(f"/tickets/{ticket_id}", json=ticket_data)
        print(f"Código de status: {update_response.status_code}")
        print(f"Conteúdo da resposta: {update_response.text}\n")
        if update_response.status_code == 200:
            return {"message": "Ticket atribuído com sucesso"}
        else:
            raise HTTPException(status_code=update_response.status_code, detail="Erro ao atualizar ticket")
    else:
        raise HTTPException(status_code=response.status_code, detail="Ticket não encontrado")

# 5. Ver todos os tickets atribuídos a um usuário
@app.get("/tickets/user/{user_id}", response_model=List[Ticket])
async def get_tickets_by_user(user_id: int, client: httpx.AsyncClient = Depends(get_http_client)):
    print(f"\n[GET /tickets/user/{user_id}] Obtendo tickets atribuídos ao usuário {user_id}")
    print(f"GET {BACKEND_URL}/tickets/usuario/{user_id}")
    response = await client.get(f"/tickets/usuario/{user_id}")
    print(f"Código de status: {response.status_code}")
    print(f"Conteúdo da resposta: {response.text}\n")
    if response.status_code == 200:
        tickets_data = response.json()
        tickets = [Ticket(**item) for item in tickets_data]
        return tickets
    raise HTTPException(status_code=response.status_code, detail="Erro ao obter tickets do usuário")

# 6. Mostrar todos os tickets, independente do status
@app.get("/tickets", response_model=List[Ticket])
async def get_all_tickets(client: httpx.AsyncClient = Depends(get_http_client)):
    print("\n[GET /tickets] Obtendo todos os tickets")
    print(f"GET {BACKEND_URL}/tickets")
    response = await client.get("/tickets")
    print(f"Código de status: {response.status_code}")
    print(f"Conteúdo da resposta: {response.text}\n")
    if response.status_code == 200:
        tickets_data = response.json()
        tickets = [Ticket(**item) for item in tickets_data]
        return tickets
    raise HTTPException(status_code=response.status_code, detail="Erro ao obter tickets")

# 7. Criar um ticket
@app.post("/tickets")
async def create_ticket(ticket: Ticket, client: httpx.AsyncClient = Depends(get_http_client)):
    # Excluir campos não necessários para a criação
    ticket_data = ticket.dict(by_alias=True, exclude_unset=True)
    # Definir status inicial como Pending (0)
    ticket_data["Status"] = Status.Pending.value
    print("\n[POST /tickets] Criando novo ticket:")
    print(f"POST {BACKEND_URL}/tickets")
    print(f"Dados enviados: {ticket_data}")
    response = await client.post("/tickets", json=ticket_data)
    print(f"Código de status: {response.status_code}")
    print(f"Conteúdo da resposta: {response.text}\n")
    if response.status_code == 201:
        return {"message": "Ticket criado com sucesso"}
    raise HTTPException(status_code=response.status_code, detail="Erro ao criar ticket")

# 8. Finalizar ticket (status = 2)
@app.put("/tickets/complete/{ticket_id}")
async def complete_ticket(ticket_id: int, client: httpx.AsyncClient = Depends(get_http_client)):
    print(f"\n[PUT /tickets/complete/{ticket_id}] Finalizando ticket {ticket_id}")
    print(f"Obtendo ticket {ticket_id}")
    print(f"GET {BACKEND_URL}/tickets/{ticket_id}")
    response = await client.get(f"/tickets/{ticket_id}")
    print(f"Código de status: {response.status_code}")
    print(f"Conteúdo da resposta: {response.text}\n")
    if response.status_code == 200:
        ticket_data = response.json()
        ticket_data["Status"] = Status.Resolved.value
        print("Atualizando ticket com novo status:")
        print(f"PUT {BACKEND_URL}/tickets/{ticket_id}")
        print(f"Dados enviados: {ticket_data}")
        update_response = await client.put(f"/tickets/{ticket_id}", json=ticket_data)
        print(f"Código de status: {update_response.status_code}")
        print(f"Conteúdo da resposta: {update_response.text}\n")
        if update_response.status_code == 200:
            return {"message": "Ticket finalizado com sucesso"}
        else:
            raise HTTPException(status_code=update_response.status_code, detail="Erro ao atualizar ticket")
    else:
        raise HTTPException(status_code=response.status_code, detail="Ticket não encontrado")
