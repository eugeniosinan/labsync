# Usar imagem base oficial do Python
FROM python:3.9-slim

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar todos os arquivos do projeto para dentro do container
COPY . .

# Definir as variáveis de ambiente, você pode adicionar mais se necessário
# Para valores dinâmicos, eles serão passados via docker-compose.yml
ARG FLASK_SECRET_KEY
ARG DATABASE_URL

# Definir as variáveis de ambiente do Flask diretamente no container
ENV FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
ENV DATABASE_URL=${DATABASE_URL}

# Instalar as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta 5000 (a porta interna do Flask)
EXPOSE 5000

# Comando para rodar o Flask no container
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
