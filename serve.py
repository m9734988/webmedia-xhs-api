import os
from asyncio import run

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from uvicorn import Config, Server

from source import Settings, XHS


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

        xhs.setup_routes(app)
        await Server(Config(app, host=host, port=port, log_level=log_level)).serve()


if __name__ == "__main__":
    run(main())
