Promotional Pricing Engine.

1. 🧠 Core Discount Logic (The "Brain")
Progressive Slab Discounts: Calculates tiered discounts (e.g., first ₹5k @ 0%, next ₹5k @ 10%) correctly handling the "split" logic.

Buy-X-Get-Y (BOGO): Automatic logic for "Buy 2 Get 1 Free" style offers on specific items.

Category-Based Discounts: Rules that target specific groups (e.g., "Flat 20% off on Electronics").

Flat & Percentage Rules: Standard coupons for fixed amounts (₹500 off) or rates (15% off).

Discount Stacking: Smart logic to apply rules in priority order (e.g., Tier Discount first, then Coupon).

Caps & Limits: Enforces max_discount_amount (e.g., "10% off up to ₹200").

Stackability Control: A stackable=False flag that prevents exclusive coupons from combining with others.

Time-Based Validity: Logic to check valid_from and valid_to timestamps (e.g., Happy Hour).

Precision Math: Uses Python Decimal for all currency math to avoid floating-point errors.

2. 🔌 API Endpoints (100% Coverage)
We implemented every endpoint requested in the assignment:

Bill Calculation

POST /api/v1/bills/calculate: The main engine that accepts a cart and returns the final bill with a breakdown of savings.

Promotion Management

POST /api/v1/promotions/: Create new rules dynamically.

GET /api/v1/promotions/: List all active/inactive rules.

GET /api/v1/promotions/{id}: View details of a specific rule.

PUT /api/v1/promotions/{id}: Update an existing rule (Strict REST compliance).

DELETE /api/v1/promotions/{id}: Soft delete a rule.

POST /api/v1/promotions/{id}/activate: Instantly enable a rule.

POST /api/v1/promotions/{id}/deactivate: Instantly disable a rule.

POST /api/v1/promotions/simulate: "Dry run" a rule to preview results without saving it.

Customer Tiers

GET /api/v1/customer-tiers/: See current tier thresholds.

POST /api/v1/customer-tiers/: Add new customer tiers.

PUT /api/v1/customer-tiers/{name}: Update tier configurations.

System

GET /health: Returns service status and version.

3. 🛡️ System Design & Quality (The "Should Haves")
Clean Architecture: Code is separated into api (routes), core (logic), and models (data).

Strategy Pattern: Discounts are implemented as separate classes (SlabDiscount, BogoDiscount), making the system easily extensible.

Concurrency Handling: Uses asyncio.Lock to ensure two admins cannot update rules at the exact same millisecond (Thread Safety).

Versioning Strategy: Every time a rule is updated, its version number automatically increments.

Audit Trail: Middleware logs every incoming request method and URL.

Structured Logging: Every request is assigned a unique X-Correlation-ID that appears in the logs for debugging.

Validation: Pydantic v2 automatically rejects bad data (e.g., negative prices, missing fields).

In-Memory Database: Runs locally with zero setup but is designed to be swappable.

4. 🧪 Testing & DevOps
Automated Test Suite:

Unit Tests: Verify the specific math of Slabs and BOGO.

Integration Tests: Verify the API accepts JSON and returns 200 OK.

Async Testing: Configured pytest-asyncio to test the concurrent DB.

Documentation:

Swagger UI: Interactive API docs at /docs.

Markdown: README.md (Setup), DESIGN.md (Architecture decisions), SUBMISSION.md (Project summary).

Docker: A Dockerfile is included to run the entire application with a single command.