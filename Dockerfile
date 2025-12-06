FROM python:3.11-slim


WORKDIR /app


# Install system deps
RUN apt-get update && apt-get install -y \
build-essential \
libpq-dev \
&& rm -rf /var/lib/apt/lists/*


# Install Poetry
RUN pip install poetry


COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi


COPY . .


EXPOSE 8000


CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]