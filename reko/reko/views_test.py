from django.test import Client
from django.urls import reverse


def test_index_page(client: Client) -> None:
    response = client.get(reverse("index"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Välkommen till handlareko.se!" in content
