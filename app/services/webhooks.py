import httpx
import asyncio
from typing import Dict
from datetime import datetime
from app.models.schemas import WebhookConfig, GenerationEvent

# Almacenamiento de webhooks (en memoria para este ejemplo)
webhooks: Dict[str, WebhookConfig] = {}

async def send_webhook(webhook: WebhookConfig, payload: GenerationEvent):
    """Envía una notificación webhook con reintentos"""
    async with httpx.AsyncClient() as client:
        headers = {}
        if webhook.secret:
            headers["X-Webhook-Secret"] = webhook.secret

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await client.post(
                    str(webhook.url),
                    json=payload.model_dump(),
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return True
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to send webhook to {webhook.url}: {str(e)}")
                    return False
                await asyncio.sleep(2 ** attempt)

async def notify_generation_event(event: GenerationEvent):
    """Notifica a todos los webhooks activos sobre un evento de generación"""
    tasks = []
    for webhook in webhooks.values():
        if webhook.active:
            tasks.append(send_webhook(webhook, event))
    
    if tasks:
        await asyncio.gather(*tasks)
