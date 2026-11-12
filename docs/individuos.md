# Indivíduos 

## Campos

- Long id;
- String nomeCivil;
- String nomeSocial;
- String nis;
- String cpf;
- data nascimento;
- int idade ( anotado com @Transient );
- rg
- orgaoExpedidor
- SexoBiologico sexo;
- List< Individuo > representados
- List< TipoRepresentacao > representacoes ( TUTOR(A), CURADOR(A), GENITOR(A), PATRILINEAR (AVÔ), MATRILINEAR(AVÓ) )

### resources

- Adicionar individuo;
- Atualizar individuo;
- Buscar individuo por cpf;
- Buscar individuo por nis;
- Listar individuos
- nomear representante;
- retirar representacao;
- Buscar naturalidade do indivíduo ( formato: `Município - UF` );


