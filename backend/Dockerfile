# Utilizando uma imagem base do Python
FROM python:3.9-slim

# Instalando Git e SQLite3
RUN apt-get update && apt-get install -y git sqlite3

# Definindo o diretório de trabalho
WORKDIR /app

# Clonando o repositório do GitHub
RUN git clone https://github.com/CrepaldiZeb/Back-Cloud.git /app

# Instalando dependências Python
RUN pip install Flask

# Executando script SQL para criar o banco de dados
RUN sqlite3 data.db < script.sql

# Expondo a porta 3000 para o Flask
EXPOSE 3000

# Iniciando a aplicação Flask
CMD ["python", "api.py"]
