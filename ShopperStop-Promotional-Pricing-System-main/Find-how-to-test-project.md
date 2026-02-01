This guide covers what to test, how to test it, and the expected output for every single feature we implemented.

Part 1: Automated Testing (The "One Command" Check)
Run the automated test suite first. This checks the math logic (Slabs, BOGO) and the API contract without you needing to do anything manually.

Command:

Bash
pytest
What This Tests:

Unit Logic: Verifies "Progressive Slabs" calculate correctly (e.g., splitting ₹15k into 0%, 10%, 20% buckets).

BOGO Logic: Verifies "Buy 2 Get 1 Free" math works.

API Contracts: Verifies that endpoints return 200 OK and valid JSON.

Lifecycle: Verifies creating, activating, deactivating, and deleting a promotion works.

Expected Output: You should see 11 green dots and "passed".

Plaintext
tests/test_api.py ...
tests/test_engine.py ..
tests/test_promotions.py ......
========================== 11 passed in 0.xxs ===========================
Part 2: Manual End-to-End Testing (Real World Scenarios)
Make sure your server is running in a separate terminal:

Bash
uvicorn app.main:app --reload
Test 1: Core Slab Discount (The Foundation)
Feature: Progressive Tiered Discounts.

Scenario: Regular Customer spends ₹15,000.

First 5k @ 0% = 0

Next 5k @ 10% = 500

Last 5k @ 20% = 1000

Total Discount: 1500

Action: Send POST to http://127.0.0.1:8000/api/v1/bills/calculate

JSON
{
  "customer": {"id": "C1", "tier": "REGULAR"},
  "cart": {
    "items": [
      {"sku": "TV", "name": "TV", "category": "ELEC", "quantity": 1, "unit_price": 15000}
    ]
  },
  "context": {"store_id": "MUM01"}
}
Expected Output:

JSON
{
  "gross_amount": 15000.0,
  "total_discount": 1500.0,  <-- VERIFY THIS MATH
  "net_amount": 13500.0,
  "discounts": [
    { "name": "Regular Customer Tier Discount", "amount": 1500.0, ... }
  ]
}
Test 2: Buy-X-Get-Y (The Complex Feature)
Feature: BOGO Strategy.

Scenario: "Buy 2 Get 1 Free" on Shirts. Customer buys 3 Shirts @ 1000 each.

Pay for 2. Get 1 free.

Total Discount: 1000.

Step A: Create Rule (POST /api/v1/promotions/)

JSON
{
  "id": "BOGO_SHIRT",
  "name": "Buy 2 Get 1 Free on Shirts",
  "type": "BUY_X_GET_Y",
  "priority": 2,
  "conditions": {"sku": "SHIRT"},
  "action": {"buy_x": 2, "get_y": 1}
}
Step B: Calculate Bill (POST /api/v1/bills/calculate)

JSON
{
  "customer": {"id": "C1", "tier": "REGULAR"},
  "cart": {
    "items": [
      {"sku": "SHIRT", "name": "Formal Shirt", "category": "CLOTH", "quantity": 3, "unit_price": 1000}
    ]
  },
  "context": {"store_id": "MUM01"}
}
Expected Output:

JSON
{
  "gross_amount": 3000.0,
  "total_discount": 1000.0,
  "net_amount": 2000.0,
  "discounts": [ ... ]
}
Test 3: Category Discount (Extensibility Check)
Feature: Category-Based Strategy.

Scenario: Flat 20% off on "ELECTRONICS".

Step A: Create Rule (POST /api/v1/promotions/)

JSON
{
  "id": "ELEC20",
  "name": "20% Off Electronics",
  "type": "CATEGORY",
  "priority": 2,
  "conditions": {"category": "ELECTRONICS"},
  "action": {"rate": 0.20}
}
Step B: Calculate Bill (Same TV request as Test 1)

Expected Output: You should see stacking happen.

Slab Discount: 1500

Category Discount: 20% of 15000 = 3000

Total Discount: 4500 (1500 + 3000)

Test 4: System Health & Audit (The "Should Haves")
Feature: Audit Logs, Correlation IDs, Health Check.

Action: GET http://127.0.0.1:8000/health

Expected Output (Browser):

JSON
{ "status": "ok", "version": "1.1.0", "service": "PPE" }
Expected Output (Terminal Console): Look at your running terminal. You should see a log entry with a unique ID:

Plaintext
INFO: ... [Correlation-ID: a1b2c3d4-...] - AUDIT: Request Started: GET /health
Test 5: REST Compliance (PUT Update)
Feature: Strict RESTful API design.

Scenario: Update the existing "ELEC20" rule to be 50% off instead of 20%.

Action: PUT /api/v1/promotions/ELEC20

JSON
{
  "id": "ELEC20",
  "name": "50% Off Electronics",
  "type": "CATEGORY",
  "priority": 2,
  "conditions": {"category": "ELECTRONICS"},
  "action": {"rate": 0.50}
}
Expected Output: Status 200 OK and response body shows version: 2.