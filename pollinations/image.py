"""Einfacher Pollinations Image-Client.

Dieser Wrapper stellt eine minimalistische Schnittstelle zum offiziellen
Image-Endpoint zur Verfügung. Er unterstützt synchrone und asynchrone
Anfragen und liefert PIL-Image-Objekte zur weiteren Verarbeitung.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any, Dict, Optional
from urllib.parse import quote, urlencode

import httpx
from PIL import Image as PILImage, UnidentifiedImageError

Prompt = str
Model = str
Filename = str
Kwargs = Dict[str, Any]


class Image:
    """Client für den ``image.pollinations.ai``-Dienst."""

    API_ENDPOINT = "https://image.pollinations.ai/prompt"

    def __init__(
        self,
        model: Model = "flux",
        width: int = 1024,
        height: int = 1024,
        seed: str = "random",
        *,
        client: Optional[httpx.Client] = None,
        async_client: Optional[httpx.AsyncClient] = None,
        **kwargs: Kwargs,
    ) -> None:
        self._default_params: Dict[str, Any] = {
            "model": model,
            "width": width,
            "height": height,
            "seed": seed,
            **kwargs,
        }
        self._sync_client = client or httpx.Client(timeout=120.0)
        self._async_client = async_client or httpx.AsyncClient(timeout=120.0)

    def close(self) -> None:
        """Schließt den synchronen Client."""
        self._sync_client.close()

    async def aclose(self) -> None:
        """Schließt den asynchronen Client."""
        await self._async_client.aclose()

    def __enter__(self) -> "Image":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    async def __aenter__(self) -> "Image":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    def _build_url(self, prompt: Prompt) -> str:
        return f"{self.API_ENDPOINT}/{quote(prompt)}"

    def url(self, prompt: Prompt, **kwargs: Kwargs) -> str:
        """Erzeugt nur die Bild-URL ohne einen HTTP-Request auszulösen."""
        params = self._default_params.copy()
        params.update(kwargs)
        return f"{self._build_url(prompt)}?{urlencode(params)}"

    def __call__(
        self,
        prompt: Prompt,
        *,
        save: bool = False,
        file: Optional[Filename] = None,
        **kwargs: Kwargs,
    ) -> PILImage.Image:
        params = self._default_params.copy()
        params.update(kwargs)
        response = self._sync_client.get(self._build_url(prompt), params=params)
        response.raise_for_status()
        if response.headers.get('content-type', '').startswith('image/'):
            try:
                image = PILImage.open(BytesIO(response.content))
            except (UnidentifiedImageError, OSError) as e:
                raise RuntimeError(f"Failed to decode image: {e}") from e
        else:
            raise RuntimeError(f"API returned non-image content: {response.text[:100]}...")
        if save and file:
            try:
                image.save(file)
            except OSError as e:
                raise RuntimeError(f"Failed to save image: {e}") from e
        return image

    async def generate_async(
        self,
        prompt: Prompt,
        *,
        save: bool = False,
        file: Optional[Filename] = None,
        **kwargs: Kwargs,
    ) -> PILImage.Image:
        params = self._default_params.copy()
        params.update(kwargs)
        response = await self._async_client.get(
            self._build_url(prompt), params=params
        )
        response.raise_for_status()
        try:
            image = PILImage.open(BytesIO(response.content))
        except (UnidentifiedImageError, OSError) as e:
            raise RuntimeError(f"Failed to decode image: {e}") from e
        if save and file:
            try:
                image.save(file)
            except OSError as e:
                raise RuntimeError(f"Failed to save image: {e}") from e
        return image

    # Alias für bessere Lesbarkeit
    async def a(
        self,
        prompt: Prompt,
        *,
        save: bool = False,
        file: Optional[Filename] = None,
        **kwargs: Kwargs,
    ) -> PILImage.Image:
        params = self._default_params.copy()
        params.update(kwargs)
        response = await self._async_client.get(
            self._build_url(prompt), params=params
        )
        response.raise_for_status()
        image = PILImage.open(BytesIO(response.content))
        if save and file:
            image.save(file)
        return image

    # Alias für bessere Lesbarkeit
    generate = __call__

