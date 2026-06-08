.PHONY: up down restart reup logs tail nginx-up nginx-down nginx-logs postgres-up postgres-down postgres-logs pgadmin-up pgadmin-down pgadmin-logs portainer-up portainer-down portainer-logs all-up all-down
# Configuráveis via linha de comando: ex.: make up SOLR_CORE=meu_core PORT=8984


NGINX_MANAGER_CONTAINER ?= nginx
PORTAINER_CONTAINER ?= portainer
POSTGRES_CONTAINER ?= postgres
PGADMIN_CONTAINER ?= pgadmin


# carrega configurações de rede e volumes
COMPOSE_BASE=devstack/compose/docker-compose.base.yml
COMPOSE_NGINX_MANAGER=devstack/compose/docker-compose.nginx.yml
COMPOSE_PORTAINER=devstack/compose/docker-compose.portainer.yml
COMPOSE_POSTGRES=devstack/compose/docker-compose.postgres.yml



up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES) up -d

down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES) down -v

restart:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES) restart

reup:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES) down
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES) up -d

logs:
	@if command -v tmux >/dev/null 2>&1; then \
		echo "Iniciando sessão tmux 'devstack' com 4 painéis..."; \
		tmux new-session -d -s devstack "docker logs -f $(POSTGRES_CONTAINER)" \; \
		split-window -h "docker logs -f $(PGADMIN_CONTAINER)" \; \
		select-pane -t 0 \; \
		split-window -v "docker logs -f $(NGINX_MANAGER_CONTAINER)" \; \
		select-pane -t 1 \; \
		split-window -v "docker logs -f $(PORTAINER_CONTAINER)" \; \
		select-layout tiled \; \
		select-pane -t 0 \; \
		attach -t devstack ; \
	else \
		echo "tmux não encontrado, exibindo logs combinados (fallback). Instale tmux para visão em colunas."; \
		docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES) logs -f; \
	fi

tail:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_POSTGRES) logs -f --tail=200

nginx-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) up -d

nginx-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) down
	
nginx-logs:
	docker logs -f $(NGINX_MANAGER_CONTAINER)
	
portainer-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PORTAINER) up -d

portainer-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PORTAINER) stop
	
portainer-logs:
	docker logs -f $(PORTAINER_CONTAINER)


postgres-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES) up -d

postgres-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES) stop
	
postgres-logs:
	docker logs -f $(PGADMIN_CONTAINER) -f $(POSTGRES_CONTAINER)

all-up: up

all-down: down

