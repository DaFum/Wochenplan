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
        Initialisiert eine neue Instanz des Text-Clients für die Pollinations Text-API.
        
        Legt das Standardmodell und optionale Standardparameter für alle Anfragen fest und erstellt synchrone sowie asynchrone HTTP-Clients mit 120 Sekunden Timeout.
        """
        self._default_params = {"model": model, **kwargs}
        self._sync_client = httpx.Client(timeout=120.0)
        self._async_client = httpx.AsyncClient(timeout=120.0)

    def close(self):
        """
        Schließt den synchronen HTTP-Client und gibt die zugehörigen Ressourcen frei.
        """
        self._sync_client.close()

    async def aclose(self):
        """
        Schließt den asynchronen HTTP-Client und gibt alle zugehörigen Ressourcen frei.
        """
        await self._async_client.aclose()

    def __enter__(self):
        """
        Ermöglicht die Verwendung der Klasse als synchronen Kontextmanager und gibt die Instanz selbst zurück.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Beendet den synchronen Kontextmanager und schließt den HTTP-Client, um Ressourcen freizugeben.
        """
        self.close()

    async def __aenter__(self):
        """
        Ermöglicht die Verwendung der Klasse als asynchronen Kontextmanager und gibt die Instanz zurück.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Beendet den asynchronen Kontextmanager und schließt den asynchronen HTTP-Client, um Ressourcen freizugeben.
        """
        await self.aclose()

    def _prepare_payload(
        self, prompt: Optional[Prompt], **kwargs: Kwargs
    ) -> Dict[str, Any]:
        """
        Erstellt die Anfrage-Payload für die Textgenerierung, indem Standardparameter mit einem optionalen Prompt und zusätzlichen Laufzeitparametern kombiniert werden.
        
        Parameter:
            prompt (Optional[str]): Der zu generierende Texteingabe-Prompt. Wird nur hinzugefügt, wenn angegeben.
        
        Gibt zurück:
            Dict[str, Any]: Die vollständige Payload für die API-Anfrage.
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
        Sendet eine synchrone Anfrage an die Pollinations Text-API und gibt entweder den vollständigen generierten Text oder einen Generator für gestreamte Textabschnitte zurück.
        
        Parameter:
            prompt (Optional[str]): Der Eingabetext für das Modell.
            stream (bool): Gibt an, ob die Antwort als Stream (Generator) zurückgegeben wird.
            kwargs: Zusätzliche Parameter zur Laufzeit, die die Standardwerte überschreiben.
        
        Rückgabe:
            Union[str, Generator[str, None, None]]: Der generierte Text als String oder ein Generator, der Textabschnitte liefert, wenn Streaming aktiviert ist.
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
        """
        Führt eine synchrone Streaming-Anfrage an die Pollinations Text-API aus und liefert Textabschnitte als Generator.
        
        Parameter:
            payload (Dict[str, Any]): Das Anfrage-Payload für die Textgenerierung.
        
        Gibt zurück:
            Generator[str, None, None]: Ein Generator, der Textabschnitte aus der Streaming-Antwort liefert.
        """
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
        Sendet eine asynchrone Anfrage an die Pollinations Text-API und gibt entweder den vollständigen generierten Text oder einen asynchronen Generator für gestreamte Textabschnitte zurück.
        
        Parameter:
            prompt (Optional[str]): Optionaler Eingabetext für das Modell.
            stream (bool): Gibt bei True einen asynchronen Generator für gestreamte Textausgabe zurück; andernfalls den vollständigen Text.
        
        Rückgabe:
            Union[str, AsyncGenerator[str, None]]: Der generierte Text als String oder ein asynchroner Generator, der Textabschnitte liefert.
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
        """
        Führt eine asynchrone Streaming-Anfrage an die Pollinations Text-API durch und liefert Textabschnitte als asynchronen Generator.
        
        Parameter:
            payload (Dict[str, Any]): Die Nutzlast für die Anfrage, einschließlich Prompt und Modellparameter.
        
        Ergibt:
            AsyncGenerator[str, None]: Ein asynchroner Generator, der Textabschnitte aus der Streaming-Antwort liefert.
        
        Wirft:
            httpx.HTTPStatusError: Wenn die API eine Fehlermeldung zurückgibt.
        """
        async with self._async_client.stream(
            "POST", self.API_ENDPOINT, json=payload
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_text():
                yield chunk

    # Alias für bessere Lesbarkeit
    Generate = __call__
