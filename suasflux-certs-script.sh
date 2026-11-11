# script de automação para a geração dos certificados com o mkcert


#!/usr/bin/env bash

# Exit on error
set -e

echo "=== [1/4] Atualizando pacotes e instalando dependências ==="
sudo apt-get update -y
sudo apt-get install -y wget curl libnss3-tools

echo "=== [2/4] Baixando e instalando o mkcert ==="
# Baixa a versão mais recente do binário x86_64 do mkcert
MKCERT_VERSION="v1.4.4"
curl -sS -L "https://github.com/FiloSottile/mkcert/releases/download/${MKCERT_VERSION}/mkcert-${MKCERT_VERSION}-linux-amd64" -o mkcert
chmod +x mkcert
sudo mv mkcert /usr/local/bin/mkcert

echo "=== [3/4] Instalando a Autoridade Certificadora Local (CA) ==="
mkcert -install

echo "=== [4/4] Gerando os certificados SSL Wildcard ==="
# Cria o diretório para armazenar os certificados
CERT_DIR="$HOME/suasflux-certs"
mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

# Lista de domínios wildcard
DOMAINS=(
  "*.suasflux.prem"
  "*.suasflux.dev"
  "*.suasflux.hml"
  "*.suasflux.prod"
  "*.catorecomeco.dev"
  "*.catorecomeco.hml"
  "*.catorecomeco.prod"
)

# Gera um único certificado que cobre todos os domínios listados
mkcert -cert-file suasflux-wildcard.pem -key-file suasflux-wildcard-key.pem "${DOMAINS[@]}"

# Exibe o caminho absoluto do certificado CA raiz gerado
CA_PATH=$(mkcert -CAROOT)

echo ""
echo "============================================================"
echo " Concluído com sucesso!"
echo "============================================================"
echo " Certificado gerado em: $CERT_DIR/suasflux-wildcard.pem"
echo " Chave privada em:     $CERT_DIR/suasflux-wildcard-key.pem"
echo ""
echo " IMPORTANTE: Para que seus navegadores confiem no certificado,"
echo " você precisa copiar a CA Raiz para a sua máquina física:"
echo " Arquivo CA Raiz:      $CA_PATH/rootCA.pem"
echo "============================================================"
