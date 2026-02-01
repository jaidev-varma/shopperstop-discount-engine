from fastapi.testclient import TestClient
from app.main import app
from app.models.db import db # Import DB to clear it

client = TestClient(app)

def create_dummy_rule(rule_id="TEST_RULE_FULL"):
    return {
        "id": rule_id,
        "name": "Test Rule",
        "type": "FLAT",
        "priority": 1,
        "conditions": {},
        "action": {"flat_amount": 100},
        "active": True
    }

def test_create_and_get_promotion():
    rule_data = create_dummy_rule("RULE_GET")
    response = client.post("/api/v1/promotions/", json=rule_data)
    assert response.status_code == 201
    response = client.get("/api/v1/promotions/RULE_GET")
    assert response.status_code == 200

def test_list_promotions():
    client.post("/api/v1/promotions/", json=create_dummy_rule("LIST_1"))
    client.post("/api/v1/promotions/", json=create_dummy_rule("LIST_2"))
    response = client.get("/api/v1/promotions/")
    assert response.status_code == 200
    assert len(response.json()) >= 2

def test_lifecycle_activate_deactivate():
    rule_id = "RULE_LIFECYCLE"
    rule_data = create_dummy_rule(rule_id)
    client.post("/api/v1/promotions/", json=rule_data)
    
    client.post(f"/api/v1/promotions/{rule_id}/deactivate")
    assert client.get(f"/api/v1/promotions/{rule_id}").json()["active"] is False
    
    client.post(f"/api/v1/promotions/{rule_id}/activate")
    assert client.get(f"/api/v1/promotions/{rule_id}").json()["active"] is True

def test_update_promotion():
    rule_id = "RULE_UPDATE"
    client.post("/api/v1/promotions/", json=create_dummy_rule(rule_id))
    
    update_data = create_dummy_rule(rule_id)
    update_data["action"]["flat_amount"] = 500
    
    response = client.put(f"/api/v1/promotions/{rule_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["action"]["flat_amount"] == 500

def test_delete_promotion():
    rule_id = "RULE_DELETE"
    client.post("/api/v1/promotions/", json=create_dummy_rule(rule_id))
    client.delete(f"/api/v1/promotions/{rule_id}")
    assert client.get(f"/api/v1/promotions/{rule_id}").status_code == 404

def test_simulate_promotion():
    # --- FIX: Clear DB to avoid interference from previous tests ---
    db.promotions.clear() 
    # -------------------------------------------------------------

    client.post("/api/v1/promotions/", json=create_dummy_rule("RULE_SIM"))
    
    payload = {
        "customer": {"id": "C1", "tier": "REGULAR"},
        "cart": {"items": [{"sku": "A", "name": "A", "category": "A", "quantity": 1, "unit_price": 200}]},
        "context": {"store_id": "S1"}
    }
    
    response = client.post("/api/v1/promotions/simulate", json=payload)
    assert response.status_code == 200
    
    # --- FIX IS HERE ---
    # Convert the string response to float for comparison
    assert float(response.json()["total_discount"]) == 100.0