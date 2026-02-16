FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1   PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
git \
postgresql-client \
build-essential \
libpq-dev \
&& rm -rf /var/lib/apt/lists/*

COPY ./backend/requirements.txt .

RUN ls -lah

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./backend .

COPY ./docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh



EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
