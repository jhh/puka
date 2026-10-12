from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
)
from django.contrib.sessions.backends.db import SessionStore
from django.core.management.base import BaseCommand, CommandError

from puka.users.models import CustomUser


class Command(BaseCommand):
    help = "Write a Playwright storage state with a signed-in session for browser QA."

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            default="qa",
            help="Username to sign in as; created when missing.",
        )
        parser.add_argument(
            "--domain",
            default="localhost",
            help="Domain the session cookie is valid for.",
        )
        parser.add_argument(
            "--output",
            default=".playwright-mcp/auth.json",
            help="Storage state file to write, relative to the project root.",
        )

    def handle(self, *_args, **options):
        if not settings.DEBUG:
            msg = "browser_auth is only available with DEBUG=true."
            raise CommandError(msg)

        user, created = CustomUser.objects.get_or_create(
            username=options["user"],
            defaults={"email": f"{options['user']}@example.com"},
        )
        if created:
            user.set_unusable_password()
            user.is_staff = True
            user.is_superuser = True
            user.save()

        session = SessionStore()
        session[SESSION_KEY] = str(user.pk)
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session[HASH_SESSION_KEY] = user.get_session_auth_hash()
        session.save()

        state = {
            "cookies": [
                {
                    "name": settings.SESSION_COOKIE_NAME,
                    "value": session.session_key,
                    "domain": options["domain"],
                    "path": "/",
                    "expires": -1,
                    "httpOnly": True,
                    "secure": settings.SESSION_COOKIE_SECURE,
                    "sameSite": settings.SESSION_COOKIE_SAMESITE or "Lax",
                },
            ],
            "origins": [],
        }
        output = Path(options["output"])
        if not output.is_absolute():
            output = settings.BASE_DIR / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(state, indent=2) + "\n")
        self.stdout.write(f"Signed in as {user.username}; wrote {output}")
