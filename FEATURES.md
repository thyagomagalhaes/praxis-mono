# Práxis SUAS - 

##  
> **Observação**
> Seguir passo a passo.

> [!WARNING]
> Garantir que o S.O. e o antivírus estejam atualizados.


## APRESENTAÇÃO: FALAR DA CONSTRUÇÃO DO MVP PRAXIS SUAS MANDU 

- **Linguagem Ubíqua** ;
- **Explorar todos os cenários** do atendimento: apesar do serviço não ser de competência do CRAS TODA VISIBILIDADE É NOSSA uma vez que é aqui que os usuários dão entrada e os 
terceiros envolvidos não são assertivos;
- Exemplicar as dificuldades e problemas enfrentados; vislumbrar melhorias; 
- mandu.praxissuas.social.local ;
- revelar período de **prova de conceito** ( como etapa de homologação de `tag / release`); 
- exibir calendário de etapas.

## MÓDULOS

- [Indivíduos](docs/individuos.md)
- [Famílias e habitação( territorialidade )](docs/familias.md)
- [Plantão Social](docs/plantao.md)


## FEDERAÇÃO

- Listar nacionalidades dos países;
- Listar siglas de estados por nacionalidade informada;
- Listar nomes de estados por nacionalidade informada; 


## TERRITÓRIO

- Listar municípios por ID do estado  
- Buscar estado do por ID do município;
- Listar nomes dos bairros por ID do município;
- Listar nome dos bairros do recife por RPA
- Buscar a RPA de um bairro por ID deste;


## HABITAÇÃO

- Buscar endereço por logradouro informado no ViaCEP;
- Buscar endereço por CEP no ViaCEP
- Buscar município de bairro informado;

## FAMÍLIA

- Long id
- String codigoCadunico
- Individuo responsável
- List< Individuo > integrantes;
- List< RelacaoFamiliar ou VínculoAfetivoParental ou Parentesco > ( PAI, MÃE, E ETC ) parentescos 
- EnderecoDomiciliar domicilio;

### resources

- Formar familia a partir indivíduos já cadastrados
- Formar família ( a partir do código da família no cadúnico )
- Formar familia a partir do nis do rf
- Vincular indivíduo(s) a família ( quando familia já existe e receverá novo integrante )
- Desvincular indivíduo(s) da família ( integrante sairá do núcleo familiar
- Designar/Nomear RF da família
- Buscar família por CPF do RF
- Buscar família por codigo familiar cadunico
- Associar endereco domiciliar ( adicionar/atualizar endereço);
- buscar endereco por parte do logradouro + recife
- buscar endereco por cep

## PLANTÃO SOCIAL ( entidade PlantaoSocial)


> **Observação**
> Aplicar o TEMPLATE METHOD.

1. Data de abertura:
2. Data de conclusão do atendimento
3. String Título:
4. String Descrição:
5. FormaAcolhida ( `DEMANDA ESPONTÂNEA`, `BUSCA ATIVA - VISITA DOMICILIAR`, `BUSCA ATIVA - AÇÃO NO TERRITÓRIO / CRAS MANDÚ PRESENTE`,  DESPACHO INTERNO, ENCAMINHAMENTO REDE E ENCAMINHAMENTO DE TERCEIROS ):
6. ComponenteServiço (´VEM LIVRE ACESSO´, `CARTEIRA PESSOA IDOSA`): 
7. TipoServiço ( IDOSO - IMPRESSÃO, IDOSO - REIMPRESSÃO, IDOSO - CONSULTA, VLA - ENTRADA, VLA - CONSULTA ): 
8. String Observações: 


## VEM LIVRE ACESSO:

- rotas em:  *livreacesso/{requerenteID}/* ou  */individuos/{requerenteId}/livreacesso* ; 
- AtendimentoCartaoLivreAcesso extends PlantaoSocial;

9. **Documento do requerente e do responsável legal**( quando necessário):  

10. **StatusEntrada**:

- `NOVO`: criado mas não enviado a SEAD. Entrada aguardando escalonamento a solucionador;
- `PROCESSANDO ( ATRIBUÍDO )`: entrada recém criada precisa ser atribuída a algum responsável pela entrada. Durante esse status o responsável acessa o SEI e preenche as informações com os dados do requente e encaminha o processo. Uma vez o processo atribuído a um responsável este não pode sofrer permuta de atribuição.
- `PROCESSANDO ( ENCAMINHADO )`: Encaminhado a SEAD. Aguardando data limite de feedback para acionar ou não a SEAD em que ligaremos pro usuário se necessário 
- `PROCESSANDO (PLANEJADO )`: Data da perícia definida. Aguardando dia da perícia e ligamos pro usuário nesse dia para lembrá-lo da perícia.
- `PENDENTE`: Falta devolutiva de algum ator envolvido ( documentação de requerente, telefones e e-mails de contato, ajuste de colaborador e etc )
- `SOLUCIONADO`: A partir do primeiro dia útil da perícia. Realizamos a Confirmação de que a perícia foi realizada. 
- `FECHADO OU ENCERRADO`: 10 dias úteis após a confirmação da perícia entramos em contato com o usuário para ver se ele recebeu a carteira

11. **HistóricoEntrada**:

- descricaoTarefa:
- TipoTarefa ( `CONTATAR REQUERENTE`, `ACIONAR SEAD`, `NOTIFICAR SOLUCIONADOR`, `NOTIFICAR AVALIADOR` )
- dataExecucao:
- Usuario realizador:
- Axexar captura de tela da tarefa e/ou documentos:

### resources

- Criar entrada  ( iniciar/abertura entrada )
- Atualizar entrada ( Cancelar entrada, Solucionar,  Colocar em espera[], Pendente[volta com documentação], Aguardando)
- Finalizar entrada ( concluir entrada );
- Buscar entrada por ID;
- Listar entradas por CPF do requerente;
- Buscar entrada mais recente por CPF do requerente;

## CARTEIRA DA PESSOA IDOSA:

- rotas em: `pessoaidosa/{requerenteID}` ;
- AtendimentoCarteiraPessoaIdosa extends PlantaoSocial;



## PAIF

- rotas em `paif/{familiaID}/evoluir` ;
- AtendimentoPaif extends PlantaoSocial

- EvolucaoFamiliar


- EvolucionalAcompanhamento

List Date dataEvolucao
List String descricao
List Encaminhamento
List Concessao ( Beneficio Eventuale etc
List Natureza ( cesta básica
Instrumental instrumental ( embeddable )

Instrumental

TipoInstrumental ( `PRONTUÁRIO SUAS` , `FAF`
identificacao-registro
String descricao_arquivo ( CAIXA 34, PASTA 21 )

BeneficioEventual

- natureza

Encaminhamento

9. Documentos da família:

### Endpoints:

- Registrar evolução familiar / atendimento eventual  ( conceder cesta basica, e etc )
- Evadir / desligar família do serviço ( familia não ingressa ou desligada )
- Ingressar família no serviço (  Família ingressa e em acompanhamento )

## CADUNICO 

- rotas em - ( `cadunico/{familiaID}/`
- AtendimentoCadUnico extends PlantaoSocial


#### Juntar PDFs

- Juntar PDF do relatório Jasper com PDF do Escaneamento de documentos. 

* [JasperReports com outros PDFs e imagens](https://pt.stackoverflow.com/questions/384296/unir-relat%C3%B3rio-do-jasperreport-com-outros-pdfs-e-imagens)

* [Uso da Classe PdfCopy da API iTEXT](https://api.itextpdf.com/iText5/java/5.5.9/)

