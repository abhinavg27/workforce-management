# Workforce Management System

A comprehensive workforce management and optimization system for warehouse logistics, consisting of multiple integrated services.

## System Architecture

This repository contains 5 main projects:

1. **Backend** - Spring Boot REST API (Java)
2. **Frontend** - React + TypeScript UI (Vite)
3. **Workforce Optimizer** - Python optimization microservice (FastAPI + OR-Tools)
4. **Chatbot** - AI-powered chatbot service (Flask + OpenAI)
5. **Forecast Backend** - Workforce forecasting service (Flask + ML)

---

## 1. Backend (Spring Boot)

### Description
Spring Boot backend providing REST APIs for workers, tasks, and assignments with MySQL database.

### Tech Stack
- Java 21
- Spring Boot 3.5.3
- MySQL
- Maven
- Flyway (DB migrations)

### Running Steps
```bash
cd backend

# Configure MySQL connection in src/main/resources/application.properties
# Ensure MySQL is running

# Build and run
mvn clean package
mvn spring-boot:run
```

### API Endpoints
- `GET /api/workers` - List workers
- `GET /api/tasks` - List tasks
- `GET /api/assignments/optimize` - Get current assignments
- `POST /api/assignments/optimize` - Re-optimize assignments

### Port
Default: `http://localhost:8080`

---

## 2. Frontend (React + TypeScript)

### Description
Modern React UI for workforce assignment visualization with Gantt charts and optimization controls.

### Tech Stack
- React
- TypeScript
- Vite
- MUI (Material UI)
- Redux

### Running Steps
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Port
Default: `http://localhost:5173` (dev mode)

---

## 3. Workforce Optimizer (Python FastAPI)

### Description
Python FastAPI microservice for advanced workforce assignment optimization using Google OR-Tools.

### Tech Stack
- Python 3.10+
- FastAPI
- Google OR-Tools
- Uvicorn

### Running Steps
```bash
cd workforce-optimizer

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn main:app --reload
# or
python3 -m uvicorn main:app --reload
```

### API Endpoints
- `POST /optimize` - Optimize workforce assignments

### Port
Default: `http://localhost:8000`

---

## 4. Chatbot (Flask + OpenAI)

### Description
Flask-based chatbot service integrating with OpenAI API for intelligent workforce data analysis.

### Tech Stack
- Python 3.8+
- Flask
- OpenAI API
- Flask-CORS

### Prerequisites
- OpenAI API key (set as environment variable)

### Running Steps
```bash
cd chatbot

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Start the service
python main.py
```

### API Endpoints
- `POST /analyze` - Analyze workforce data with AI

### Port
Default: `http://localhost:5000`

---

## 5. Forecast Backend (Flask + ML)

### Description
Workforce forecasting application using Linear Regression and LLM for predicting workforce needs during events.

### Tech Stack
- Python 3.8+
- Flask
- scikit-learn
- pandas, numpy
- OpenAI API
- Flask-CORS

### Prerequisites
- OpenAI API key
- Historical data CSV file

### Running Steps
```bash
cd forecast-backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure OpenAI API key and base URL in app.py

# Ensure historical data CSV is available

# Start the service
python3 app.py
```

### Port
Default: `http://localhost:5001` (check app.py for actual port)

---

## Complete System Startup

To run the entire system, start all services in the following order:

1. **Start MySQL Database** (required for backend)

2. **Start Backend**
   ```bash
   cd backend && mvn spring-boot:run
   ```

3. **Start Workforce Optimizer**
   ```bash
   cd workforce-optimizer && uvicorn main:app --reload
   ```

4. **Start Chatbot** (optional)
   ```bash
   cd chatbot && python main.py
   ```

5. **Start Forecast Backend** (optional)
   ```bash
   cd forecast-backend && python3 app.py
   ```

6. **Start Frontend**
   ```bash
   cd frontend && npm run dev
   ```

### Access Points
- Frontend UI: http://localhost:5173
- Backend API: http://localhost:8080
- Optimizer API: http://localhost:8000
- Chatbot API: http://localhost:5000
- Forecast API: http://localhost:5001

---

## Documentation

- Detailed FRD: See `FRD_Workforce_Management_System.md`
- Individual README files in each project folder

## License
MIT