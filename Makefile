#!make
include .env
export $(shell sed 's/=.*//' .env)

COMPOSE = docker-compose -f ${DOCKER_COMPOSE_FILE}
BASE_COMMAND = ${COMPOSE} run --rm ${SERVICE_NAME}
COMMAND = ${BASE_COMMAND}  /bin/bash -c


up:
	${COMPOSE} up --build

down:
	${COMPOSE} down

migrate:
	${COMMAND} 'alembic upgrade head'

makemigrations:
	$(COMMAND) "alembic revision --autogenerate --message='$(call args)'"

downgrade:
	$(COMMAND) "alembic downgrade -1"

test:
	${COMMAND} 'pytest'

shell:
	${COMMAND} 'bash'

flake8:
	${COMMAND} 'cd /app && flake8'

mypy:
	${COMMAND} 'cd /app && mypy .'
