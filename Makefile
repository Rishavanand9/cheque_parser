# Variables
DOCKER_COMPOSE = docker-compose
DC_FILE = docker-compose.yml

# Phony targets
.PHONY: build up down restart logs ps clean frontend frontend-rebuild backend backend-rebuild frontend-logs backend-logs

# Build or rebuild services
build:
	@echo "Building services..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) build

# Create and start containers
up:
	@echo "Starting services..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) up -d

# Stop and remove containers, networks
down:
	@echo "Stopping and removing services..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) down

# Restart services
restart: down up

# View output from containers
logs:
	@echo "Showing logs..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) logs -f

# List containers
ps:
	@echo "Listing containers..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) ps

# Remove stopped containers and unused images
clean:
	@echo "Cleaning up..."
	docker system prune -f

# Frontend service management
frontend:
	@echo "Starting frontend service..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) up -d frontend

frontend-rebuild:
	@echo "Rebuilding frontend service..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) up -d --build frontend

frontend-down:
	@echo "Stopping frontend service..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) stop frontend

frontend-logs:
	@echo "Showing logs for frontend service..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) logs -f frontend

# Backend service management
backend:
	@echo "Starting backend service..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) up -d backend

backend-rebuild:
	@echo "Rebuilding backend service..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) up -d --build backend

backend-down:
	@echo "Stopping backend service..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) stop backend

backend-logs:
	@echo "Showing logs for backend service..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) logs -f backend
