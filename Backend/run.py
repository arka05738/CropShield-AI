"""
CropShield AI — Local Development Server Launcher.

Usage:
    python run.py
    python run.py --port 8005 --reload
"""
import argparse
import os
import sys
from pathlib import Path

# Ensure Backend root is in sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load .env from root and Backend if present
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR.parent / ".env")
load_dotenv(BACKEND_DIR / ".env")

import uvicorn
from app.core.config import settings


def parse_args():
    parser = argparse.ArgumentParser(description="CropShield AI Backend Server")
    default_port = int(os.getenv("PORT", "8005"))
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("HOST", "0.0.0.0"),
        help="Host address to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=default_port,
        help=f"Port to run the backend on (default: {default_port})",
    )
    parser.add_argument(
        "--reload",
        dest="reload",
        action="store_true",
        default=settings.ENVIRONMENT.lower() != "production",
        help="Enable auto-reload on code changes (default: True for non-prod)",
    )
    parser.add_argument(
        "--no-reload",
        dest="reload",
        action="store_false",
        help="Disable auto-reload",
    )
    return parser.parse_args()


def print_banner(host: str, port: int):
    display_host = "localhost" if host in ("0.0.0.0", "127.0.0.1") else host
    print("\n" + "=" * 60)
    print("🌾  CropShield AI — Backend Server")
    print("=" * 60)
    print(f" Environment   : {settings.ENVIRONMENT}")
    print(f" Mongo URI     : {settings.MONGO_URI.split('@')[-1] if '@' in settings.MONGO_URI else settings.MONGO_URI}")
    print(f" Database      : {settings.MONGO_DB_NAME}")
    print(f" Groq LLM      : {settings.GROQ_MODEL} (Key set: {bool(settings.GROQ_API_KEY)})")
    print(f" Server URL    : http://{display_host}:{port}")
    print(f" OpenAPI Docs  : http://{display_host}:{port}/docs")
    print(f" Health Check  : http://{display_host}:{port}/api/v1/health")
    print("-" * 60)
    print(f" Farmer Portal : http://localhost:5173")
    print(f" Admin Center  : http://localhost:5174")
    print("=" * 60 + "\n")


def main():
    args = parse_args()
    print_banner(args.host, args.port)
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
