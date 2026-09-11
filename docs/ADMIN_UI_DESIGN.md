# Admin UI Design — CropShield AI Monitoring Console

## Information architecture

Primary navigation (backend-supported only):

| Nav item | Route | Data sources |
|---|---|---|
| Dashboard | `/admin/dashboard` | `GET /admin/analytics`, `/admin/cases`, `/admin/pests`, `/admin/users` |
| Cases | `/admin/cases` | `/admin/cases` + `/admin/pests` (unified) |
| Disease Cases | `/admin/disease-cases` | `/admin/cases` (type filter) |
| Pest Cases | `/admin/pest-cases` | `/admin/pests` cases |
| Farmers | `/admin/farmers` | `/admin/users` + activity from cases |
| Models | `/admin/models` | `/admin/models` |
| Profile | `/admin/profile` | `/auth/me` + public env |

Case detail: `/admin/cases/:kind/:id` where `kind` is `disease` | `pest`.

Legacy routes (`/admin/users`, `/analyses`, `/diseases`, `/pests`, `/analytics`, `/settings`) redirect into the IA above.

## Pages

- **Dashboard** — KPI cards (real aggregates), disease/pest/crop charts, timeline (labeled period), recent cases table.
- **Cases** — filterable list (type, crop, date, severity, search).
- **Disease / Pest Cases** — same list locked to one type.
- **Case detail** — disease: image, crop, disease, AI confidence, model, RAG/recommendation status, timestamp. Pest: image, detections, bboxes when present, confidence, count, preliminary severity, model, RAG, timestamp.
- **Farmers** — farmer accounts only; analysis counts; recent activity. No passwords/tokens.
- **Models** — disease models + pest model from registry; provider, model ID, architecture/mode, scope, status. Threshold = filter, not accuracy. Model-card notes labeled **Model-reported metric**.
- **Profile** — operator identity, public API base, logout clears JWT session keys.

## Components

- `AdminLayout` — desktop left sidebar + top header; mobile drawer nav.
- `States` — Loading, Empty, Error (no raw FastAPI traces), Unauthorized, DataSourceBadge, PageHeader.
- `ModelRegistryAdmin` — model monitoring cards.
- `lib/cases.ts` — unify disease/pest rows, farmer label join, confidence formatting.

## Data sources & honesty rules

- All KPIs/charts come from admin APIs or are derived from loaded case arrays.
- If a field is missing → **Not available** or omitted.
- Never label confidence as “accuracy”.
- Expert-review agreement % is labeled separately from model accuracy.
- Crop distribution is derived client-side from loaded disease + pest cases (documented on the chart).
- Timeline period is labeled from `timeline_trends` date range (disease analyses buckets).

## Responsive strategy

- Desktop: sidebar + content.
- Tablet/mobile: hamburger drawer; tables become stacked cards under `md`.
- Charts use `ResponsiveContainer`.
- Touch targets ≥ ~44px on primary controls.

## Accessibility

- Landmark nav/header/main.
- `:focus-visible` ring.
- ARIA labels on menu open/close and alerts.
- High-contrast green/ink palette; Literata + Figtree.
- Confidence and severity always spelled out in text.

## Security considerations

- Admin JWT required (`cropshield_admin_token`).
- Login rejects `FARMER` roles; `RequireAdmin` blocks non-admin roles.
- Logout clears token + user from `localStorage`.
- Frontend only uses public API base (`VITE_API_BASE_URL` or relative `/api/v1`).
- Dev proxy: `http://127.0.0.1:8005` (CropShield).
- No Mongo URI, HF token, JWT secret, or backend secrets in frontend source.

## API contract notes (Step 9)

| Change | Why |
|---|---|
| Admin `GET /admin/pests` case objects enriched with `image_url`, `detections`, `user_id`, `advisory`, dimensions | Smallest fix so case detail can render real pest OD evidence without new endpoints |
| Admin Vite proxy `:8000` → `:8005` | Align with CropShield backend host port used by Farmer UI |
| Frontend pest list parsing reads `cases` array | Already returned by backend; types/client updated |

## Out of scope (intentionally)

- Farmer frontend unchanged.
- No new AI models.
- No fake KPIs/charts/weather/sensors.
- Knowledge/validations/GIS map removed from primary nav (still available via redirects only where remapped).
