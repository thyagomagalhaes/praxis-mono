.PHONY: up down restart reup logs tail postgres-up postgres-down postgres-logs nginx-manager-up nginx-manager-down nginx-manager-logs all-up all-down
# Configuráveis via linha de comando: ex.: make up SOLR_CORE=meu_core PORT=8984


POSTGRES_CONTAINER ?= postgres
POSTGRES_PORT ?= 5432
NGINX_MANAGER_CONTAINER ?= nginx-manager
NGINX_MANAGER_PORT ?= 80


# carrega configurações de rede e volumes
COMPOSE_BASE=devstack/compose/docker-compose.base.yml
COMPOSE_POSTGRES=devstack/compose/docker-compose.postgres.yml
COMPOSE_NGINX_MANAGER=devstack/compose/docker-compose.nginx-manager.yml


up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_NGINX_MANAGER) up -d

down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_NGINX_MANAGER) down -v

restart:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_NGINX_MANAGER) restart

reup:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_NGINX_MANAGER) down
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_NGINX_MANAGER) up -d

logs:
	@if command -v tmux >/dev/null 2>&1; then \
		echo "Iniciando sessão tmux 'devstack' com 3 painéis..."; \
		tmux new-session -d -s devstack "docker logs -f $(POSTGRES_CONTAINER)" \; \
		split-window -h "docker logs -f $(NGINX_MANAGER_CONTAINER)" \; \
		select-pane -t 0 \; \
		select-layout tiled \; \
		select-pane -t 0 \; \
		attach -t devstack ; \
	else \
		echo "tmux não encontrado, exibindo logs combinados (fallback). Instale tmux para visão em colunas."; \
		docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_NGINX_MANAGER) logs -f; \
	fi

tail:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_NGINX_MANAGER) logs -f --tail=200

postgres-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES) up -d

postgres-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES) stop
	
postgres-logs:
	docker logs -f $(POSTGRES_CONTAINER))

nginx-manager-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) up -d

nginx-manager-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) down
	
nginx-manager-logs:
	docker logs -f $(NGINX_MANAGER_CONTAINER)

all-up: up

all-down: down

