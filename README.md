# FaceGate PoC

Минимальный запускаемый PoC распознавания лиц для офисной проходной.

FaceGate нужен бизнесу, чтобы ускорить проход сотрудников и сократить очереди на проходных в часы пик. Бесконтактная идентификация снижает зависимость от физических карт и количество типовых ситуаций, которые охране приходится разбирать вручную. В отличие от карты, которую можно передать другому человеку, распознавание лица усиливает контроль личности и повышает безопасность доступа. При этом система работает по принципу fail safe: сомнительные случаи не открывают турникет автоматически, а направляются на проверку с сохранением карты как fallback.

## Что реализовано

- FastAPI endpoint `POST /v1/access/verify` и `GET /health`;
- decision engine с решениями `allow / manual_review / deny`;
- безопасный fallback: только `allow` создаёт mock-команду `open`;
- идемпотентность по `event_id`;
- audit log в `logs/access_events.jsonl`;
- готовые demo-сценарии и pytest-тесты.

## Что является mock

Face detection, quality model, liveness, embeddings, ANN search и Secure Access Controller / турникет. Результаты CV pipeline заданы заранее для демонстрационных `event_id`.

Идемпотентность хранится в памяти процесса и является упрощением PoC; в production она заменяется persistent/distributed storage.

В target architecture mock CV pipeline заменяется реальными edge-моделями и локальным ANN-индексом при сохранении того же decision/fallback flow.

## Запуск

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

После запуска откройте demo UI: http://127.0.0.1:8000

Swagger: http://127.0.0.1:8000/docs

Тесты:

```bash
pytest
```
