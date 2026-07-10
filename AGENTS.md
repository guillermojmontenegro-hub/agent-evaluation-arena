# AGENTS.md

## Misión

Comparar sistemas AI con evaluaciones repetibles, presupuestos equivalentes y resultados explicables.

## Reglas

- Versionar dataset, runner, grader y configuración del modelo en cada resultado.
- Separar generación de evaluación para evitar contaminación.
- Priorizar graders determinísticos; calibrar cualquier grader LLM.
- Aislar ejecución de código y bloquear red salvo que la tarea la requiera.
- No mezclar runs con presupuestos diferentes en un ranking.
- Persistir trazas reproducibles sin guardar secretos.

## Entidades

`Suite`, `Task`, `Candidate`, `Run`, `Trace`, `Grade` y `LeaderboardSnapshot`.

## Terminado

Semillas y versiones registradas, tests de graders, intervalos de confianza visibles y replay funcional.
