"""
Trade Store Application - Complete Project Structure

Directory Structure:
trade-store/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── trade.py
│   │   └── schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── kafka_consumer.py
│   │   ├── trade_service.py
│   │   └── expiry_scheduler.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── postgres_repository.py
│   │   └── mongodb_repository.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── exceptions.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_trade_service.py
│   ├── test_repositories.py
│   ├── test_api.py
│   └── test_kafka_consumer.py
├── diagrams/
│   ├── sequence_diagram.puml
│   ├── class_diagram.puml
│   └── architecture_diagram.puml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
"""