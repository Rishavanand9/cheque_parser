# Variables
DOCKER_COMPOSE = docker-compose
DC_FILE = docker-compose.yml

# Phony targets
.PHONY: build up down restart logs ps clean

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