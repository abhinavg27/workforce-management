# Workforce Management Optimization System - Backend

Spring Boot backend for workforce assignment optimization in warehouse logistics.

## Features
- Java 21, Maven, Spring Boot 3.5.3
- MySQL (or compatible) with Flyway migrations (see `db/migration/`)
- REST APIs for workers, tasks, assignments
- Integration with Python FastAPI microservice for advanced optimization
- Modular, testable structure
- Real-time updates (WebSocket, optional)
- JWT/OAuth2 security (optional)

## Running the Backend
1. Ensure MySQL is running and configured in `src/main/resources/application.properties`.
2. Run Flyway migrations (auto on startup).
3. Build and start:
   ```sh
   mvn clean package
   mvn spring-boot:run
   ```

## API Endpoints
- `GET /api/workers` - List workers
- `GET /api/tasks` - List tasks
- `GET /api/assignments/optimize` - Get current assignments (Gantt format)
- `POST /api/assignments/optimize` - Re-optimize assignments (calls Python, updates DB)

## Integration with Python Optimizer
- The backend calls the Python FastAPI microservice for assignment optimization.
- Results are persisted in the assignment table and served to the frontend.

## Development
- Use Java 21+
- See `src/main/resources/application.properties` for DB config

## License
MIT
