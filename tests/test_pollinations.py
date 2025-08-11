import sys
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image as PILImage

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pollinations.text import Text
from pollinations.image import Image


def test_text_sends_prompt_as_message():
    """Der Text-Client sollte den Prompt als Benutzernachricht senden."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == httpx.URL("https://text.pollinations.ai/")
        # Parse JSON manuell, da httpx.Request keine json()-Methode besitzt
        import json

        body = json.loads(request.content.decode())
        assert body["messages"][-1]["content"] == "Hello"
        return httpx.Response(200, text="Hi!")

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    txt = Text(client=client)
    try:
        result = txt("Hello")
        assert result == "Hi!"
    finally:
        txt.close()


def test_image_returns_pil_image():
    """Der Image-Client sollte ein PIL-Bild zurückgeben."""

    img_buf = BytesIO()
    PILImage.new("RGB", (1, 1), color="red").save(img_buf, format="PNG")
    content = img_buf.getvalue()

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "image.pollinations.ai"
        return httpx.Response(200, content=content)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    img_client = Image(client=client)
    try:
        image = img_client("Test")
        assert isinstance(image, PILImage.Image)
        assert image.size == (1, 1)
    finally:
        img_client.close()

