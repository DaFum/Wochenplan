from typing import Any, AsyncGenerator, Dict, Generator, Optional, Union

import httpx

# Typ-Aliase für Klarheit, basierend auf den bereitgestellten Signaturen
Prompt = str
Model = str
System = str
Stream = bool
Kwargs = Dict[str, Any]


class Text:
    """
    Eine Klasse zur Interaktion mit den Pollinations Text-API-Endpunkten,
    die sowohl synchrone als auch asynchrone Operationen unterstützt.
    """
    API_ENDPOINT = "https://api.pollinations.ai/v2/text"

    def __init__(self, model: Model = "openai", **kwargs: Kwargs):
        """
        Initialisiert den Text-Client mit Standardparametern.

        :param model: Das zu verwendende Standardmodell.
        :param kwargs: Weitere Standardparameter, die bei jeder Anfrage
                       gesendet werden (z.B. system, seed).
        """
        self._default_params = {"model": model, **kwargs}
        self._sync_client = httpx.Client(timeout=120.0)
        self._async_client = httpx.AsyncClient(timeout=120.0)

    def close(self):
        """Schließt die HTTP-Clients und gibt Ressourcen frei."""
        self._sync_client.close()

    async def aclose(self):
        """Schließt die HTTP-Clients asynchron und gibt Ressourcen frei."""
        await self._async_client.aclose()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    def _prepare_payload(
        self, prompt: Optional[Prompt], **kwargs: Kwargs
    ) -> Dict[str, Any]:
        """
        Erstellt die Anfrage-Payload durch Mischen der Standard- und
        Laufzeitparameter.
        """
        payload = self._default_params.copy()
        if prompt is not None:
            payload["prompt"] = prompt
        payload.update(kwargs)
        return payload

    def __call__(
        self,
        prompt: Optional[Prompt] = None,
        stream: Stream = False,
        **kwargs: Kwargs
    ) -> Union[str, Generator[str, None, None]]:
        """
        Führt eine synchrone Anfrage zur Textgenerierung aus.

        :param prompt: Der Eingabe-Prompt für das Modell.
        :param stream: Wenn True, wird ein Generator für das Streaming der
                       Antwort zurückgegeben.
        :param kwargs: Laufzeitparameter, die die Standardeinstellungen
                       überschreiben.
        :return: Der generierte Text oder ein Generator von Text-Tokens.
        """
        payload = self._prepare_payload(prompt, **kwargs)

        if stream:
            return self._sync_stream_request(payload)

        response = self._sync_client.post(self.API_ENDPOINT, json=payload)
        response.raise_for_status()
        return response.text

    def _sync_stream_request(
        self, payload: Dict[str, Any]
    ) -> Generator[str, None, None]:
        """Behandelt synchrone Streaming-Anfragen."""
        with self._sync_client.stream(
            "POST", self.API_ENDPOINT, json=payload
        ) as response:
            response.raise_for_status()
            for chunk in response.iter_text():
                yield chunk

    async def Async(
        self,
        prompt: Optional[Prompt] = None,
        stream: Stream = False,
        **kwargs: Kwargs
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Führt eine asynchrone Anfrage zur Textgenerierung aus.

        :param prompt: Der Eingabe-Prompt für das Modell.
        :param stream: Wenn True, wird ein asynchroner Generator für das
                       Streaming der Antwort zurückgegeben.
        :param kwargs: Laufzeitparameter, die die Standardeinstellungen
                       überschreiben.
        :return: Der generierte Text oder ein asynchroner Generator von
                 Text-Tokens.
        """
        payload = self._prepare_payload(prompt, **kwargs)

        if stream:
            return self._async_stream_request(payload)

        response = await self._async_client.post(
            self.API_ENDPOINT, json=payload
        )
        response.raise_for_status()
        return response.text

    async def _async_stream_request(
        self, payload: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """Behandelt asynchrone Streaming-Anfragen."""
        async with self._async_client.stream(
            "POST", self.API_ENDPOINT, json=payload
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_text():
                yield chunk

    # Alias für bessere Lesbarkeit
    Generate = __call__
