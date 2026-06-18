# Práxis — SUAS

- PoC de uma solução digital de **gestão do acolhimento institucional de indivíduos e familias** em condição de vulnerabilidade e/ou risco social;

- Esse projeto nasceu diante da necessidade prospectada de *digitalização dos processos de movimentação de entrada e saída de indivíduos e famílias em Casa de Acolhida do município do Recife/PE*;

- A Casa em questão é a **CAT O Recomeço**, uma *Unidade de Acolhimento institucional de permanência temporária para mulheres e filhos* cujos registros físicos *apresentam dados de famílias acolhidas desde 2002*;

- Informações cadastrais **das famílias e os indivíduos integrantes**, **do período e histórico do acolhimento ( com admissões, saídas e reentradas)**, **do registro de atendimentos ( escutas, acompanhamentos, direcionamentos ), evoluções e encaminhamentos ( e suas formas)**, **administração e prestação de contas de benefícios sóciais** recebidos por àqueles bem como um **painel de observabilidade** - contendo a apresentação de um *dashboard* de informações prestadas em tempo real sobre as *vagas disponíveis e o perfil do público atendido* são algumas das funcionalidades ofertadas neste PoC;   

- A presente solução trata-se de um *webservice monolito modular* com recursos acessados nas formas de `URL's mapeadas em views renderizadas` via **template engine** e endpoints expostos em `JSON` via **REST API** desenvolvido com majoritariamente com **Java 25 e Spring Boot 4 (MVC + REST)**.

- Para detalhes técnicos veja [documentação](docs/README.md);

- Para `ambiente dev` veja [build local](devstack/README.md);

## Abstract

- A proposta é de um MVP como um hub para prestação de serviços e atendimentos pelos municípios às famílias e indivíduos em condição de vulnerabilidade  / ou risco social; em consonância com as tipificações do Sistema Único da Assistência Social ( SUAS ); com acréscimo de experiências aplicadas no município do Recife - PE;

- A assistência social está organizada por meio do Sistema Único de Assistência Social ( SUAS ), presente em todo o Brasil. Seu objetivo é garantir a proteção social aos cidadãos, ou seja, apoio a indivíduos, famílias e à comunidade no enfrentamento de suas dificuldades, por meio de serviços, benefícios, programas e projetos;

- Com um modelo de gestão participativa, o SUAS articula os esforços e os recursos dos municípios, estados e União para a execução e o financiamento da Política Nacional de Assistência Social;

- A política de assistência social oferece um conjunto de serviços para garantir que o cidadão não fique desamparado quando ocorram situações inesperadas, nas quais a sua capacidade de acessar direitos sociais fique comprometida;

- Essas situações podem estar relacionadas à idade da pessoa, a quando algum membro da família depende de cuidados especiais, envolve-se com drogas ou álcool, perde o emprego, envolve-se em situações de violência, membros da família se distanciam ou quando há algum desastre natural na comunidade;

- A assistência social oferta serviços para fortalecer famílias e desenvolver sua autonomia, apoiando-as para que superem eventuais dificuldades e acessem direitos sociais, evitando o rompimento de laços;

- Além disso, trabalha em parceria com outras políticas públicas e encaminha os cidadãos a outros órgãos quando as situações enfrentadas não podem ser resolvidas apenas pela assistência social, como nos casos que envolvem desemprego, violência, doenças, acesso a educação, saneamento básico, moradia, entre outros.



## Estrutura do Projeto

```
praxis-monolito/
├── Procfile                    # Deploy Heroku/Render
├── pom.xml                     # Build Maven
├── src/
│   └── main/
│       ├── java/app/praxis/modulo/
│       │   ├── federacao/      # Controllers REST, Controllers MVC (Thymeleaf), Entidades JPA, Repositórios Spring Data, Camada de serviços, DTOs de API de paises, estados e municípios
│       └── resources/
│           ├── application.properties
│           ├── db
|                ├── migration/ # Scripts Flyway (V01…V16)
|                ├── testdata/  # população BD
│           ├── templates/      # Views Thymeleaf
│   └── test/
│       ├── java/app/praxis/modulo/
│       └── resources/
│           ├── application-mock.properties
├── devstack/
│   └── compose/ # Serviços orquestrados
│   └── .env     # Template de variáveis de ambiente
│   └── README.md 
├── docs/        # Documentação 
│   └── README.md 
├── postman/        # Collections do postman 
├── HELP.md                     # Referências das tecnologias dos starters SPRING
├── README.md                   # Overview do projeto
```

## API REST

| Recurso | Endpoint base | Métodos disponíveis |
|---|---|---|
| País | `/api/paises` | GET |
| Estado | `/api/estados` | GET |
| Município | `/api/municipios` | GET |

## Licença

Este projeto é ...
