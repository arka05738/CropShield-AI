# CropShield AI

**Smart India Hackathon 2026 — Problem Statement ID: 26131**  
**Early Detection and Management of Crop Diseases and Pest Infestations**

CropShield AI is a modular crop-health intelligence platform with:

- **Farmer portal** (`Frontend SIH/`) — Vite + React 19
- **Admin command center** (`Admin/`) — separate Vite + React 19 app
- **Shared FastAPI backend** (`Backend/`) — `/api/v1`, OpenAPI at `/docs`

This repository prioritizes **honest capability labeling** over marketing claims. Disease inference uses a **Hugging Face PlantVillage ViT** when `torch`/`transformers` are installed; otherwise (or for uncovered crops) a **labeled heuristic** fallback. Pest detection is **off by default** (no YOLO weights shipped). No Keras weights from outside this directory are used.

---

## 1. Project overview

Farmers upload a crop image, receive an image-level disease assessment, optional weather context, grounded (or explicitly unavailable) advisory, and can request expert validation. Agriculture officials use the Admin app to inspect users, analyses, hotspots, validation queues, knowledge catalog, and model registry metadata — all from **real stored data**.

## 2. Problem statement

SIH PS 26131: Early Detection and Management of Crop Diseases and Pest Infestations.

## 3. Architecture

```
Farmer Frontend (Vercel-ready)     Admin Frontend (Vercel-ready)
        \                              /
         \                            /
          ---- HTTPS /api/v1 ---->
                 FastAPI (Render-ready)
                    |     |      |
                 ML/RAG  Weather  DB (Mongo or memory)
```

## 4. Features (actual)

| Feature | Status |
|---------|--------|
| Auth (JWT + bcrypt) | Working; roles enforced on admin APIs |
| Image upload + gatekeeper | Working (ExG heuristic) |
| Crop / disease inference | Hugging Face PlantVillage ViT (primary); heuristic fallback labeled in `inference_meta` |
| Pest detection | Unavailable unless `USE_MOCK_PEST` or `PEST_MODEL_PATH` |
| Risk fusion | Working (rules); distinguished from image-level result |
| Weather (Open-Meteo) | Working; cache/unavailable labeled |
| RAG advisory | Curated ICAR-style records + optional Groq; no fabricated doses on miss |
| History | Real store (Mongo when available, else memory) |
| Expert validation | Working; ground truth stored; no auto-retrain |
| Admin analytics | Derived from stored records only |
| GIS hotspots | Seeded + recorded cases |
| Multilingual UI | Partial (nav strings); API language param supported |
| Voice | Not implemented |

## 5. Folder structure

```
crop_Project_SIH/
├── Admin/                 # Official/Admin SPA (port 5174)
├── Frontend SIH/          # Farmer SPA (port 5173)
├── Backend/               # FastAPI
├── infrastructure/        # Docker, Render, Vercel helpers
├── knowledge-base/        # Curated POP markdown
├── docs/                  # Audit + implementation reports
├── docker-compose.yml
├── .env.example
└── README.md
```

## 6–8. Local setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Optional: MongoDB on `localhost:27017`

### Environment
```bash
cp .env.example .env
# Set JWT_SECRET and optional GROQ_API_KEY
```

### Backend
```bash
cd Backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Docs: http://localhost:8000/docs  
- Health: http://localhost:8000/api/v1/health

### Farmer frontend
```bash
cd "Frontend SIH"
npm install
npm run dev
```
http://localhost:5173

### Admin frontend
```bash
cd Admin
npm install
npm run dev
```
http://localhost:5174

## 9. Environment variables

See `.env.example`. Important:

| Variable | Purpose |
|----------|---------|
| `JWT_SECRET` | Required in production |
| `ALLOW_DEMO_AUTH` | Dev-only soft auth (keep `false`) |
| `MONGO_URI` | Optional persistence |
| `GROQ_API_KEY` | Optional LLM |
| `USE_MOCK_PEST` | Labeled demo pest boxes only |
| `CORS_ORIGINS` | Comma-separated; never `*` with credentials |
| `VITE_API_BASE_URL` | Frontend/Admin production API URL |

## 10. AI model configuration

- **Disease (primary):** Hugging Face Hub model `kimcomehome/plantvillage-vit-leaf-disease` (ViT fine-tuned on PlantVillage, 38 classes). Set `USE_HF_DISEASE_MODEL=true` and install `torch` + `transformers`. Optional `HF_TOKEN` for Hub rate limits.
- **Coverage:** Tomato, Potato, Grape, Maize/Corn, Apple, Cherry, Peach, Pepper, Strawberry, etc. **Not** covered by PlantVillage: Rice, Wheat, Cotton, Sugarcane, Sunflower — those use the heuristic fallback with an explicit note (or unavailable if no taxonomy).
- **No external local Keras/DenseNet files** from other folders are loaded.
- Crop ID: prefers `crop_hint`; otherwise color-hash among disease-supported crops.
- Pest: set `PEST_MODEL_PATH` for trained YOLO; otherwise unavailable (`USE_MOCK_PEST` for labeled demo only).
- Env: `HF_DISEASE_MODEL_ID`, `USE_HF_DISEASE_MODEL`, `DISEASE_MODEL_DIR` (unused by HF path), `PEST_MODEL_PATH`.

## 11. RAG setup

- ChromaDB + 64-dim hash embeddings (not MiniLM).
- Curated records in `Backend/app/rag/icar_knowledge.py`.
- If no crop–disease match → **guidance unavailable** (no invented dosage).

## 12. Database

- Prefers MongoDB; otherwise in-memory (lost on restart).
- Health endpoint reports `persistence_mode`.

## 13. Demo accounts (development only)

Demo users are **not** created in production.

| Condition | Behaviour |
|-----------|-----------|
| `ENVIRONMENT=production` | Seed blocked |
| `SEED_DEMO_DATA=false` (default) | Seed blocked |
| `SEED_DEMO_DATA=true` + non-production | Seeds `demo@` / `admin@` for local/SIH demos |

Never set `SEED_DEMO_DATA=true` on Render. Create real admin users via secure registration/ops process.

## 14. Testing

```bash
cd Backend
pytest tests/test_api.py -v
```

```bash
cd "Frontend SIH"
npm run build

cd ../Admin
npm run build
```

## 15. Docker

```bash
docker-compose up --build
```
- Farmer: http://localhost:5173  
- Admin: http://localhost:5174  
- API: http://localhost:8000  

## 16. Vercel (Frontend + Admin)

1. Import `Frontend SIH` (or `Admin`) as a Vite project.
2. Set `VITE_API_BASE_URL=https://<your-render-api>/api/v1`
3. Ensure SPA rewrites (`vercel.json` already present in each app).
4. Add your Vercel origin to backend `CORS_ORIGINS`.

Helper copies: `infrastructure/vercel/frontend.vercel.json`, `admin.vercel.json`.

## 17. Render (Backend)

1. Use `infrastructure/Dockerfile.backend` (or Blueprint `infrastructure/render/render.yaml`).
2. Set `JWT_SECRET`, `CORS_ORIGINS`, optional `MONGO_URI`, `GROQ_API_KEY`.
3. Health check: `/api/v1/health`
4. `PORT` is read from the environment.

## 18. Troubleshooting

| Issue | Fix |
|-------|-----|
| 401 on diagnose | Login first; `ALLOW_DEMO_AUTH` must be false in prod |
| 403 on admin | Use admin account; farmers are rejected |
| Empty pests | Expected unless mock/trained pest model enabled |
| Weather unavailable | Network or missing lat/lon; UI should show unavailable |
| Mongo not connected | App continues in memory mode |

## 19. Security

- Admin authorization is enforced by the backend.
- Public registration limited to `FARMER`.
- No plaintext password fallback.
- Do not commit `.env` or API keys.

## 20. Current limitations

- Disease HF model covers PlantVillage crops only; Rice/Wheat/Cotton/Sugarcane/Sunflower use heuristic or unavailable
- No YOLO pest weights in repo
- Hash embeddings, not sentence-transformers
- Knowledge PDF upload is catalog-only
- Voice STT/TTS not implemented
- Memory store if Mongo unavailable
- Multilingual UI only partially applied

## 21. Future SIH extensions

- Additional HF models for Indian crops outside PlantVillage
- Real YOLO pest model via `PEST_MODEL_PATH`
- MiniLM embeddings + true PDF chunking
- Full GIS clustering from districts at scale
- Voice interfaces

## License

Apache-2.0 (project materials for SIH).
