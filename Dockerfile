FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
ENV ARENA_RUNS_DIR=/data/runs
VOLUME ["/data/runs"]
EXPOSE 8000
CMD ["uvicorn", "agent_arena.api:app", "--host", "0.0.0.0", "--port", "8000"]
