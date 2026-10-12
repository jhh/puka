"""The browser_auth command seeds a Playwright storage state for local QA."""

from __future__ import annotations

import json

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client
from django.urls import reverse

from puka.users.models import CustomUser

pytestmark = pytest.mark.django_db


def test_browser_auth_writes_storage_state(settings, tmp_path):
    settings.DEBUG = True
    output = tmp_path / "auth.json"

    call_command("browser_auth", output=str(output))

    user = CustomUser.objects.get(username="qa")
    assert user.is_staff
    assert user.is_superuser
    assert not user.has_usable_password()

    state = json.loads(output.read_text())
    assert state["origins"] == []
    (cookie,) = state["cookies"]
    assert cookie["name"] == "sessionid"
    assert cookie["domain"] == "localhost"
    assert cookie["path"] == "/"
    assert cookie["httpOnly"] is True
    assert cookie["secure"] is False
    assert cookie["sameSite"] == "Lax"

    client = Client()
    client.cookies["sessionid"] = cookie["value"]
    response = client.get(reverse("home"))
    assert response.status_code == 200


def test_browser_auth_requires_debug(settings):
    settings.DEBUG = False
    with pytest.raises(CommandError):
        call_command("browser_auth")
