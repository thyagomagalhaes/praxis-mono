# 🧭 Simp DevStack — Stack Local (Solr + Redis + RabbitMQ + MinIO)

Infraestrutura de desenvolvimento pronta para uso com **Docker Compose**, focada em padronizar o sobe/desce e operação de serviços de apoio (Solr, Redis, RabbitMQ, MinIO e RedisInsight) entre projetos.

---

## 🚀 Como usar (via Makefile)

1.  Certifique-se de ter **Docker** e **Docker Compose** instalados.
2.  Use os alvos do Makefile para subir os serviços desejados:

<!-- end list -->

```bash
# Todos os serviços (Solr, Redis, RabbitMQ, MinIO)
make up

# Somente Solr
make solr-up

# Somente Redis + RedisInsight
make redis-up

# Somente RabbitMQ
make rabbitmq-up

# Somente MinIO
make minio-up

# Para encerrar tudo
make down
```

### Serviços Expostos (App rodando no Host)

- **Solr UI:** `http://localhost:8983/solr`
- **Redis (host):** `127.0.0.1:8060` (senha em `redis/redis.conf` ou `.env`)
- **RedisInsight:** `http://localhost:5540`
- **RabbitMQ UI:** `http://localhost:8000` (usuários em `rabbitmq/definitions.json`)
- **MinIO API:** `http://localhost:8090` (S3 API)
- **MinIO Console:** `http://localhost:8091` (UI Web)

---

## ⚙️ Estrutura do diretório

A estrutura é organizada por serviço e por arquivos de composição:

```
compose/
  ├── docker-compose.base.yml
  ├── docker-compose.solr.yml
  ├── docker-compose.redis.yml
  ├── docker-compose.rabbitmq.yml
  └── docker-compose.minio.yml
solr/
  ├── configsets/
  │   └── partes/
  │       └── conf/
  │           ├── managed-schema
  │           └── ...
  └── seed/
      └── partes.json
redis/
  └── redis.conf
rabbitmq/
  ├── definitions.json
  └── rabbitmq.config
```

Principais papéis:

- `compose/*.yml`: Composição por serviço (base, solr, redis, etc.).
- `solr/configsets`: Schemas/configs do Solr.
- `solr/seed`: Dados de seed para testes do Solr.
- `redis/redis.conf`: Configuração do Redis (bind, senha, persistência).
- `rabbitmq/*.json/config`: Definição de usuários, filas e exchanges do RabbitMQ.

---

## 🔌 Conectando seu backend (Rodando no Host)

Como seu backend (rodando fora de containers, na sua IDE) deve se conectar à stack Docker:

- **Solr:** `http://localhost:8983/solr`
- **Redis:** host `localhost`, porta `8060`, senha (veja `redis/redis.conf` ou `.env`).
- **RabbitMQ:** host `localhost`, porta `8072`, vhost `/`, usuário/senha (veja `rabbitmq/definitions.json`).
- **MinIO:** endpoint `http://localhost:8090`, access-key/secret-key (veja `compose/docker-compose.minio.yml`).

(Se o backend rodar _dentro_ da rede `simp-network`, use o nome do container como host e a porta interna. Ex: `http://minio:8090`).

---

## 🧰 Operações úteis (Makefile)

Logs e diagnóstico:

```bash
make logs        # split 2x2: Solr | Redis | RabbitMQ | MinIO (requer tmux)
make logs-solr   # apenas Solr
make redis-logs  # apenas Redis
make ri-logs     # RedisInsight
make rabbitmq-logs # apenas RabbitMQ
make minio-logs  # apenas MinIO
make tail        # últimos logs de todos
```

Saúde/seed/consulta schema do Solr:

```bash
make health
make ping
make seed
make schema
```

---

## 📦 Seeds e testes rápidos

Seed Solr via Makefile:

```bash
make seed
```

Consulta rápida (exemplo):

```bash
curl -s "http://localhost:8983/solr/partes/select?q=*:*&rows=5&fl=id,nome" | jq
```

---

## ❓ Troubleshooting

| Problema                                                            | Solução                                                                                                                                          |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `network simp-network declared as external, but could not be found` | Use os compose fornecidos (já criam a rede) com `make up`.                                                                                       |
| `NOAUTH Authentication required.` no Redis                          | Verifique a senha usada pelo cliente e a `requirepass` em `redis/redis.conf` (ou no `.env`).                                                     |
| SolrCore init failure                                               | Valide `solr/configsets/.../solrconfig.xml` e `managed-schema`.                                                                                  |
| MinIO (App): `Bucket not found`                                     | O container `mc-setup` deve criar os buckets. Verifique os logs (`make logs` ou `docker logs minio-mc-setup`) para ver se ele rodou com sucesso. |

---

---

## 📎 Apêndice — Referências do Solr

- Painel Web: [http://localhost:8983/solr](https://www.google.com/search?q=http://localhost:8983/solr)

- Campos do core `partes`:

  ```bash
  make schema
  ```

### Como checar

```bash
curl -s "http://localhost:8983/solr/partes/select?q=*:*&rows=5&fl=id,nome" | jq
```

Retorno esperado (exemplo):

```json
{
  "responseHeader": {
    "status": 0,
    "QTime": 19,
    "params": { "q": "*:*", "fl": "id,nome", "rows": "5" }
  },
  "response": {
    "numFound": 6,
    "start": 0,
    "numFoundExact": true,
    "docs": [
      { "id": "1", "nome": "A apurar" },
      { "id": "2", "nome": "A sociedade" },
      { "id": "3", "nome": "Estado de Mato Grosso" },
      { "id": "4", "nome": "Ministério Público do Estado de Mato Grosso" },
      { "id": "5", "nome": "Ministério Público do Estado de Pernambuco" }
    ]
  }
}
```
