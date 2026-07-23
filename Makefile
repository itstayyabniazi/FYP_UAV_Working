# ======================================================
# FYP UAV Development Makefile
# ======================================================

PROJECT_DIR=./docker

build:
	cd $(PROJECT_DIR) && docker compose build

rebuild:
	cd $(PROJECT_DIR) && docker compose build --no-cache

up:
	cd $(PROJECT_DIR) && docker compose up -d

down:
	cd $(PROJECT_DIR) && docker compose down

restart:
	cd $(PROJECT_DIR) && docker compose down && docker compose up -d

shell:
	cd $(PROJECT_DIR) && docker compose exec fyp-uav bash

logs:
	cd $(PROJECT_DIR) && docker compose logs -f

status:
	cd $(PROJECT_DIR) && docker compose ps
