# Functional Requirements Document (FRD)
## Workforce Management System

**Document Version:** 1.0  
**Date:** August 5, 2025  
**Project:** Workforce Management and Optimization System for Logistics Operations  

---

## 1. Executive Summary

The Workforce Management System is a comprehensive solution designed to optimize workforce allocation and task scheduling in logistics warehouse operations. The system integrates advanced optimization algorithms with real-time assignment management capabilities to maximize operational efficiency while ensuring worker capacity constraints and skill requirements are met.

## 2. System Overview

### 2.1 System Architecture
The system follows a microservices architecture with the following components:
- **Frontend**: React TypeScript application with Material-UI components
- **Backend**: Spring Boot REST API with MySQL database
- **Optimization Engine**: Python FastAPI microservice using Google OR-Tools
- **Additional Services**: Chatbot and forecasting modules

### 2.2 Core Technologies
- **Backend**: Java 21, Spring Boot 3.5.3, MySQL, Flyway migrations
- **Frontend**: React 18, TypeScript, Vite, Material-UI, Redux Toolkit
- **Optimization**: Python 3.10+, FastAPI, Google OR-Tools CP-SAT solver
- **Database**: MySQL with comprehensive schema for workers, tasks, and assignments

## 3. Functional Requirements

### 3.1 Worker Management

#### 3.1.1 Worker Registration and Profile Management
- **FR-WM-001**: System shall allow creation of worker profiles with unique 7-character worker IDs
- **FR-WM-002**: System shall store worker demographics including name and age
- **FR-WM-003**: System shall support multiple skill assignments per worker with skill levels (1-4) and productivity ratings (0-100%)
- **FR-WM-004**: System shall manage worker shift schedules across different days of the week
- **FR-WM-005**: System shall support multiple shift templates (Morning 08:00-16:00, Evening 16:00-00:00, Night 00:00-08:00, Day Short 09:00-15:00, Late Start 10:00-18:00)

#### 3.1.2 Skill Management
- **FR-WM-006**: System shall maintain a master list of skills categorized by process skill sub-categories
- **FR-WM-007**: Skills shall be categorized into functional groups: In (7000), Out (7001/8000), Sort (7002), Pick (8000), Rebin (8001), Pack (8002), Other (3001/3002)
- **FR-WM-008**: System shall track skill proficiency levels and productivity metrics per worker-skill combination

#### 3.1.3 Worker Data Visualization
- **FR-WM-009**: System shall provide tabular view of all workers with their skills and shift information
- **FR-WM-010**: System shall display skill levels using visual indicators (color-coded chips)
- **FR-WM-011**: System shall support worker selection and bulk operations

### 3.2 Task Management

#### 3.2.1 Task Definition and Configuration
- **FR-TM-001**: System shall support creation of tasks with unique task IDs and descriptive names
- **FR-TM-002**: System shall categorize tasks by type (In, Out, Sort, Pick, Rebin, Pack, Other) based on required skills
- **FR-TM-003**: System shall assign priority levels (1-9) to tasks for optimization ordering
- **FR-TM-004**: System shall support task count specification (number of units to be completed)
- **FR-TM-005**: System shall manage task dependencies through dependent task ID relationships

#### 3.2.2 Task Data Management
- **FR-TM-006**: System shall maintain mapping between tasks and required skills
- **FR-TM-007**: System shall support task CRUD operations with validation
- **FR-TM-008**: System shall provide task listing with filtering and sorting capabilities
- **FR-TM-009**: System shall support bulk task operations (selection, deletion)

### 3.3 Assignment Optimization

#### 3.3.1 Optimization Engine Requirements
- **FR-AO-001**: System shall integrate with Python-based optimization engine using Google OR-Tools CP-SAT solver
- **FR-AO-002**: System shall optimize assignments based on multiple criteria:
  - Worker skill matching
  - Productivity levels
  - Task priorities
  - Shift constraints
  - Break requirements (60 minutes after 4 hours)
  - Task dependencies
- **FR-AO-003**: System shall support task splitting across multiple workers when beneficial
- **FR-AO-004**: System shall ensure no worker overlap in assigned time slots
- **FR-AO-005**: System shall automatically schedule mandatory breaks for each worker

#### 3.3.2 Assignment Management
- **FR-AO-006**: System shall persist optimized assignments in the database
- **FR-AO-007**: System shall support manual assignment removal and reassignment
- **FR-AO-008**: System shall track assignment status (PENDING, ACCEPTED, REJECTED)
- **FR-AO-009**: System shall capture worker feedback on rejected assignments
- **FR-AO-010**: System shall maintain historical assignment data

#### 3.3.3 Unassigned Task Tracking
- **FR-AO-011**: System shall identify and track tasks that cannot be assigned due to constraints
- **FR-AO-012**: System shall report reasons for unassigned tasks (skill mismatch, capacity constraints, time limitations)
- **FR-AO-013**: System shall maintain unassigned task queue with remaining unit counts

### 3.4 Gantt Chart Visualization

#### 3.4.1 Visual Assignment Display
- **FR-GV-001**: System shall display assignments in Gantt chart format with 24-hour timeline
- **FR-GV-002**: System shall show worker names and shift information alongside assignment bars
- **FR-GV-003**: System shall use color coding for different task types with legend
- **FR-GV-004**: System shall display task details on hover (task name, units, time range)
- **FR-GV-005**: System shall show shift start/end markers for each worker
- **FR-GV-006**: System shall highlight current time with dashed line indicator

#### 3.4.2 Interactive Features
- **FR-GV-007**: System shall support click-to-view task details in modal dialog
- **FR-GV-008**: System shall allow assignment removal through task detail modal
- **FR-GV-009**: System shall support assignment export functionality
- **FR-GV-010**: System shall filter out night shift workers from main display (20:00-06:00)

#### 3.4.3 Accessibility and Usability
- **FR-GV-011**: System shall provide keyboard navigation support
- **FR-GV-012**: System shall include ARIA labels for screen reader compatibility
- **FR-GV-013**: System shall display assignments without overlap using intelligent lane assignment
- **FR-GV-014**: System shall show unassigned tasks in separate dedicated section

### 3.5 Dashboard and Reporting

#### 3.5.1 Assignment Overview
- **FR-DR-001**: System shall provide dashboard with assignment optimization status
- **FR-DR-002**: System shall display key metrics: total assignments, unassigned tasks, worker utilization
- **FR-DR-003**: System shall show real-time optimization results
- **FR-DR-004**: System shall support re-optimization triggers

#### 3.5.2 Unassigned Task Management
- **FR-DR-005**: System shall display unassigned tasks in tabular format with task ID, name, and remaining units
- **FR-DR-006**: System shall provide visual indicators for unassigned task priority
- **FR-DR-007**: System shall allow manual review and reassignment of unassigned tasks

### 3.6 Data Management and Persistence

#### 3.6.1 Database Operations
- **FR-DM-001**: System shall use transactional operations for assignment updates
- **FR-DM-002**: System shall support database migrations through Flyway
- **FR-DM-003**: System shall maintain referential integrity across all entities
- **FR-DM-004**: System shall store shift information within assignment records for audit purposes

#### 3.6.2 API Integration
- **FR-DM-005**: System shall provide RESTful APIs for all CRUD operations
- **FR-DM-006**: System shall support JSON data exchange between frontend and backend
- **FR-DM-007**: System shall maintain API endpoints for optimization triggers
- **FR-DM-008**: System shall provide WebSocket support for real-time updates

### 3.7 Additional Modules

#### 3.7.1 Forecasting Module
- **FR-FM-001**: System shall include workforce forecasting capabilities using historical data
- **FR-FM-002**: System shall predict future workforce requirements based on historical patterns
- **FR-FM-003**: System shall integrate forecasting results with assignment optimization

#### 3.7.2 Chatbot Integration
- **FR-CB-001**: System shall provide chatbot interface for common workforce queries
- **FR-CB-002**: System shall support natural language queries about assignments and availability
- **FR-CB-003**: System shall integrate chatbot responses with real-time system data

## 4. Non-Functional Requirements

### 4.1 Performance Requirements
- **NF-PERF-001**: System shall process optimization requests within 30 seconds for up to 100 workers and 1000 tasks
- **NF-PERF-002**: System shall support concurrent user access with response times under 2 seconds
- **NF-PERF-003**: Gantt chart shall render smoothly for up to 50 workers simultaneously

### 4.2 Scalability Requirements
- **NF-SCALE-001**: System architecture shall support horizontal scaling of microservices
- **NF-SCALE-002**: Database shall support growth to 10,000+ workers and 100,000+ daily tasks
- **NF-SCALE-003**: Frontend shall handle large datasets through pagination and virtual scrolling

### 4.3 Reliability Requirements
- **NF-REL-001**: System shall maintain 99.5% uptime during operational hours
- **NF-REL-002**: Optimization engine shall provide fallback mechanisms for solver failures
- **NF-REL-003**: System shall include error handling and recovery mechanisms

### 4.4 Security Requirements
- **NF-SEC-001**: System shall implement secure API endpoints with authentication
- **NF-SEC-002**: System shall protect sensitive worker and operational data
- **NF-SEC-003**: System shall maintain audit logs for all assignment changes

### 4.5 Usability Requirements
- **NF-USE-001**: System shall provide intuitive user interface following Material Design principles
- **NF-USE-002**: System shall support responsive design for desktop and tablet devices
- **NF-USE-003**: System shall include comprehensive error messages and user guidance

## 5. Data Requirements

### 5.1 Core Entities
- **Workers**: Worker ID, name, age, skills, shifts, productivity metrics
- **Tasks**: Task ID, name, type, priority, skill requirements, dependencies, unit counts
- **Assignments**: Assignment ID, worker-task mapping, time slots, status, feedback
- **Skills**: Skill ID, name, categories, process codes
- **Shifts**: Shift templates, time ranges, break durations

### 5.2 Data Relationships
- Many-to-many relationship between workers and skills
- Many-to-many relationship between workers and shifts
- One-to-many relationship between tasks and assignments
- Hierarchical task dependencies through parent-child relationships

### 5.3 Data Volume Estimates
- **Workers**: 100-1000 active workers
- **Tasks**: 1000-10000 daily tasks
- **Assignments**: 5000-50000 daily assignments
- **Historical Data**: 1-year retention for optimization learning

## 6. Integration Requirements

### 6.1 Internal Integration
- **Backend-Frontend**: RESTful API communication with JSON payloads
- **Backend-Optimizer**: HTTP API calls to Python FastAPI service
- **Database Integration**: MyBatis for ORM with XML mapping configurations

### 6.2 External Integration Capabilities
- **ERP Systems**: API endpoints for workforce data synchronization
- **Time Tracking**: Integration points for actual vs. planned time tracking
- **Reporting Systems**: Data export capabilities for business intelligence tools

## 7. Constraints and Assumptions

### 7.1 Technical Constraints
- **Programming Languages**: Java 21 for backend, Python 3.10+ for optimization, TypeScript for frontend
- **Database**: MySQL as primary data store
- **Deployment**: Containerized deployment with Docker support
- **Optimization**: Google OR-Tools CP-SAT solver dependency

### 7.2 Business Constraints
- **Operating Hours**: System optimized for warehouse operating hours (day/evening shifts primarily)
- **Skill Categories**: Fixed skill categorization aligned with warehouse processes
- **Break Requirements**: Mandatory 60-minute breaks after 4 hours of work

### 7.3 Assumptions
- **Worker Availability**: Workers are available during their assigned shifts
- **Skill Accuracy**: Worker skill levels and productivity data are accurately maintained
- **Task Data**: Task requirements and dependencies are correctly specified
- **Network Connectivity**: Reliable network connectivity between microservices

## 8. Success Criteria

### 8.1 Functional Success Criteria
- **Assignment Optimization**: 95% of tasks successfully assigned to qualified workers
- **Constraint Satisfaction**: 100% compliance with worker capacity and skill constraints
- **Dependency Resolution**: 100% of task dependencies properly sequenced
- **User Interface**: Intuitive Gantt chart visualization with sub-second interaction response

### 8.2 Performance Success Criteria
- **Optimization Speed**: Complete optimization within 30 seconds for standard workload
- **System Response**: Frontend interactions complete within 2 seconds
- **Data Accuracy**: 100% data consistency between optimization engine and database

### 8.3 Business Success Criteria
- **Operational Efficiency**: 20% improvement in task completion rates
- **Worker Utilization**: 85%+ average worker utilization during shifts
- **Manual Intervention**: 50% reduction in manual assignment adjustments

---

## Appendix A: API Endpoints

### Assignment Optimization Controller
- `GET /api/assignments/optimize` - Retrieve current assignments
- `POST /api/assignments/optimize` - Trigger re-optimization
- `POST /api/assignments/optimize/remove` - Remove specific assignment
- `POST /api/assignments/optimize/{id}/accept` - Accept assignment
- `POST /api/assignments/optimize/{id}/reject` - Reject assignment with feedback

### Core Management Controllers
- `GET /api/workers` - List workers with skills and shifts
- `POST /api/workers` - Create new worker
- `GET /api/tasks` - List tasks with dependencies
- `POST /api/tasks` - Create new task
- `GET /api/skills` - List available skills
- `GET /api/shifts` - List shift templates

### Python Optimization Service
- `POST /optimize` - Optimize worker-task assignments using CP-SAT solver

## Appendix B: Database Schema Summary

### Core Tables
- `worker` - Worker master data
- `task` - Task definitions and requirements
- `assignment` - Current assignment state
- `skill_master` - Skill definitions and categories
- `worker_skill` - Worker-skill relationships with proficiency
- `shift_template` - Shift time templates
- `worker_shift` - Worker-shift assignments by day
- `unassigned_task` - Tasks that could not be assigned

### Key Relationships
- Workers have multiple skills with varying proficiency levels
- Workers are assigned to shifts on specific days of the week
- Tasks require specific skills and may have dependencies
- Assignments link workers to tasks with time slots and completion status

---

**Document Prepared By:** AI Assistant  
**Review Status:** Draft  
**Next Review Date:** TBD