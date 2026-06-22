# Alvos que não representam arquivos físicos no disco
.PHONY: up down restart reup logs tail \
        nginx-up nginx-down nginx-logs \
        ngrok-up ngrok-down ngrok-logs \
        portainer-up portainer-down portainer-logs \
        keycloak-up keycloak-down keycloak-logs \
        mysql-up mysql-down mysql-logs \
        phpmyadmin-up phpmyadmin-down phpmyadmin-logs \
        postgres-up postgres-down postgres-logs \
        pgadmin-up pgadmin-down pgadmin-logs \
        redis-up redis-down redis-logs \
        redisinsight-up redisinsight-down redisinsight-logs \
        all-up all-down

# Configuráveis via linha de comando: ex.: make up SOLR_CORE=meu_core PORT=8984

NGINX_MANAGER_CONTAINER_INFRA ?= nginx-manager
NGROK_CONTAINER_INFRA ?= ngrok-tunnel-webhooks
PORTAINER_CONTAINER_INFRA ?= portainer-hub

KEYCLOAK_CONTAINER_FSW ?= keycloak-fsw

MYSQL_CONTAINER_FSW ?= mysql-fsw
PHPMYADMIN_CONTAINER_CONSOLE ?= phpmyadmin-cli

POSTGRES_CONTAINER_FSW ?= postgresql-fsw
PGADMIN_CONTAINER_CONSOLE ?= pgadmin-cli

REDIS_CONTAINER_FSW ?= redis-fsw
REDISINSIGHT_CONTAINER_CONSOLE ?= redisinsight-cli


# carrega configurações de rede e volumes
COMPOSE_BASE=stacks/docker-compose.base.yml
COMPOSE_NGINX_MANAGER=stacks/docker-compose.nginx.yml
COMPOSE_NGROK=stacks/docker-compose.ngrok.yml
COMPOSE_MYSQL=stacks/docker-compose.mysql.yml
COMPOSE_POSTGRES=stacks/docker-compose.postgres.yml
COMPOSE_REDIS=stacks/docker-compose.redis.yml
COMPOSE_KEYCLOAK=stacks/docker-compose.keycloak.yml
COMPOSE_PORTAINER=stacks/docker-compose.portainer.yml


up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) up -d

down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) down -v

restart:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) restart

reup:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) down
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) up -d

logs:
	@if command -v tmux >/dev/null 2>&1; then \
		echo "Iniciando sessão tmux 'devstack' com 10 painéis..."; \
		tmux new-session -d -s devstack -n "logs" "docker logs -f $(NGINX_MANAGER_CONTAINER_INFRA)"; \
		tmux split-window -h -t devstack:logs "docker logs -f $(NGROK_CONTAINER_INFRA)"; \
		tmux split-window -v -t devstack:logs.0 "docker logs -f $(MYSQL_CONTAINER_FSW)"; \
		tmux split-window -v -t devstack:logs.1 "docker logs -f $(PHPMYADMIN_CONTAINER_CONSOLE)"; \
		tmux split-window -v -t devstack:logs.2 "docker logs -f $(POSTGRES_CONTAINER_FSW)"; \
		tmux split-window -v -t devstack:logs.3 "docker logs -f $(PGADMIN_CONTAINER_CONSOLE)"; \
		tmux split-window -v -t devstack:logs.4 "docker logs -f $(REDIS_CONTAINER_FSW)"; \
		tmux split-window -v -t devstack:logs.5 "docker logs -f $(REDISINSIGHT_CONTAINER_CONSOLE)"; \
		tmux split-window -v -t devstack:logs.6 "docker logs -f $(KEYCLOAK_CONTAINER_FSW)"; \
		tmux split-window -v -t devstack:logs.7 "docker logs -f $(PORTAINER_CONTAINER_INFRA)"; \
		tmux select-layout -t devstack:logs tiled; \
		tmux attach-session -t devstack; \
	else \
		echo "tmux não encontrado, exibindo logs combinados (fallback). Instale tmux para visão em colunas."; \
		docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) logs -f; \
	fi

tail:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) logs -f --tail=200

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

