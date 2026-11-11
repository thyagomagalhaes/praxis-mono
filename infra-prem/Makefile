# ============================================================
# SUAFLUX PREM - Makefile
# Padronização de operações de infraestrutura on-premise
# ============================================================

.PHONY: help networks-up common-up common-down common-logs common-ps \
        fsw-up fsw-down fsw-logs fsw-ps \
        hml-up hml-down hml-logs hml-ps \
        prod-up prod-down prod-logs prod-ps \
        all-up all-down all-logs all-ps clean backup

# --------------------------------------------------
# Variáveis
# --------------------------------------------------
COMPOSE_COMMON := docker compose -f docker-compose.common.yml --env-file .env.common
COMPOSE_FSW    := docker compose -f docker-compose.fsw.yml --env-file .env.fsw
COMPOSE_HML    := docker compose -f docker-compose.hml.yml --env-file .env.hml
COMPOSE_PROD   := docker compose -f docker-compose.prod.yml --env-file .env.prod

# --------------------------------------------------
# Ajuda
# --------------------------------------------------
help:
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║           SUAFLUX PREM - Infraestrutura On-Premise           ║"
	@echo "╠══════════════════════════════════════════════════════════════╣"
	@echo "║ Comandos disponíveis:                                        ║"
	@echo "╠══════════════════════════════════════════════════════════════╣"
	@echo "║  make networks-up   → Cria todas as redes Docker             ║"
	@echo "║  make common-up     → Sobe Shared Services (common)          ║"
	@echo "║  make common-down   → Derruba Shared Services                ║"
	@echo "║  make common-logs   → Logs do ambiente common                ║"
	@echo "║  make common-ps     → Status dos containers common           ║"
	@echo "║                                                              ║"
	@echo "║  make fsw-up        → Sobe Desenvolvimento (fsw)             ║"
	@echo "║  make fsw-down      → Derruba Desenvolvimento                ║"
	@echo "║  make fsw-logs      → Logs do ambiente fsw                   ║"
	@echo "║  make fsw-ps        → Status dos containers fsw              ║"
	@echo "║                                                              ║"
	@echo "║  make hml-up        → Sobe Staging (hml)                     ║"
	@echo "║  make hml-down      → Derruba Staging                        ║"
	@echo "║  make hml-logs      → Logs do ambiente hml                   ║"
	@echo "║  make hml-ps        → Status dos containers hml              ║"
	@echo "║                                                              ║"
	@echo "║  make prod-up       → Sobe Produção (prod)                   ║"
	@echo "║  make prod-down     → Derruba Produção                       ║"
	@echo "║  make prod-logs     → Logs do ambiente prod                  ║"
	@echo "║  make prod-ps       → Status dos containers prod             ║"
	@echo "║                                                              ║"
	@echo "║  make all-up        → Sobe TUDO (atenção aos recursos!)      ║"
	@echo "║  make all-down      → Derruba TUDO                           ║"
	@echo "║  make all-logs      → Logs de todos os ambientes             ║"
	@echo "║  make all-ps        → Status de todos os containers          ║"
	@echo "║                                                              ║"
	@echo "║  make backup        → Backup dos volumes Docker              ║"
	@echo "║  make clean         → Remove volumes órfãos e prune          ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"

# --------------------------------------------------
# Redes
# --------------------------------------------------
networks-up:
	@echo "🔧 Criando e validando redes Docker..."
	@docker network inspect suasflux-prem-common >/dev/null 2>&1 || \
		docker network create suasflux-prem-common --label com.docker.compose.network=suasflux-prem-common
	@docker network inspect suasflux-prem-fsw >/dev/null 2>&1 || \
		docker network create suasflux-prem-fsw --label com.docker.compose.network=suasflux-prem-fsw
	@docker network inspect suasflux-prem-hml >/dev/null 2>&1 || \
		docker network create suasflux-prem-hml --label com.docker.compose.network=suasflux-prem-hml
	@docker network inspect suasflux-prem-prod >/dev/null 2>&1 || \
		docker network create suasflux-prem-prod --label com.docker.compose.network=suasflux-prem-prod
	@echo "✅ Redes criadas com sucesso!"


# --------------------------------------------------
# COMMON (Shared Services)
# --------------------------------------------------
common-up: networks-up
	@echo "🚀 Subindo Shared Services (common)..."
	$(COMPOSE_COMMON) up -d
	@echo "✅ Common operacional!"
	@echo "   MariaDB:      localhost:3307"
	@echo "   Adminer:      http://localhost:8082"
	@echo "   Portainer:    https://localhost:9443"
	@echo "   NPM:          http://localhost:81"
	@echo "   Ngrok:        http://localhost:4040"

common-down:
	@echo "🛑 Derrubando Shared Services (common)..."
	$(COMPOSE_COMMON) down

common-logs:
	$(COMPOSE_COMMON) logs -f

common-ps:
	$(COMPOSE_COMMON) ps

# --------------------------------------------------
# FSW (Desenvolvimento)
# --------------------------------------------------
fsw-up: networks-up
	@echo "🚀 Subindo Desenvolvimento (fsw)..."
	$(COMPOSE_FSW) up -d
	@echo "✅ FSW operacional!"
	@echo "   MySQL ( keycloak ):        localhost:3306"
	@echo "   phpMyAdmin:   http://localhost:8083"
	@echo "   PostGIS msfederacao:   localhost:5431"
	@echo "   PG Tileserv msfederacao:   http://localhost:7800"
	@echo "   PostGIS msterritorializacao:   localhost:5432"
	@echo "   PG Tileserv msterritorializacao:   http://localhost:7801"
	@echo "   PostgreSQL mspublico:   localhost:5433"
	@echo "   PostgreSQL msacolhimento:   localhost:5434"
	@echo "   PostgreSQL msatendimento:   localhost:5435"
	@echo "   pgAdmin:      http://localhost:8084"
	@echo "   Redis:        localhost:6379"
	@echo "   RedisInsight: http://localhost:8085"
	@echo "   MongoDB:      localhost:27017"
	@echo "   MongoExpress: http://localhost:8086"
	@echo "   RabbitMQ:     localhost:5672  | Management: http://localhost:15672"
	@echo "   Kafka:        localhost:9092"
	@echo "   Kafbat UI:    http://localhost:8081"
	@echo "   OpenSearch:   REST API: localhost:9200  | Performance Analyzer: localhost:9600"
	@echo "   OpenSearch Dashboards:  http://localhost:5601"
	@echo "   MinIO API:    localhost:9000  | Console: http://localhost:9001"
	@echo "   Mailpit SMTP: localhost:1025  | Web: http://localhost:8025"
	@echo "   Wiremock Twillio API SMS+WhastsApp: http://localhost:8180"
	@echo "   Keycloak:     http://localhost:8080"

fsw-down:
	@echo "🛑 Derrubando Desenvolvimento (fsw)..."
	$(COMPOSE_FSW) down

fsw-logs:
	$(COMPOSE_FSW) logs -f

fsw-ps:
	$(COMPOSE_FSW) ps

# --------------------------------------------------
# HML (Staging)
# --------------------------------------------------
hml-up: networks-up
	@echo "🚀 Subindo Staging (hml)..."
	$(COMPOSE_HML) up -d
	@echo "✅ HML operacional!"
	@echo "   MySQL:        localhost:3306"
	@echo "   PostgreSQL:   localhost:5432"
	@echo "   Redis:        localhost:6379"
	@echo "   MongoDB:      localhost:27017"
	@echo "   RabbitMQ:     localhost:5672  | Management: localhost:15672"
	@echo "   Kafka:        localhost:9092"
	@echo "   Kafbat UI:    http://localhost:8081"
	@echo "   MinIO API:    localhost:9000  | Console: http://localhost:9001"
	@echo "   Keycloak:     http://localhost:8080"
	@echo "   Vault:        http://localhost:8200"

hml-down:
	@echo "🛑 Derrubando Staging (hml)..."
	$(COMPOSE_HML) down

hml-logs:
	$(COMPOSE_HML) logs -f

hml-ps:
	$(COMPOSE_HML) ps

# --------------------------------------------------
# PROD (Produção)
# --------------------------------------------------
prod-up: networks-up
	@echo "🚀 Subindo Produção (prod)..."
	$(COMPOSE_PROD) up -d
	@echo "✅ PROD operacional!"
	@echo "   MySQL:        localhost:3306"
	@echo "   PostgreSQL:   localhost:5432"
	@echo "   Redis:        localhost:6379"
	@echo "   MongoDB:      localhost:27017"
	@echo "   RabbitMQ:     localhost:5672  | Management: localhost:15672"
	@echo "   Kafka:        localhost:9092"
	@echo "   Kafbat UI:    http://localhost:8081"
	@echo "   MinIO API:    localhost:9000  | Console: http://localhost:9001"
	@echo "   Keycloak:     http://localhost:8080"
	@echo "   Vault:        http://localhost:8200"

prod-down:
	@echo "🛑 Derrubando Produção (prod)..."
	$(COMPOSE_PROD) down

prod-logs:
	$(COMPOSE_PROD) logs -f

prod-ps:
	$(COMPOSE_PROD) ps

# --------------------------------------------------
# Operações globais
# --------------------------------------------------
all-up: common-up fsw-up hml-up prod-up
	@echo "🌍 Todos os ambientes estão operacionais!"

all-down:
	@echo "🛑 Derrubando TODOS os ambientes..."
	$(COMPOSE_PROD) down
	$(COMPOSE_HML) down
	$(COMPOSE_FSW) down
	$(COMPOSE_COMMON) down

all-logs:
	@echo "📋 Logs de todos os ambientes (Ctrl+C para sair)..."
	$(COMPOSE_COMMON) logs -f &
	$(COMPOSE_FSW) logs -f &
	$(COMPOSE_HML) logs -f &
	$(COMPOSE_PROD) logs -f &
	wait

all-ps:
	@echo "📊 Status dos containers:"
	@echo ""
	@echo "--- COMMON ---"
	$(COMPOSE_COMMON) ps
	@echo ""
	@echo "--- FSW ---"
	$(COMPOSE_FSW) ps
	@echo ""
	@echo "--- HML ---"
	$(COMPOSE_HML) ps
	@echo ""
	@echo "--- PROD ---"
	$(COMPOSE_PROD) ps

# --------------------------------------------------
# Backup e Manutenção
# --------------------------------------------------
backup:
	@echo "💾 Iniciando backup dos volumes..."
	mkdir -p backups/$$(date +%Y%m%d_%H%M%S)
	docker run --rm -v suasflux-prem-common-mariadb-rds-nginx-data:/data -v $$(pwd)/backups:/backups alpine tar czf /backups/$$(date +%Y%m%d_%H%M%S)/common-mariadb-nginx.tar.gz -C /data .
	docker run --rm -v suasflux-prem-fsw-mysql-keycloak-data:/data -v $$(pwd)/backups:/backups alpine tar czf /backups/$$(date +%Y%m%d_%H%M%S)/fsw-mysql-keycloak.tar.gz -C /data .
	docker run --rm -v suasflux-prem-fsw-postgis-msfederacao-data:/data -v $$(pwd)/backups:/backups alpine tar czf /backups/$$(date +%Y%m%d_%H%M%S)/fsw-postgis-msfederacao.tar.gz -C /data .
	docker run --rm -v suasflux-prem-fsw-postgis-msterritorializacao-data:/data -v $$(pwd)/backups:/backups alpine tar czf /backups/$$(date +%Y%m%d_%H%M%S)/fsw-postgis-msterritorializacao.tar.gz -C /data .
	docker run --rm -v suasflux-prem-fsw-postgres-mspublico-data:/data -v $$(pwd)/backups:/backups alpine tar czf /backups/$$(date +%Y%m%d_%H%M%S)/fsw-postgres-mspublico.tar.gz -C /data .
	docker run --rm -v suasflux-prem-fsw-postgres-msacolhimento-data:/data -v $$(pwd)/backups:/backups alpine tar czf /backups/$$(date +%Y%m%d_%H%M%S)/fsw-postgres-msacolhimento.tar.gz -C /data .
	docker run --rm -v suasflux-prem-fsw-postgres-msatendimento-data:/data -v $$(pwd)/backups:/backups alpine tar czf /backups/$$(date +%Y%m%d_%H%M%S)/fsw-postgres-msatendimento.tar.gz -C /data .
	docker run --rm -v suasflux-prem-fsw-postgres-msspatial-data:/data -v $$(pwd)/backups:/backups alpine tar czf /backups/$$(date +%Y%m%d_%H%M%S)/fsw-postgres-msspatial.tar.gz -C /data .
	docker run --rm -v suasflux-prem-fsw-postgis-msspatial-data:/data -v $$(pwd)/backups:/backups alpine tar czf /backups/$$(date +%Y%m%d_%H%M%S)/fsw-postgis-msspatial.tar.gz -C /data .
	docker run --rm -v suasflux-prem-hml-mysql-data:/data -v $$(pwd)/backups:/backups alpine tar czf /backups/$$(date +%Y%m%d_%H%M%S)/hml-mysql.tar.gz -C /data .
	docker run --rm -v suasflux-prem-hml-postgres-data:/data -v $$(pwd)/backups:/backups alpine tar czf /backups/$$(date +%Y%m%d_%H%M%S)/hml-postgres.tar.gz -C /data .
	docker run --rm -v suasflux-prem-prod-mysql-data:/data -v $$(pwd)/backups:/backups alpine tar czf /backups/$$(date +%Y%m%d_%H%M%S)/prod-mysql.tar.gz -C /data .
	docker run --rm -v suasflux-prem-prod-postgres-data:/data -v $$(pwd)/backups:/backups alpine tar czf /backups/$$(date +%Y%m%d_%H%M%S)/prod-postgres.tar.gz -C /data .
	@echo "✅ Backup concluído em backups/$$(date +%Y%m%d_%H%M%S)/"

clean:
	@echo "🧹 Limpando recursos não utilizados..."
	docker system prune -f
	docker volume prune -f
	@echo "✅ Limpeza concluída!"
