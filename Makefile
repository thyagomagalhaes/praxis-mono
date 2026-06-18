.PHONY: up down restart reup logs tail nginx-up nginx-down nginx-logs postgres-up postgres-down postgres-logs pgadmin-up pgadmin-down pgadmin-logs portainer-up portainer-down portainer-logs all-up all-down
# Configuráveis via linha de comando: ex.: make up SOLR_CORE=meu_core PORT=8984

NGINX_MANAGER_CONTAINER_INFRA ?= nginx-infra
PORTAINER_CONTAINER_INFRA ?= portainer-infra

POSTGRES_CONTAINER_DEV ?= postgres-dev
PGADMIN_CONTAINER_DEV ?= pgadmin-dev


# carrega configurações de rede e volumes
COMPOSE_BASE=stacks/docker-compose.base.yml
COMPOSE_NGINX_MANAGER=stacks/docker-compose.nginx.yml
COMPOSE_PORTAINER=stacks/docker-compose.portainer.yml

COMPOSE_POSTGRES_DEV=stacks/docker-compose.postgres.yml



up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES_DEV) up -d

down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES_DEV) down -v

restart:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES_DEV) restart

reup:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES_DEV) down
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES_DEV) up -d

logs:
	@if command -v tmux >/dev/null 2>&1; then \
		echo "Iniciando sessão tmux 'devstack' com 4 painéis..."; \
		tmux new-session -d -s devstack "docker logs -f $(POSTGRES_CONTAINER_DEV)" \; \
		split-window -h "docker logs -f $(PGADMIN_CONTAINER_DEV)" \; \
		select-pane -t 0 \; \
		split-window -v "docker logs -f $(NGINX_MANAGER_CONTAINER_INFRA)" \; \
		select-pane -t 1 \; \
		split-window -v "docker logs -f $(PORTAINER_CONTAINER_INFRA)" \; \
		select-layout tiled \; \
		select-pane -t 0 \; \
		attach -t devstack ; \
	else \
		echo "tmux não encontrado, exibindo logs combinados (fallback). Instale tmux para visão em colunas."; \
		docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES_DEV) logs -f; \
	fi

tail:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES_DEV) logs -f --tail=200

nginx-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) up -d

nginx-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) down
	
nginx-logs:
	docker logs -f $(NGINX_MANAGER_CONTAINER_INFRA)
	
portainer-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PORTAINER) up -d

portainer-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PORTAINER) stop
	
portainer-logs:
	docker logs -f $(PORTAINER_CONTAINER_INFRA)

postgres-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES_DEV) up -d

postgres-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES_DEV) stop
	
postgres-logs:
	docker logs -f $(POSTGRES_CONTAINER_DEV)

pgadmin-logs:
	docker logs -f $(PGADMIN_CONTAINER_DEV)

all-up: up

all-down: down

