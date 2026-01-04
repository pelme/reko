from django.test import Client
from django.urls import reverse


def test_index_page(client: Client) -> None:
    response = client.get(reverse("index"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "<h1>handlareko.se</h1>" in content
