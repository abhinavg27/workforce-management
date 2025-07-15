# Workforce Management Optimization System - Backend

This is a Spring Boot 3.1.5 backend for a workforce task assignment optimization system for warehouse logistics operations.

## Features
- Java 17, Maven, Spring Boot 3.1.5
- Google OR-Tools integration (for optimization logic)
- PostgreSQL with Flyway migrations
- MapStruct for DTO mapping
- WebSocket (STOMP) for real-time updates
- JWT/OAuth2 security (basic config, extend as needed)
- Modular, testable structure
- REST APIs for workers, tasks, assignments
- Analytics endpoints (to be implemented)
- Validation, error handling, CORS config
- Sample data loader

## Getting Started

1. **Configure PostgreSQL**
   - Ensure PostgreSQL is running and accessible at `localhost:5432/wmsdb` (see `application.properties`).
   - Update username/password as needed.
2. **Build and Run**
   ```sh
   mvn clean spring-boot:run
   ```
3. **API Endpoints**
   - `GET /api/workers`, `POST /api/workers`, ...
   - `GET /api/tasks`, ...
   - `GET /api/assignments`, ...

4. **WebSocket**
   - Connect to `/ws` endpoint (STOMP/SockJS)

5. **Flyway Migrations**
   - On startup, DB schema is auto-migrated.

## Development
- Use Java 17+
- See `src/main/resources/application.properties` for config
- Extend security, analytics, and optimization logic as needed

## License
MIT
