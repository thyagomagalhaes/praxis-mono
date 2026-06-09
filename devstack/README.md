# 🧭 Práxis DevStack — Stack Local

- Infraestrutura de desenvolvimento pronta para uso com **Docker Compose**, focada em padronizar o sobe / desce da operação dos seguintes serviços de apoio entre projetos: 

    - Portainer
    - Nginx Proxy Manager
    - PostgreSQL + pgAdmin

---

## ⚙️ Estrutura do diretório

A estrutura é organizada por serviço e por arquivos de composição:

```
compose/
  ├── docker-compose.base.yml
  ├── docker-compose.nginx.yml
  ├── docker-compose.portainer.yml
  └── docker-compose.postgres.yml
```

Principais papéis:

- `compose/*.yml`: Composição dos serviços (base, PostgreSQL + pgAdmin, Nginx, Portainer e etc ).

---

## 🚀 Como usar (via Makefile)

1.  Primeiro faça a adição dos `virtual hosts`:

```bash
127.0.0.1 localhost
127.0.0.1 postgresql
127.0.0.1 praxis.local
127.0.0.1 nginx.praxis.local 
127.0.0.1 pgadmin.praxis.local
127.0.0.1 portainer.praxis.local
```

2.  Certifique-se de ter **Docker** e **Docker Compose** instalados;
3.  Use os alvos do `Makefile` para subir os serviços desejados:

<!-- end list -->

```bash
# Todos os serviços (Portainer, Nginx, PostgreSQL)
make up

# Somente Portainer
make portainer-up

# Somente PostgreSQL + pgAdmin
make postgres-up

# Somente Nginx Proxy Manager
make nginx-up

# Para encerrar tudo
make down
```

---

## 🚀 Serviços Expostos ( App rodando no Host )

| Serviço |  Função | Porta | Virtual Hosts / Nginx Proxy | Redirection Hosts | Streams | Protocolo TCP/IP |
| --- | --- | --- | --- | --- |  --- |  --- |
| Nginx Proxy Manager | Proxy reverso, redirections e streams | `81` | `nginx.praxis.local` | --- | --- | HTTP |
| PostgreSQL | URL de conexão com o SGBD | `5432` | --- | --- | `postgresql` OU `nome_container` OU `ip_container`  |  JDBC:POSTGRESQL  |
| pgAdmin |  Console / admin web do SGBD | `5050` | `pgadmin.praxis.local` | --- | --- | HTTP |
| Portainer CE | Console / admin web para orquestração do Docker Compose | `9443` | `portainer.praxis.local` | --- | --- | HTTP |

---


## 🔌 Conectando seu backend (Rodando no Host)

Como seu backend (rodando fora de containers, na sua IDE) deve se conectar à stack Docker:


- **PostgreSQL:** host `postgresql` ou `praxis.local` e porta `5432`;

(Se o backend rodar _dentro_ da rede `praxis-network`, use o nome do container como host e a porta interna. Ex: `http://pgadmin:5050`).

---

## 🧰 Operações úteis (Makefile)

- Logs e diagnóstico:

```bash
make logs        # split 2x2: Nginx | PostgreSQL | Portainer (requer tmux)
make nginx-logs   # apenas Nginx
make postgres-logs  # apenas PostgreSQL
make portainer-logs # apenas Portainer
make tail        # últimos logs de todos
```

---
