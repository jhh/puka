from __future__ import annotations

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_bookmarks(client):
    url = reverse("bookmarks")
    response = client.get(url)
    assert response.status_code == 200
