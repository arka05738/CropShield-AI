"""
Production configuration validation.
Fails fast in production when required secrets/origins are missing or unsafe.
"""
from __future__ import annotations

import logging
import sys

logger = logging.getLogger("cropshield.config")

# Known-weak / placeholder secrets that must never be used in production
FORBIDDEN_JWT_SECRETS = {
    "",
    "dev-only-cropshield-jwt-change-me",
    "dev-only-compose-jwt-secret-min-32-chars",
    "cropshield-secure-jwt-key-2026-agritech-sih",
    "cropshield-super-secret-key-2026",
    "generate-a-long-random-secret",
    "generate-a-long-random-secret-at-least-32-chars",
    "change-me",
    "secret",
    "jwt-secret",
    "test-jwt-secret-cropshield-32chars-min",
    "e2e-verification-jwt-secret-32chars-min",
}


def validate_runtime_settings(settings) -> None:
    """
    Raise SystemExit with a clear message if production configuration is unsafe.
    Development may proceed with documented local defaults.
    """
    env = (settings.ENVIRONMENT or "development").lower().strip()
    is_prod = env == "production"

    if is_prod:
        secret = (settings.JWT_SECRET or "").strip()
        if not secret:
            _fail(
                "CONFIGURATION ERROR: JWT_SECRET is required when ENVIRONMENT=production. "
                "Set a long random secret in the hosting environment. Refusing to start."
            )
        if secret in FORBIDDEN_JWT_SECRETS or len(secret) < 32:
            _fail(
                "CONFIGURATION ERROR: JWT_SECRET is missing, too short (<32 chars), or a known placeholder. "
                "Set a unique strong secret. Refusing to start."
            )

        if settings.SEED_DEMO_DATA:
            _fail(
                "CONFIGURATION ERROR: SEED_DEMO_DATA cannot be true when ENVIRONMENT=production. "
                "Refusing to start with demo account seeding enabled."
            )

        if settings.ALLOW_DEMO_AUTH:
            _fail(
                "CONFIGURATION ERROR: ALLOW_DEMO_AUTH cannot be true when ENVIRONMENT=production. "
                "Refusing to start."
            )

        if settings.USE_MOCK_AI:
            _fail(
                "CONFIGURATION ERROR: USE_MOCK_AI cannot be true when ENVIRONMENT=production. "
                "Refusing to start with mock disease predictions enabled."
            )

        origins = [o for o in (settings.CORS_ORIGINS or []) if o and o != "*"]
        if not origins:
            _fail(
                "CONFIGURATION ERROR: CORS_ORIGINS must be set to an explicit comma-separated "
                "allowlist when ENVIRONMENT=production (do not use *). Refusing to start."
            )
        if "*" in (settings.CORS_ORIGINS or []):
            _fail(
                "CONFIGURATION ERROR: CORS origin '*' is not allowed in production. Refusing to start."
            )

        if settings.USE_MOCK_PEST:
            logger.warning(
                "USE_MOCK_PEST=true in production — pest results will be labeled MOCK only. "
                "Prefer USE_MOCK_PEST=false."
            )

        logger.info("Production configuration validation passed.")
    else:
        if not (settings.JWT_SECRET or "").strip():
            logger.warning(
                "JWT_SECRET not set — using documented development-only fallback. "
                "Never use this in production."
            )
        if settings.SEED_DEMO_DATA:
            logger.warning(
                "SEED_DEMO_DATA=true — development demo users/analyses may be created. "
                "Disabled automatically when ENVIRONMENT=production."
            )


def _fail(message: str) -> None:
    logger.error(message)
    print(message, file=sys.stderr)
    raise SystemExit(1)
