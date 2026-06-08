# WebMedia XHS API

This is a deployable wrapper for `XHS-Downloader`.

It runs the upstream FastAPI routes as an independent backend service for the
main WebMedia Extractor site.

## API

Health check:

```http
GET /health
```

Parse RedNote / Xiaohongshu detail:

```http
POST /xhs/detail
Content-Type: application/json
Authorization: Bearer <XHS_API_TOKEN>

{
  "url": "https://xhslink.com/...",
  "download": false,
  "skip": false
}
```

`XHS_API_TOKEN` is optional. If it is empty, `/xhs/detail` is public. If it is
set, the caller must send the matching bearer token.

## Render Deploy

1. Push this folder to a GitHub repository.
2. Create a Render Blueprint from the repository.
3. Render will read `render.yaml` and build the Docker service.
4. Set `XHS_API_TOKEN` during Blueprint setup if you want a private API.
5. After deploy, copy the Render service URL, for example:

```text
https://webmedia-xhs-api.onrender.com
```

6. In the Vercel project for the main site, set:

```env
XHS_API_BASE_URL=https://webmedia-xhs-api.onrender.com
XHS_API_TOKEN=<same token if configured>
```

7. Redeploy the main Vercel site.

## Local Run

Requires Python 3.12.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PORT="5556"
python serve.py
```

Open:

```text
http://127.0.0.1:5556/health
```

## Notes

- This service should be deployed separately from the Next.js/Vercel frontend.
- The main site calls this service only when `XHS_API_BASE_URL` is configured.
- Keep `download` as `false` from the website so the backend returns media URLs
  instead of storing files in the container.
- The included upstream source is GPL-3.0.
