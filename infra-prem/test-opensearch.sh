#!/usr/bin/env bash

# validar a conexão HTTPS, a autenticação básica e o healthcheck.

# Carrega as variáveis do .env
if [ -f .env ]; then
  export $(cat .env | grep -v '#' | xargs)
else
  echo "Erro: Arquivo .env não encontrado."
  exit 1
fi

HOST="https://localhost:9200"
USER="admin"
PASS="${OPENSEARCH_INITIAL_ADMIN_PASSWORD}"

echo "========================================="
echo " Verificando Status do Cluster OpenSearch"
echo "========================================="

# 1. Teste de Conexão SSL + Autenticação Básica
echo -n "1. Testando conexão com autenticação básica... "
RESPONSE_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" -u "${USER}:${PASS}" "${HOST}")

if [ "$RESPONSE_CODE" -eq 200 ]; then
  echo "[OK] (HTTP $RESPONSE_CODE)"
else
  echo "[FALHA] (HTTP $RESPONSE_CODE)"
  exit 1
fi

# 2. Leitura do Health Status do Cluster
echo -n "2. Checando saúde do cluster... "
CLUSTER_HEALTH=$(curl -k -s -u "${USER}:${PASS}" "${HOST}/_cluster/health" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

echo "[STATUS: ${CLUSTER_HEALTH}]"

# 3. Teste de Criação de Índice
echo -n "3. Criando índice de teste ('dev-test-index')... "
CREATE_INDEX=$(curl -k -s -X PUT -u "${USER}:${PASS}" "${HOST}/dev-test-index")

if echo "$CREATE_INDEX" | grep -q '"acknowledged":true'; then
  echo "[OK]"
else
  echo "[FALHA] Resposta: $CREATE_INDEX"
fi

# 4. Limpeza do Índice de Teste
echo -n "4. Removendo índice de teste... "
DELETE_INDEX=$(curl -k -s -X DELETE -u "${USER}:${PASS}" "${HOST}/dev-test-index")

if echo "$DELETE_INDEX" | grep -q '"acknowledged":true'; then
  echo "[OK]"
else
  echo "[FALHA]"
fi

echo "========================================="
echo "Tudo pronto! Acesse a interface visual em:"
echo "http://localhost:5601"
echo "Usuário: admin | Senha: ${PASS}"
echo "========================================="