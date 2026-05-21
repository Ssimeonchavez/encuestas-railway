FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update \
	&& apt-get install -y build-essential libssl-dev libffi-dev cargo \
	&& rm -rf /var/lib/apt/lists/* \
	&& pip install --no-cache-dir -r requirements.txt \
	&& apt-get remove -y build-essential cargo \
	&& apt-get autoremove -y \
	&& rm -rf /var/lib/apt/lists/*

COPY . .

# Railway asigna el puerto automáticamente via variable PORT
ENV PORT=5000
EXPOSE 5000

CMD gunicorn --bind 0.0.0.0:$PORT run:app