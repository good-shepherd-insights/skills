---
name: wappalyzer-api
description: Use when any agent needs to fingerprint a website's technology stack (CMS, frameworks, CDN, analytics) via the GSI wappalyzergo API.
---

# wappalyzer API

Send a URL, get detected technologies. Source: `good-shepherd-insights/wappalyzergo-api` (wire types in `api/v1/types.go`).

## Endpoint

Local (verified live 2026-09-19): `http://127.0.0.1:18081`
Public: `https://wappalyzer.goodshepherdinsights.com` (tunnel — verify reachable before use)

## Auth

All `/v1/*` routes require the shared bearer token:

```http
Authorization: Bearer <WAPP_API_TOKEN>
```

Read the token from the env var `WAPP_API_TOKEN` on the box — never hardcode or commit it. `/healthz`, `/readyz`, `/v1/version` need no token.

## Call

```bash
curl -sS -m 30 http://127.0.0.1:18081/v1/fingerprint \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $WAPP_API_TOKEN" \
  -d '{"url":"https://example.com","include":["apps","cats","info"]}'
```

`url` is required. `include` is optional; valid values `apps` (default), `cats`, `info`.

Response: `status_code` (upstream HTTP status — check it before trusting results), `duration_ms`, `final_url`, and `tech` with only the requested sections: `apps` (sorted names), `cats` (name → category IDs), `info` (description, website, CPE, icon, categories).

## Errors

| HTTP | code | Meaning |
|---|---|---|
| 400 | `bad_request` | missing url / bad JSON / unknown include |
| 401 | `unauthorized` | missing or wrong bearer token |
| 429 | `rate_limited` | over 60 req/min default budget |
| 502 | `fetch_failed` | upstream unreachable |
| 503 | `not_ready` | engine not loaded |

All errors carry `request_id` — quote it when reporting.

## Pitfalls

- v1 is static headers+body only — no JS-rendered detection.
- Non-2xx upstream pages still fingerprint; check `status_code`.
