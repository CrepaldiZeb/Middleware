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

# (restante do código permanece o mesmo)


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
    response = await client.get("/tickets/abertos")
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
    response = await client.get(f"/usuarios/login/{pessoa.login}")
    if response.status_code == 200:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    elif response.status_code != 204:
        # Se o status não for 204 (No Content), pode indicar um erro
        raise HTTPException(status_code=response.status_code, detail="Erro ao verificar usuário")
    # Criar o usuário
    response = await client.post("/usuarios", json=pessoa.dict(by_alias=True))
    if response.status_code == 201:
        return {"message": "Usuário criado com sucesso"}
    raise HTTPException(status_code=response.status_code, detail="Erro ao criar usuário")

# 3. Autenticar usuário e retornar dados
@app.post("/login")
async def authenticate_user(login: str, senha: str, client: httpx.AsyncClient = Depends(get_http_client)):
    response = await client.get(f"/usuarios/login/{login}")
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
    # Obter o ticket atual
    response = await client.get(f"/tickets/{ticket_id}")
    if response.status_code == 200:
        ticket_data = response.json()
        ticket_data["ID_pessoa"] = user_id
        ticket_data["Status"] = Status.InProgress.value
        # Atualizar o ticket
        update_response = await client.put(f"/tickets/{ticket_id}", json=ticket_data)
        if update_response.status_code == 200:
            return {"message": "Ticket atribuído com sucesso"}
        else:
            raise HTTPException(status_code=update_response.status_code, detail="Erro ao atualizar ticket")
    else:
        raise HTTPException(status_code=response.status_code, detail="Ticket não encontrado")

# 5. Ver todos os tickets atribuídos a um usuário
@app.get("/tickets/user/{user_id}", response_model=List[Ticket])
async def get_tickets_by_user(user_id: int, client: httpx.AsyncClient = Depends(get_http_client)):
    response = await client.get(f"/tickets/usuario/{user_id}")
    if response.status_code == 200:
        tickets_data = response.json()
        tickets = [Ticket(**item) for item in tickets_data]
        return tickets
    raise HTTPException(status_code=response.status_code, detail="Erro ao obter tickets do usuário")

# 6. Mostrar todos os tickets, independente do status
@app.get("/tickets", response_model=List[Ticket])
async def get_all_tickets(client: httpx.AsyncClient = Depends(get_http_client)):
    response = await client.get("/tickets")
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
    response = await client.post("/tickets", json=ticket_data)
    if response.status_code == 201:
        return {"message": "Ticket criado com sucesso"}
    raise HTTPException(status_code=response.status_code, detail="Erro ao criar ticket")

# 8. Finalizar ticket (status = 2)
@app.put("/tickets/complete/{ticket_id}")
async def complete_ticket(ticket_id: int, client: httpx.AsyncClient = Depends(get_http_client)):
    # Obter o ticket atual
    response = await client.get(f"/tickets/{ticket_id}")
    if response.status_code == 200:
        ticket_data = response.json()
        ticket_data["Status"] = Status.Resolved.value
        # Atualizar o ticket
        update_response = await client.put(f"/tickets/{ticket_id}", json=ticket_data)
        if update_response.status_code == 200:
            return {"message": "Ticket finalizado com sucesso"}
        else:
            raise HTTPException(status_code=update_response.status_code, detail="Erro ao atualizar ticket")
    else:
        raise HTTPException(status_code=response.status_code, detail="Ticket não encontrado")
