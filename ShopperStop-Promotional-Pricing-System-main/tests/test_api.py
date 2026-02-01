from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    # FIX: Changed path from "/api/v1/bills/health" to "/health"
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_calculate_bill_api():
    payload = {
        "customer": {"id": "C1", "tier": "REGULAR"},
        "cart": {
            "items": [
                {"sku": "1", "name": "TV", "category": "ELEC", "quantity": 1, "unit_price": 5000}
            ]
        },
        "context": {"store_id": "ST1"}
    }
    response = client.post("/api/v1/bills/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_discount" in data
    assert "net_amount" in data

def test_promotion_crud_lifecycle():
    # 1. Create
    promo_data = {
        "id": "TEST_PROMO_API",
        "name": "Test Promo",
        "type": "FLAT",
        "action": {"flat_amount": 100},
        "active": False
    }
    res = client.post("/api/v1/promotions/", json=promo_data)
    assert res.status_code == 201
    
    # 2. Activate
    res = client.post("/api/v1/promotions/TEST_PROMO_API/activate")
    assert res.status_code == 200
    
    # 3. Verify Active
    res = client.get("/api/v1/promotions/TEST_PROMO_API")
    assert res.json()['active'] is True