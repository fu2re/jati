ISORT := isort -m 3 -e

VIRTUAL_ENV_CHECK := import sys;b=hasattr(sys, \"real_prefix\");r=hasattr(sys, \"base_prefix\");print(b or (r and sys.base_prefix != sys.prefix))
VIRTUAL_ENV := $(shell echo "$(VIRTUAL_ENV_CHECK)" | python)

RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(RUN_ARGS):;@:)

.PHONY: build
build:
ifeq ($(VIRTUAL_ENV), True)
	@poetry install
else
	@docker-compose build
endif

.PHONY: install
install: build

.PHONY: run
run:
ifeq ($(VIRTUAL_ENV), True)
	@uvicorn main:app --reload
else
	@docker-compose up -d
endif

.PHONY: stop
stop:
ifeq ($(VIRTUAL_ENV), True)
	@echo "does not run"
else
	@docker-compose down
endif

.PHONY: restart
restart:
ifeq ($(VIRTUAL_ENV), True)
	@echo "does not run"
else
	@docker-compose down && docker-compose up -d
endif

.PHONY: test
test:
ifeq ($(VIRTUAL_ENV), True)
	@pytest tests
else
	docker-compose run --rm python -m pytest
endif

.PHONY: lint
lint:
ifeq ($(VIRTUAL_ENV), True)
	@flake8 wallet
else
	@docker-compose run --rm $(CONTAINER_NAME) flake8 wallet
endif

.PHONY: sort
sort:
ifeq ($(VIRTUAL_ENV), True)
	$(ISORT) wallet
else
	@docker-compose run --rm $(ISORT)
endif

.PHONY: migrations
migrations:
	@alembic revision -m "auto" --autogenerate --head head
	@git add alembic/versions/.

.PHONY: migrate
migrate:
	@alembic upgrade head

.PHONY: clean
clean: clean-build clean-pyc

.PHONY: clean-build
clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} + clean-pyc