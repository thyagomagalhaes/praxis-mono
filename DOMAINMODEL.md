# suasflux-monolito
Conjunto de soluções digitais na forma de webservices que servem de hub para prestação de serviços e atendimentos pelos municípios às famílias e indivíduos em condição de vulnerabilidade social; em consonância com as tipificações do Sistema Único da Assistência Social ( SUAS ); com acréscimo de experiências aplicadas no município do Recife - PE.

> ### Modelo de domínio

#### Endereço
  Todo Grupo familiar tem `um e somente um` **Endereço** .
  
  Um **Endereço** é composto de um `logradouro` ( nome de rua, avanida, travessa e etc), `numero` ( identificação numérica do domicílio no logradouro ), `Tipo de Moradia` ( qualificação da moradia: `CASA`, `APARTAMENTO` e etc),

Ele tem a estrutura de um `conjunto domiciliar` (`TERRENO` dividido ou não por familiares, `CONDOMÍNIO`, `VILA` e etc) que tem um `nome` ou não. Ele também pode estar numa `localidade` (`ASSENTAMENTO`, `COMUNIDADE`, `QUADRA` e etc ) que também tem um `nome` e ter ou não um `ponto de referência`.

Por fim, o endereço está vinculado a uma `região política administativa`, um `bairro`, um `cep`, uma `cidade` e um `estado`.

* [Domínio de Usuários](https://github.com/thyagomagalhaes/balcao-focal-SUAS/blob/main/socialjobber-api/uml/dominio-usuario.png)

#### Juntar PDFs

- Juntar PDF do relatório Jasper com PDF do Escaneamento de documentos. 

* [JasperReports com outros PDFs e imagens](https://pt.stackoverflow.com/questions/384296/unir-relat%C3%B3rio-do-jasperreport-com-outros-pdfs-e-imagens)

* [Uso da Classe PdfCopy da API iTEXT](https://api.itextpdf.com/iText5/java/5.5.9/)


## DIAGNÓSTIGO

> ###  Nome dos repositórios e seus projetos

socialpraxis-hub

 
- duty-rest: serviços do plantão social em geral;
- dispatch-solvers-rest: solucionadores
- dispatch-approvers-rest: aprovadores 
- family-nucleus-rest: família 
- recorder-rest: para os arquivos de FAF, Prontuário e etc; referência SIAS 
- locator-rest: REST API que expõe informações diversas de algumas API's: **dos correios** (buscar endereços dos usuários / familias, a partir da identificação do logradouro + cidade ou CEP ), **do IBGE** 
( assuntos de natalidade `nacionalidade e naturalidade` em documentos como RG; bairros e suas localidades ), de **Dados Recife** (datasets de informações de equipamentos, serviços e etc);
- benefits-rest: REST API que expõe informações diversas sobre os **programas de benefícios ao cidadão oferecidos pelo Governo Federal** ( `BPC, PETI, BOLSA FAMÍLIA E ETC` ) a partir da **API de Dados do Governo Federal**

- socialduty-v1.0
- solvers-v1.0
- approvers-v1.0
- familynucleus-v1.0
- recorder-v1.0
- locator-v1.0
- benefits-v1.0

> ###  Descrição

Conjunto de `soluções digitais` na forma de `webservices` que servem de `hub` para prestação de serviços e 
atendimentos `online` pelos municípios às famílias e indivíduos em condição de vulnerabilidade social; em consonância 
com as tipificações do `Sistema Único da Assistência Social ( SUAS )`.

> ### Abstract

- Nesse momento já estão disponíveis 3 ("três") `soluções back-end`, sendo: 
  - Uma **RESTful API** construída sob o **ecossistema Spring** utilizando `seus projetos mais amplamente ( Spring Boot, Spring MVC e outros)`. Esta expõe endpoints na `representação JSON`;
  - Um **microserviço de envio de email**, com integração ao `Amazon Simple Email Service ( AWS SES )`;
  - Um **microserviço de autenticação e autorização**, integrado a solução de gerenciamento de identidade e acesso open source `Keycloak`; 

- Também é fornecido `collections de endpoints` do HTTP client Postman;
- O próximo passo será a produção de um webservice para consumo da API e apresentação mais amigável aos usuários em **Angular**.
- E no longo prazo uma melhor experiência aos utilizadores do sistema através da integração com o **Liferay Portal** 

> #### Features

1. Indivíduo ( /individuos )
* Cadastrar; 
* Atualizar; 
* Pesquisar por CPF;

2. Família ( /familias )
* Formar família;
* Definir RF;
* Buscar RF;
* Listar indivíduos da família;
* Desmembrar grupo familiar;
* Vincular indivíduo a grupo familiar;
* Desvincular indivíduo de grupo familiar;
 

3. Serviço ( /servicos )
* Registrar / novo;
* Ingressar grupo familiar no serviço;
* Egressar grupo familiar no serviço;

4. Vem Livre Acesso ( /servicos/vlas )
* Inscrever indivíduo;
* Nomear representante;
* Listar todas as inscrições por Status;
* Listar inscrições do indivíduo;

   - Carregar automaticamente o `etarismo` do requerente; validar o `CPF` do usuário; carregar o endereço automaticamente a partir do `CEP` ou `logradouro` ;  
   - Registrar atendimento para o Vem Livre Acesso;
   - Informar usuário para atendimento ( se usuário já registrado, caso contrário cadastrar usuário e vincular a família ou formar família)
   - Tirar foto do Usuário em versão 3x4 utilizando o componente Angular [ngx-webcam](https://www.npmjs.com/package/ngx-webcam) e capturar assinatura;
   - Capturar foto dos documentos no formato A4;
   - Apensar imagens na forma de .PDF;
   - Imprime formulário em versão .PDF e junta com .PDF final dos documentos somatizados;
   
5. Integração com API Externas
* API Dados Recife: ( /apis/dados-recife)
   - Consultas diversas; 
* API de Dados do Governo Federal: ( /apis/dados-federal )
   - Consulta os registros de `Bolsa Família` por CPF/NIS;
   - Consulta as parcelas disponibilizadas pelo `Bolsa Família` pelo CPF/NIS;
   - Consulta os registros de `Benefício de Prestação Continuada ( BPC )` por CPF/NIS;
   - Consulta os registros `Programa de Erradicação do Trabalho Infantil (PETI )` por CPF/NIS;
 * API ViaCEP dos Correios: ( /apis/correios/enderecos )
   - Consulta informações de `endereço` por CEP informado;
 * API de Localidades do IBGE: ( /apis/ibge/municipios )
   - Listagem de `municípios` por `UF`;

6. Others:
- Dashboard de exibição de atendimentos;



#### Juntar PDFs

- Juntar PDF do relatório Jasper com PDF do Escaneamento de documentos. 

* [JasperReports com outros PDFs e imagens](https://pt.stackoverflow.com/questions/384296/unir-relat%C3%B3rio-do-jasperreport-com-outros-pdfs-e-imagens)

* [Uso da Classe PdfCopy da API iTEXT](https://api.itextpdf.com/iText5/java/5.5.9/)

> #### Learn

* [Portal da Transparência do Governo Federal - API de Dados](https://portaldatransparencia.gov.br/api-de-dados)
* [Documentação da API de Dados](https://api.portaldatransparencia.gov.br/swagger-ui.html)
* [API de Localidades do IBGE](https://servicodados.ibge.gov.br/api/docs/localidades#api-Municipios-estadosUFMunicipiosGet)
* [API de Dados Recife](http://dados.recife.pe.gov.br/dataset/divisao-dos-centros-de-referencia-de-assistencia-social/resource/97ee8f79-7b53-40f3-8d57-35f319e5d0ae)
