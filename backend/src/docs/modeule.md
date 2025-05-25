```
cookie-violations-checker/
├── api/                  # Main API endpoints
│   ├── __init__.py
│   ├── app.py            # FastAPI main application
│   ├── middleware.py     # Auth, logging, rate limiting
│   ├── routes.py         # Route definitions
│   └── models.py         # Data models for API
│
├── services/                 # Core functionality modules
│   ├── __init__.py
│   ├── policy_finder.py      # Finding policy URLs
│   ├── content_extractor.py  # Extracting policy content
│   ├── feature_analyzer.py   # Analyzing policy features with LLM
│   ├── cookie_collector.py   # Collecting actual cookies
│   ├── violation_detector.py # Detecting violations
│   └── report_generator.py   # Generating reports
│
├── database/               # Quản lý kết nối và thao tác với database
│   ├── __init__.py
│   ├── connection.py       # Kết nối đến database
│   ├── schema.py           # Định nghĩa schema
│   ├── migrations/         # Quản lý các phiên bản schema
│   └── repositories/       # Các lớp repository tương tác với từng entity
│       ├── __init__.py
│       ├── policy_repo.py
│       ├── cookie_repo.py
│       ├── violation_repo.py
│       └── report_repo.py
│
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── html_parser.py    # HTML parsing utilities
│   ├── text_processor.py # Text processing
│   ├── llm_client.py     # LLM integration
│   └── logger.py         # Logging utilities
│
├── models/               # Data models
│   ├── __init__.py
│   ├── policy.py         # Policy data models
│   ├── cookies.py        # Cookie data models
│   ├── features.py       # Feature data models
│   └── violations.py     # Violation data models
│
├── config/               # Configuration
│   ├── __init__.py
│   └── settings.py       # Application settings
││
├── docs/                 # Documentation
│   ├── architecture.md
│   ├── api_reference.md
│   └── user_guide.md
│
├── tests/                # Tests
│   ├── __init__.py
│   ├── test_policy_finder.py
│   ├── test_content_extractor.py
│   └── test_violation_detector.py
│
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker configuration
└── README.md             # Project README
```
