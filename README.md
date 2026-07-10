# Agent Evaluation Arena

Infraestructura reproducible para comparar agentes, modelos, prompts y herramientas sobre las mismas tareas y con presupuestos equivalentes.

![Python](https://img.shields.io/badge/Python-3.12-3776AB) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688) ![Next.js](https://img.shields.io/badge/Next.js-16-black) ![License](https://img.shields.io/badge/license-MIT-c7ff5e)

## Qué incluye

- Suites y datasets versionados, con graders determinísticos (`exact_match`, `contains`, `regex`).
- Presupuestos explícitos de pasos, tokens y tiempo; un leaderboard nunca mezcla presupuestos.
- Versiones de dataset, runner, grader, modelo y prompt registradas en cada resultado.
- Semillas persistidas, trazas ordenadas y replay completo sin credenciales.
- Ranking por éxito, costo y latencia con intervalos de confianza Wilson al 95%.
- API FastAPI documentada en OpenAPI y dashboard responsive en Next.js.
- Store append-only en JSON, sencillo de auditar y reemplazar por PostgreSQL.

## Inicio rápido

Requiere Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn agent_arena.api:app --reload
```

La API queda en `http://localhost:8000` y su documentación en `http://localhost:8000/docs`.

En otra terminal:

```bash
cd web
npm install
npm run dev
```

El dashboard queda en `http://localhost:3000`. También se puede levantar todo con `docker compose up --build`.

## Ejecutar una evaluación

El runner inicial usa respuestas fixture para mantener el ejemplo determinístico y sin acceso de red. Los adapters de proveedores pueden implementarse detrás de la misma frontera, manteniendo generación y evaluación separadas.

```bash
curl -sS http://localhost:8000/v1/evaluations \
  -H 'content-type: application/json' \
  --data @examples/evaluation.json
```

La respuesta contiene dos `run_ids`. Consultá o reproducí uno:

```bash
curl -sS http://localhost:8000/v1/runs/<run_id>
curl -sS http://localhost:8000/v1/runs/<run_id>/replay
```

El fingerprint del presupuesto del ejemplo es `steps=20;tokens=8000;timeout=120`:

```bash
curl -sS --get http://localhost:8000/v1/leaderboard \
  --data-urlencode 'suite_id=reasoning-core' \
  --data-urlencode 'suite_version=1.0.0' \
  --data-urlencode 'budget=steps=20;tokens=8000;timeout=120'
```

## Modelo de datos

`Suite` agrupa `Task`; cada `Candidate` produce un `Run` inmutable con `Trace` y `Grade`. Los runs compatibles se materializan como un `LeaderboardSnapshot`. Los archivos se guardan en `runs/<uuid>.json` mediante reemplazo atómico.

## Validación

```bash
pytest
ruff check .
cd web && npm run build
```

Los tests cubren graders, versionado, semillas, persistencia, replay, aislamiento por presupuesto, intervalos de confianza y endpoints principales.

## Seguridad y reproducibilidad

El runner incluido no ejecuta código ni realiza llamadas externas. Una integración futura que ejecute herramientas debe correr en un sandbox sin red por defecto, con límites de CPU/memoria/tiempo y un allowlist explícito. Las trazas admiten sólo payloads del dominio y nunca deben recibir secretos.

## Licencia

MIT
