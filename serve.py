import os
from asyncio import run
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from uvicorn import Config, Server

from source import Settings, XHS

parse_events: list[dict] = []
max_parse_events = 1000
allowed_event_keys = {
    "createdAt",
    "platform",
    "ok",
    "code",
    "message",
    "inputPreview",
    "sourceUrl",
    "durationMs",
    "mediaCount",
}


def authorized(request: Request) -> bool:
    token = os.getenv("XHS_API_TOKEN", "").strip()
    if not token:
        return True
    return request.headers.get("authorization") == f"Bearer {token}"


async def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5556"))
    log_level = os.getenv("LOG_LEVEL", "info")
    settings = Settings().run()

    if cookie := os.getenv("XHS_COOKIE", "").strip():
        settings["cookie"] = cookie
    if proxy := os.getenv("XHS_PROXY", "").strip():
        settings["proxy"] = proxy
    if image_format := os.getenv("XHS_IMAGE_FORMAT", "").strip():
        settings["image_format"] = image_format.upper()

    async with XHS(**settings) as xhs:
        app = FastAPI(title="WebMedia XHS API", version="1.0")

        @app.middleware("http")
        async def require_token(request: Request, call_next):
            if request.url.path.startswith("/xhs/") and not authorized(request):
                return JSONResponse({"detail": "Unauthorized"}, status_code=401)
            return await call_next(request)

        @app.get("/health")
        async def health():
            return {"ok": True}

        @app.post("/logs/parse")
        async def record_parse_log(request: Request):
            payload = await request.json()
            raw_event = payload.get("event") if isinstance(payload, dict) else None
            if not isinstance(raw_event, dict):
                return JSONResponse({"ok": False, "error": "Invalid event"}, status_code=400)

            event = {key: raw_event.get(key) for key in allowed_event_keys if key in raw_event}
            event["createdAt"] = event.get("createdAt") or datetime.now(timezone.utc).isoformat()
            event["platform"] = str(event.get("platform") or "unknown")[:40]
            event["ok"] = bool(event.get("ok"))
            for key in ("code", "message", "inputPreview", "sourceUrl"):
                if event.get(key) is not None:
                    event[key] = str(event[key])[:500]

            parse_events.insert(0, event)
            del parse_events[max_parse_events:]
            return {"ok": True}

        @app.get("/logs/stats")
        async def parse_log_stats():
            total = len(parse_events)
            success = sum(1 for event in parse_events if event.get("ok"))
            failed = total - success
            durations = [event.get("durationMs") for event in parse_events if isinstance(event.get("durationMs"), int)]
            by_platform: dict[str, int] = {}
            by_error: dict[str, int] = {}

            for event in parse_events:
                platform = str(event.get("platform") or "unknown")
                by_platform[platform] = by_platform.get(platform, 0) + 1
                code = event.get("code")
                if code:
                    code_text = str(code)
                    by_error[code_text] = by_error.get(code_text, 0) + 1

            return {
                "ok": True,
                "stats": {
                    "total": total,
                    "success": success,
                    "failed": failed,
                    "successRate": 0 if total == 0 else round(success / total, 4),
                    "avgDurationMs": 0 if not durations else round(sum(durations) / len(durations)),
                    "byPlatform": by_platform,
                    "byError": by_error,
                    "recent": parse_events[:30],
                },
            }

        xhs.setup_routes(app)
        await Server(Config(app, host=host, port=port, log_level=log_level)).serve()


if __name__ == "__main__":
    run(main())
