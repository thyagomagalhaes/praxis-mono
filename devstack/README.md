# 🧭 Práxis DevStack — Stack Local

- Infraestrutura de desenvolvimento pronta para uso com **Docker Compose**, focada em padronizar o sobe/desce e operação dos seguintes serviços de apoio entre projetos: 

    - Portainer
    - Nginx
    - PostgreSQL

---

## 🚀 Como usar (via Makefile)

1.  Adição de `virtual hosts`:

```bash
127.0.0.1 localhost
127.0.0.1 praxis.local
127.0.0.1 nginx.praxis.local 
127.0.0.1 pgadmin.praxis.local
127.0.0.1 portainer.praxis.local
```

2.  Certifique-se de ter **Docker** e **Docker Compose** instalados;
3.  Use os alvos do Makefile para subir os serviços desejados:

<!-- end list -->

```bash
# Todos os serviços (Portainer, Nginx, PostgreSQL)
make up

# Somente Portainer
make portainer-up

# Somente PostgreSQL + pgAdmin
make postgres-up

# Somente Nginx + Nginx Proxy Manager
make nginx-up

# Para encerrar tudo
make down
```

### Serviços Expostos (App rodando no Host)

- **Nginx Proxy Controller:** `http://nginx.praxis.local` ou `http://localhost:81`
- **PgAdmin:** `http://pgadmin.praxis.local` ou `http://localhost:5050`
- **Portainer CE:** `http://portainer.praxis.local` ou `http://localhost:9443`


---

## ⚙️ Estrutura do diretório

A estrutura é organizada por serviço e por arquivos de composição:

```
compose/
  ├── docker-compose.base.yml
  ├── docker-compose.nginx.yml
  ├── docker-compose.portainer.yml
  └──  docker-compose.postgres.yml
```

Principais papéis:

- `compose/*.yml`: Composição por serviço (base, Nginx, Portainer e etc.).

---

## 🔌 Conectando seu backend (Rodando no Host)

Como seu backend (rodando fora de containers, na sua IDE) deve se conectar à stack Docker:


- **Postgres:** host `localhost` ou `www.praxis.local` e porta `5432`;


(Se o backend rodar _dentro_ da rede `praxis-network`, use o nome do container como host e a porta interna. Ex: `http://pgadmin:5050`).

---

## 🧰 Operações úteis (Makefile)

Logs e diagnóstico:

```bash
make logs        # split 2x2: Nginx | PostgreSQL | Portainer (requer tmux)
make nginx-logs   # apenas Nginx
make postgres-logs  # apenas PostgreSQL
make portainer-logos # apenas Portainer
make tail        # últimos logs de todos
```

---
