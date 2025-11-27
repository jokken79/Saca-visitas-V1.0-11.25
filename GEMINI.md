# UNS Visa Management System Project Context

This document provides a comprehensive overview of the "UNS Visa Management System" project to guide future development and analysis.

## 1. Project Overview

This is a full-stack web application designed as a Human Resources Information System (HRIS) for Japanese staffing agencies (派遣会社). Its primary purpose is to manage employee data, visa information, client companies (派遣先), and employment contracts.

The application is architected as a multi-container system orchestrated by Docker Compose.

### Core Technologies
- **Backend:** Python with the **FastAPI** framework.
- **Frontend:** Static **HTML, JavaScript, and CSS (Tailwind CSS)**. There is no complex frontend build system (like React, Vue, etc.).
- **Database:** **PostgreSQL**.
- **Web Server / Reverse Proxy:** **Nginx**, which serves the static frontend files and proxies API requests to the FastAPI backend.
- **Caching:** **Redis** is included for caching and session management.
- **Containerization:** **Docker** and **Docker Compose**.

### Directory Structure
- `backend/`: Contains the FastAPI application source code.
- `frontend/`: Contains all static frontend assets (HTML, JS, CSS).
- `database/`: Holds the database initialization script (`init.sql`).
- `nginx/`: Contains the Nginx configuration.
- `docker-compose.yml`: Defines all the services, networks, and volumes.
- `README.md`: The primary source of project information.

## 2. Building and Running the Project

The entire application is designed to be run via Docker Compose.

### To Start the Application:
1.  Navigate to the project root directory.
2.  Run the following command:
    ```bash
    docker compose up -d --build
    ```

### Accessing Services:
Once running, the services are available at the following custom ports:
- **Frontend Application:** `http://localhost:8180`
- **Backend API Docs (Swagger UI):** `http://localhost:8100/docs`
- **Database Admin (Adminer):** `http://localhost:8181`
- **PostgreSQL Database Port:** `5433`
- **Redis Port:** `6380`

## 3. Development Conventions

- **Separation of Concerns:** The project maintains a strict separation between the backend API (`backend` service) and the frontend application (`frontend` service).
- **API-Driven:** The static frontend communicates with the backend exclusively through the REST API exposed by FastAPI.
- **Database Schema:** The initial database schema is defined in `database/init.sql` and is automatically loaded when the PostgreSQL container starts for the first time.
- **Reverse Proxy:** Nginx is configured in `nginx/nginx.conf`. It handles routing requests starting with `/api/` to the FastAPI backend and serves the static files from the `frontend/` directory for all other requests.
- **Environment Variables:** Configuration for database passwords and other secrets is handled via environment variables, with defaults specified in `docker-compose.yml` and a template in `.env.example`.
- **No Automated Tests:** The `README.md` explicitly states that there are no automated test suites. Testing is expected to be done manually.
