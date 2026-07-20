# Alvos que não representam arquivos físicos no disco
.PHONY: up down restart reup logs tail \
        nginx-up nginx-down nginx-logs \
        ngrok-up ngrok-down ngrok-logs \
        portainer-up portainer-down portainer-logs \
        keycloak-up keycloak-down keycloak-logs \
        mariadb-up mariadb-down mariadb-logs \
        adminer-logs \
        minio-up minio-down minio-logs \
        minioconsole-logs \
        mysql-up mysql-down mysql-logs \
        phpmyadmin-logs \
        postgres-up postgres-down postgres-logs \
        pgadmin-logs \
        rabbitmq-up rabbitmq-down rabbitmq-logs \
        redis-up redis-down redis-logs \
        redisinsight-logs \
        vault-up vault-down vault-logs \
        all-up all-down

# Configuráveis via linha de comando: ex.: make up SOLR_CORE=meu_core PORT=8984

NGINX_MANAGER_CONTAINER ?= nginx-manager
NGROK_CONTAINER ?= ngrok
PORTAINER_CONTAINER ?= portainer

KEYCLOAK_CONTAINER ?= keycloak
MINIO_CONTAINER ?= minio
MINIOCONSOLE_CONTAINER ?= minioconsole

MARIADB_CONTAINER ?= mariadb
ADMINER_CONTAINER ?= adminer

MYSQL_CONTAINER ?= mysql
PHPMYADMIN_CONTAINER ?= phpmyadmin

POSTGRES_CONTAINER ?= postgresql
PGADMIN_CONTAINER ?= pgadmin

RABBITMQ_CONTAINER ?= rabbitmq

REDIS_CONTAINER ?= redis
REDISINSIGHT_CONTAINER ?= redisinsight

VAULT_CONTAINER ?= vault


# carrega configurações de rede e volumes
COMPOSE_BASE=stacks/docker-compose.base.yml
COMPOSE_NGINX_MANAGER=stacks/docker-compose.nginx.yml
COMPOSE_NGROK=stacks/docker-compose.ngrok.yml
COMPOSE_MINIO=stacks/docker-compose.minio.yml
COMPOSE_MARIADB=stacks/docker-compose.mariadb.yml
COMPOSE_MYSQL=stacks/docker-compose.mysql.yml
COMPOSE_POSTGRES=stacks/docker-compose.postgres.yml
COMPOSE_RABBITMQ=stacks/docker-compose.rabbitmq.yml
COMPOSE_REDIS=stacks/docker-compose.redis.yml
COMPOSE_KEYCLOAK=stacks/docker-compose.keycloak.yml
COMPOSE_PORTAINER=stacks/docker-compose.portainer.yml
COMPOSE_VAULT=stacks/docker-compose.vault.yml



up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MINIO) -f $(COMPOSE_MARIADB) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_RABBITMQ) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_VAULT) up -d

down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MINIO) -f $(COMPOSE_MARIADB) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_RABBITMQ) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_VAULT) down -v
	
restart:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MINIO) -f $(COMPOSE_MARIADB) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_RABBITMQ) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_VAULT) restart

reup:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MINIO) -f $(COMPOSE_MARIADB) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_RABBITMQ) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_VAULT) down
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MINIO) -f $(COMPOSE_MARIADB) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_RABBITMQ) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_VAULT) up -d

logs:
	@if command -v tmux >/dev/null 2>&1; then \
		echo "Iniciando sessão tmux 'devstack' com 16 painéis..."; \
		tmux new-session -d -s devstack -n "logs" "docker logs -f $(NGINX_MANAGER_CONTAINER)"; \
		tmux split-window -h -t devstack:logs "docker logs -f $(NGROK_CONTAINER)"; \
		tmux split-window -v -t devstack:logs.0 "docker logs -f $(MARIADB_CONTAINER)"; \
		tmux split-window -v -t devstack:logs.1 "docker logs -f $(ADMINER_CONTAINER)"; \
		tmux split-window -v -t devstack:logs.2 "docker logs -f $(MYSQL_CONTAINER)"; \
		tmux split-window -v -t devstack:logs.3 "docker logs -f $(PHPMYADMIN_CONTAINER)"; \
		tmux split-window -v -t devstack:logs.4 "docker logs -f $(POSTGRES_CONTAINER)"; \
		tmux split-window -v -t devstack:logs.5 "docker logs -f $(PGADMIN_CONTAINER)"; \
		tmux split-window -v -t devstack:logs.6 "docker logs -f $(REDIS_CONTAINER)"; \
		tmux split-window -v -t devstack:logs.7 "docker logs -f $(REDISINSIGHT_CONTAINER)"; \
		tmux split-window -v -t devstack:logs.8 "docker logs -f $(KEYCLOAK_CONTAINER)"; \
	    tmux split-window -v -t devstack:logs.9 "docker logs -f $(MINIO_CONTAINER)"; \
		tmux split-window -v -t devstack:logs.10 "docker logs -f $(MINIOCONSOLE_CONTAINER)"; \
		tmux split-window -v -t devstack:logs.11 "docker logs -f $(RABBITMQ_CONTAINER)"; \
		tmux split-window -v -t devstack:logs.12 "docker logs -f $(VAULT_CONTAINER)"; \
        tmux split-window -v -t devstack:logs.13 "docker logs -f $(PORTAINER_CONTAINER)"; \
		tmux select-layout -t devstack:logs tiled; \
		tmux attach-session -t devstack; \
	else \
		echo "tmux não encontrado, exibindo logs combinados (fallback). Instale tmux para visão em colunas."; \
		docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MINIO) -f $(COMPOSE_MARIADB) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_RABBITMQ) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_VAULT) logs -f; \
	fi

tail:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) -f $(COMPOSE_MINIO) -f $(COMPOSE_MARIADB) -f $(COMPOSE_MYSQL) -f $(COMPOSE_POSTGRES) -f $(COMPOSE_RABBITMQ) -f $(COMPOSE_REDIS) -f $(COMPOSE_KEYCLOAK) -f $(COMPOSE_PORTAINER) -f $(COMPOSE_VAULT) logs -f --tail=200

nginx-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) up -d

nginx-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) down
	
nginx-logs:
	docker logs -f $(NGINX_MANAGER_CONTAINER)
	
ngrok-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) up -d
    
ngrok-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_NGINX_MANAGER) -f $(COMPOSE_NGROK) down
    
ngrok-logs:
	docker logs -f $(NGROK_CONTAINER)
    
portainer-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PORTAINER) up -d

portainer-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PORTAINER) down
	
portainer-logs:
	docker logs -f $(PORTAINER_CONTAINER)

mariadb-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_MARIADB) up -d

mariadb-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_MARIADB) down
	
mariadb-logs:
	docker logs -f $(MARIADB_CONTAINER)
	
adminer-logs:
	docker logs -f $(ADMINER_CONTAINER)
	
minio-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_MINIO) up -d

minio-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_MINIO) down
	
minio-logs:
	docker logs -f $(MINIO_CONTAINER)
	
minioconsole-logs:
	docker logs -f $(MINIOCONSOLE_CONTAINER)

mysql-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_MYSQL) up -d

mysql-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_MYSQL) down
	
mysql-logs:
	docker logs -f $(MYSQL_CONTAINER)
	
phpmyadmin-logs:
	docker logs -f $(PHPMYADMIN_CONTAINER)
	
keycloak-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_MYSQL) -f $(COMPOSE_KEYCLOAK) up -d

keycloak-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_MYSQL) -f $(COMPOSE_KEYCLOAK) down
	
keycloak-logs:
	docker logs -f $(KEYCLOAK_CONTAINER)

postgres-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES) up -d

postgres-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_POSTGRES) down
	
postgres-logs:
	docker logs -f $(POSTGRES_CONTAINER)

pgadmin-logs:
	docker logs -f $(PGADMIN_CONTAINER)

rabbitmq-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_RABBITMQ) up -d

rabbitmq-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_RABBITMQ) stop
	
rabbitmq-logs:
	docker logs -f $(RABBITMQ_CONTAINER)
	
redis-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_REDIS) up -d

redis-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_REDIS) stop
	
redis-logs:
	docker logs -f $(REDIS_CONTAINER)

redisinsight-logs:
	docker logs -f $(REDISINSIGHT_CONTAINER)
	
vault-up:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_VAULT) up -d

vault-down:
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_VAULT) stop
	
vault-logs:
	docker logs -f $(VAULT_CONTAINER)

all-up: up

all-down: down

