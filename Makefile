PYTHON=python3
PKG_NAME=app

ROOT_DIR:=$(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
VENV=$(ROOT_DIR)/venv
flake8=$(VENV)/bin/flake8
pip=$(VENV)/bin/pip3
pytest=$(VENV)/bin/pytest
bandit=$(VENV)/bin/bandit
black=$(VENV)/bin/black
python=$(VENV)/bin/$(PYTHON)

$(VENV):
	cp scripts/pre-commit .git/hooks/
	$(PYTHON) -m venv $(VENV)

$(VENV)/bin/$(PKG_NAME): $(VENV)
	$(pip) install .

venv: $(VENV)

install: $(VENV)/bin/$(PKG_NAME)

dev-install: $(pytest)

$(pytest): $(VENV)
	$(pip) install -e .[dev]

lint: $(pytest)
	$(black) $(PKG_NAME)
	$(flake8) $(PKG_NAME) --ignore E501,W605,F841

test: $(pytest)
	$(pytest) -v --cov-branch --cov=tests/unit --cov-report=term
	coverage report -m --fail-under=50

scan:
	$(bandit) -lll -r app/

run:
	$(VENV)/bin/$(PKG_NAME) run

clean:
	rm -rf $(VENV)
	rm -rf dist
	rm -rf $(PKG_NAME).egg-info

docker-start-dev-env:
	docker build -t datacurator-sentiment .
	docker run --entrypoint /bin/sh -v $(CURDIR):/src --name datacurator-sentiment-dev-env -itd datacurator-sentiment
	docker exec datacurator-sentiment-dev-env pip3 install -e .[dev]
	docker attach datacurator-sentiment-dev-env

docker-stop-dev-env:
	docker stop datacurator-sentiment-dev-env
	docker rm datacurator-sentiment-dev-env

docker-build:
	docker build -t datacurator-sentiment .

docker-run:
	docker container run -p 5000:5000 --name datacurator-sentiment -td datacurator-sentiment 
	docker ps -l

docker-stop:
	docker stop datacurator-sentiment

docker-remove:
	docker rmi -f datacurator-sentiment
