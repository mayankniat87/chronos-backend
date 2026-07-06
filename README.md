# Project Chronos - Backend

**Explainable Business Time Machine API for SME Restaurant Simulations**

Chronos is a powerful backend system designed to help small and medium-sized restaurant businesses understand and simulate their operational decisions. Using advanced graph-based modeling and AI-powered explanations, Chronos helps restaurant owners explore "what-if" scenarios and make data-driven decisions.

## 🎯 Features

- **Data Onboarding**: Import restaurant operational data (customers, inventory, orders, staff, expenses)
- **Graph-Based Business Modeling**: Build and analyze business entity relationships
- **Decision Service**: Evaluate business decisions with confidence scoring
- **Scenario Simulation**: Run "what-if" simulations to predict outcomes
- **Explainable AI**: Get AI-powered explanations for decisions using Gemini
- **Rule Engine**: Define and execute business rules
- **Health Monitoring**: Built-in health check endpoints

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Data Processing**: Pandas, OpenPyXL
- **ML/AI**: Google Gemini API
- **Data Validation**: Pydantic
- **Graph Processing**: NetworkX

## 📋 Prerequisites

- Python 3.8+
- Git
- pip or conda

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mayankniat87/chronos-backend.git
   cd chronos-backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration:
   ```env
   DATABASE_URL=sqlite:///./chronos.db
   # Or for PostgreSQL:
   # DATABASE_URL=postgresql://user:password@localhost/chronos
   
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

## 🎬 Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**Interactive API Documentation**: `http://localhost:8000/docs` (Swagger UI)

## 📁 Project Structure

```
chronos-backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API route handlers
│   │   ├── routes_upload.py    # Data upload endpoints
│   │   ├── routes_graph.py     # Graph building endpoints
│   │   ├── routes_decision.py  # Decision service endpoints
│   │   └── routes_health.py    # Health check endpoints
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   └── database.py         # Database setup and session management
│   ├── models/                 # SQLAlchemy ORM models
│   │   └── restaurant.py       # Restaurant data models
│   ├── schemas/                # Pydantic validation schemas
│   │   └── restaurant.py       # Request/response schemas
│   └── services/               # Business logic services
│       ├── build_graph.py      # Graph building logic
│       ├── decision_service.py # Decision evaluation
│       └── simulation/         # Simulation engines
│           ├── confidence_calculator.py
│           ├── explain.py
│           ├── rule_engine.py
│           └── scenario_generator.py
├── scripts/
│   └── generate_seed_data.py   # Data generation utilities
├── seed_data/                  # Sample data CSVs and Excel files
├── tests/                      # Test suite
│   ├── test_live_api.py
│   └── test_onboarding.py
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (ignored by Git)
└── README.md                   # This file
```

## 🔌 API Endpoints

### Health Check
- `GET /health` - Check API status

### Data Upload & Onboarding
- `POST /upload/restaurants` - Upload restaurant data
- `POST /upload/orders` - Upload order history
- `POST /upload/inventory` - Upload inventory data
- `POST /upload/customers` - Upload customer data
- `POST /upload/staff` - Upload staff information
- `POST /upload/expenses` - Upload expense records

### Graph Operations
- `POST /graph/build` - Build business relationship graph
- `GET /graph/{restaurant_id}` - Retrieve restaurant graph
- `GET /graph/{restaurant_id}/analyze` - Analyze graph metrics

### Decision Service
- `POST /decision/evaluate` - Evaluate a business decision
- `GET /decision/{decision_id}` - Get decision details with explanation
- `POST /decision/{decision_id}/confidence` - Calculate decision confidence

### Simulation
- `POST /simulate/scenario` - Run scenario simulation
- `GET /simulate/{simulation_id}/results` - Get simulation results

## 🗄️ Database Setup

The application automatically creates database schemas on startup.

**For SQLite** (default):
- Database file: `chronos.db`
- Automatically created in the project root

**For PostgreSQL**:
```bash
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/chronos
```

## 📊 Sample Data

Generate sample data for testing:

```bash
python scripts/generate_seed_data.py
```

This will populate the `seed_data/` directory with sample CSVs and Excel files.

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run live API tests:
```bash
python tests/test_live_api.py
```

## 🔐 Security Notes

- ⚠️ **CORS**: Currently allows all origins (`*`). Restrict to specific domains in production.
- ⚠️ **API Keys**: Never commit `.env` files or API keys to version control.
- ⚠️ **Database**: Use strong credentials for PostgreSQL in production.

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 💬 Support

For issues, questions, or suggestions, please open an issue on GitHub or contact the development team.

---

**Last Updated**: July 2026  
**Version**: 1.0.0
