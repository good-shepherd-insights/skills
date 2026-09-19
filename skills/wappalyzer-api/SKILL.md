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

All `/v1/*` routes require the shared bearer token. The public API is a public service — this token is the public access key:

```http
Authorization: Bearer devtoken
```

`/healthz`, `/readyz`, `/v1/version` need no token.

## Call

```bash
curl -sS -m 30 http://127.0.0.1:18081/v1/fingerprint \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer devtoken' \
  -d '{"url":"https://example.com","include":["apps","cats","info"]}'
```

`url` is required. `include` is optional; valid values `apps` (default), `cats`, `info`.

Response schema (only sections listed in `include` are populated; rest omitted):

```json
{
  "url": "https://example.com/",
  "final_url": "https://example.com/",
  "status_code": 200,
  "duration_ms": 40,
  "tech": {
    "apps": ["Cloudflare", "React"],
    "cats": {"Cloudflare": [31], "React": [12]},
    "info": {
      "React": {
        "description": "React is an open-source JavaScript library...",
        "website": "https://reactjs.org",
        "cpe": "cpe:2.3:a:facebook:react:*:*:*:*:*:*:*:*",
        "icon": "React.svg",
        "categories": ["JavaScript frameworks"]
      }
    }
  }
}
```

- `url` — as sent; `final_url` — after redirects; `status_code` — upstream HTTP status; `duration_ms` — fetch+fingerprint time.
- `tech.apps` — sorted string list. `tech.cats` — name → Wappalyzer category IDs. `tech.info` — name → metadata object (empty fields omitted).

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
