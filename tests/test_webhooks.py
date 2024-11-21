import pytest
from app.services.webhooks import notify_generation_event
from app.models.schemas import GenerationEvent
from datetime import datetime

def test_webhook_registration(client, valid_webhook_config):
    """Test webhook registration and listing"""
    # Registrar webhook
    response = client.post("/api/webhooks", json=valid_webhook_config)
    assert response.status_code == 200
    data = response.json()
    webhook_id = data["id"]
    
    # Listar webhooks
    response = client.get("/api/webhooks")
    assert response.status_code == 200
    webhooks = response.json()
    assert any(w["id"] == webhook_id for w in webhooks)
    
    # Eliminar webhook
    response = client.delete(f"/api/webhooks/{webhook_id}")
    assert response.status_code == 200

def test_webhook_validation(client):
    """Test webhook configuration validation"""
    invalid_configs = [
        # URL inválida
        {
            "url": "not-a-url",
            "secret": "test-secret"
        },
        # Sin URL
        {
            "secret": "test-secret"
        }
    ]
    
    for config in invalid_configs:
        response = client.post("/api/webhooks", json=config)
        assert response.status_code == 422

def test_webhook_update(client, valid_webhook_config):
    """Test webhook update functionality"""
    # Registrar webhook
    response = client.post("/api/webhooks", json=valid_webhook_config)
    assert response.status_code == 200
    webhook_id = response.json()["id"]
    
    # Actualizar webhook
    updated_config = valid_webhook_config.copy()
    updated_config["description"] = "Updated description"
    response = client.put(f"/api/webhooks/{webhook_id}", json=updated_config)
    assert response.status_code == 200
    
    # Verificar actualización
    response = client.get("/api/webhooks")
    webhooks = response.json()
    updated_webhook = next(w for w in webhooks if w["id"] == webhook_id)
    assert updated_webhook["description"] == "Updated description"

def test_webhook_notification(client, valid_webhook_config, valid_template_request):
    """Test webhook notification when generating frontpage"""
    # Registrar webhook
    response = client.post("/api/webhooks", json=valid_webhook_config)
    assert response.status_code == 200
    
    # Generar frontpage (debería disparar notificación)
    response = client.post("/api/generate-frontpage", json=valid_template_request)
    assert response.status_code == 200
    
    # Nota: Para probar las notificaciones reales, necesitarías un servidor de prueba
    # que reciba las notificaciones. Aquí solo verificamos que no haya errores
    # en el proceso de generación cuando hay webhooks configurados.
