# 🧭 SUAS Flux DevStack — Stack Local

- Infraestrutura de desenvolvimento pronta para uso com **Docker Compose**, focada em padronizar o sobe / desce da operação dos seguintes serviços de apoio entre projetos: 

    - Portainer
    - Ngrok
    - Nginx Proxy Manager
    - PostgreSQL + pgAdmin
    - Mysql + PhpMyAdmin
    - MariaDB + Adminer
    - Redis + Redis Insight
    - RabbitMQ
    - Minio API + Minio Console
    - Sendgrid
    - Keycloak
    - Vault
    

---

## ⚙️ Estrutura do diretório

A estrutura é organizada por serviço e por arquivos de composição:

```
compose/
  ├── docker-compose.base.yml
  ├── docker-compose.keycloak.yml
  ├── docker-compose.mariadb.yml
  ├── docker-compose.minio.yml
  ├── docker-compose.mysql.yml
  ├── docker-compose.nginx.yml
  ├── docker-compose.ngrok.yml
  ├── docker-compose.portainer.yml
  ├── docker-compose.postgres.yml
  ├── docker-compose.rabbitmq.yml
  ├── docker-compose.redis.yml
  ├── docker-compose.sendgrid.yml
  └── docker-compose.vault.yml
```

Principais papéis:

- `compose/*.yml`: Composição dos serviços (base, PostgreSQL + pgAdmin, Nginx, Portainer e etc ).

---

## 🚀 Como usar (via Makefile)

1.  Primeiro faça as adições dos `virtual hosts` e dos `streams`:

```bash
# Virtual hosts

127.0.0.1 nginx
127.0.0.1 suasflux.prem
127.0.0.1 nginx.suasflux.prem  ngrok.suasflux.prem
127.0.0.1 keycloak.suasflux.prem portainer.suasflux.prem
127.0.0.1 www.catorecomeco.dev www.catorecomeco.hml
127.0.0.1 mail.suasflux.dev mail.suasflux.hml
127.0.0.1 adminer.suasflux.prem minio.suasflux.prem pgadmin.suasflux.prem rabbitmq.suasflux.prem redisinsight.suasflux.prem phpmyadmin.suasflux.prem vault.suasflux.prem

# Virtual hosts with custom locations
# Realms keycloak

127.0.0.1 sso.suasflux.dev sso.suasflux.hml

# Streams

127.0.0.1 mariadb.dev minio.dev mysql.dev postgresql.dev rabbitmq.dev redis.dev sendgrid.dev
127.0.0.1 mariadb.hml minio.hml mysql.hml postgresql.hml rabbitmq.hml redis.hml sendgrid.hml
```

2. Certifique-se de ter o **Certbot** instalado. Configure os domínios `HTTPS` no **NGINX**;
3. Cheque o status e habilite o firewall do host se necessário: para liberar as portas **HTTP e HTTPS**:

```bash
sudo ufw status
Estado: inativo
```

```bash
sudo ufw enable
Firewall está ativo e habilitado na inicialização do sistema
```

```bash
sudo ufw allow http
sudo ufw allow https
```

```bash
~$ sudo ufw status
Estado: ativo

Para                       Ação        De
----                       ----        --
80/tcp                     ALLOW       Anywhere                  
443                        ALLOW       Anywhere                  
80/tcp (v6)                ALLOW       Anywhere (v6)             
443 (v6)                   ALLOW       Anywhere (v6)  
```


3. Certifique-se de ter **Docker** e **Docker Compose** instalados;
4. Use os alvos do `Makefile` para subir os serviços desejados:
5. Para ver se tem uma porta ocupada ( identificamos o PID da porta ) sudo lsof -i <protocolo>:<porta> `sudo lsof -i TCP:8080` ; Para liberar a porta faça um: `sudo kill -9 <PID>` ; 

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

- É bom ao dar `docker system prune --all` um depois de *derrubar os serviços e assim limpar o Docker*.  

5. Insira as entradas do **NGINX** com os `virtual hosts específicos`:

- **Proxies**: `pgAdmin`, `portainer` e `nginx`
- **Streams**: Para o serviço do `PostgreSQL` e outros que rodam sobre o TCP
- **Redirections**: Redirecionar o `localhost` e o `127.0.0.1`para a `nginx`. A página de apresentação do `nginx` também deve ser *desabilitada*;

6. Reinicie o host.


---

## 🚀 Serviços Expostos ( App rodando no Host )

| Serviço |  Função | Porta | Virtual Hosts / Nginx Proxy | Redirection Hosts | Streams | Protocolo TCP/IP |
| --- | --- | --- | --- | --- |  --- |  --- |
| Keycloak | Identity and Access Management - IAM | `8080` | `keycloak.tech` | --- | --- | HTTP |
| Realm Práxis | SSO Práxis | `8181` | `sso.praxis.dev` | --- | --- | HTTP |
| Práxis Monolito | Práxis | `8585` | `www.praxis.dev` | --- | --- | HTTP |
| MySQL | URL de conexão com o SGBD | `3306` | --- | --- | `mysql` OU `nome_container` OU `ip_container`  |  JDBC:MYSQL  |
| Nginx Proxy Manager | Proxy reverso, redirections e streams | `81` | `manager.nginx.tech` | --- | --- | HTTP |
| PostgreSQL | URL de conexão com o SGBD | `5432` | --- | --- | `postgresql` OU `nome_container` OU `ip_container`  |  JDBC:POSTGRESQL  |
| pgAdmin |  Console / admin web do SGBD | `5050` | `pgadmin.tech` | --- | --- | HTTP |
| Redis | URL de conexão com o SGBD | `5432` | --- | --- | `redis` OU `nome_container` OU `ip_container`  |  JDBC:REDIS  |
| RedisInsight |  Console / admin web do SGBD | `5050` | `redisinsight.tech` | --- | --- | HTTP |
| Portainer CE | Console / admin web para orquestração do Docker Compose | `9443` | `portainer.tech` | --- | --- | HTTP |

---


## 🔌 Conectando seu backend (Rodando no Host)

Como seu backend (rodando fora de containers, na sua IDE) deve se conectar à stack Docker:


- **PostgreSQL:**

  - `URL`: jdbc:postgresql://postgresql.praxis.local , não precisando informar a porta uma vez que está configurado o **stream Nginx ** 
  - Se o backend rodar _dentro_ da rede `praxis-network`, use o nome do container como host e a porta interna. Ex: `http://pgadmin:5050`).

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
