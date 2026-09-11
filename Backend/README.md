# CropShield Backend

FastAPI service for CropShield AI (SIH 2026 PS 26131).

## Run

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- OpenAPI: `/docs`
- Health: `/api/v1/health`

## Tests

```bash
pytest tests/test_api.py -v
```

## Notes

- Vision is heuristic unless weights are configured.
- Pest detection off by default (`USE_MOCK_PEST=false`).
- Mongo optional; memory fallback is labeled via health `persistence_mode`.
