## Restaurant Order System (Modular + Real-time)

Production-grade backend scaffold:

- **API**: FastAPI (REST) + Socket.IO (WebSockets)
- **DB**: MongoDB (Motor)
- **Cache/Broker**: Redis (cache + pub/sub)
- **Auth**: JWT access + refresh (RBAC-ready)
- **Multi-tenant**: `restaurantId` is required and scoped through all domain queries

### Folder structure

```
app/
  main.py
  core/
    config.py
    security.py
    errors.py
    logging.py
  db/
    mongo.py
    redis.py
  middlewares/
    rbac.py
    tenant.py
  events/
    bus.py
    types.py
    socket.py
  modules/
    auth/
      router.py
      service.py
      models.py
    orders/
      router.py
      service.py
      models.py
    products/
      router.py
      service.py
      models.py
    inventory/
      router.py
      service.py
      models.py
    payments/
      router.py
      service.py
      models.py
    analytics/
      router.py
      service.py
      models.py
```

### Run locally (Docker)

1) Create `.env` (copy from `.env.example`)
2) Start services:

```bash
docker compose up --build
```

- REST docs at `http://localhost:8000/docs`
- Socket.IO at `http://localhost:8000/socket.io/`

### Core real-time events

- `OrderCreated`
- `OrderUpdated`
- `PaymentCompleted`
- `InventoryLow` (stubbed)

