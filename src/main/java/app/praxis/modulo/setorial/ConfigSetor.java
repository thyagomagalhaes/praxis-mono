package app.praxis.modulo.setorial;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

// Classe inner enum

public class ConfigSetor{

	public static final String CRAS = "CENTRO DE REFERÊNCIA DE ASSISTENCIA SOCIAL";

	
	
	// Uso dos enums como atributos da classe
	private TipoGerencia gerencia;
	private TipoDivisao divisao;
	private TipoUnidade unidade;

	public ConfigSetor(TipoGerencia gerencia, TipoDivisao divisao, TipoUnidade unidade) {
		this.gerencia = gerencia;
		this.divisao = divisao;
		this.unidade = unidade;
	}


	public TipoGerencia getGerencia() {
		return gerencia;
	}

	public TipoDivisao getDivisao() {
		return divisao;
	}
	
	public TipoUnidade getUnidade() {
		return unidade;
	}




	//Enum para o Tipo de Gerencia
	public enum TipoGerencia{
		BASICA("GPSB","GERÊNCIA DE PROTEÇÃO SOCIAL BÁSICA"),
		MEDIA("GPSEMC","GERÊNCIA DE PROTEÇÃO SOCIAL ESPECIAL DE MEDIA COMPLEXIDADE"),
		ALTA("GPSEAC","GERÊNCIA DE PROTEÇÃO SOCIAL ESPECIAL DE ALTA COMPLEXIDADE");

		private String sigla;
		private String nome;
		private List<TipoGerencia> gerencias;

		TipoGerencia(String sigla, String nome, TipoGerencia... gerencias) {
			this.nome=nome;
			this.sigla=sigla;
			this.gerencias=Arrays.asList(gerencias);

		}

		public String getNome() {
			return this.nome;
		}

		public String getSigla() {
			return this.sigla;
		}	

		public List<String> nomesGerencias(){
			List<String> nomesGerencias = new ArrayList<>();
			for (TipoGerencia gerencias : TipoGerencia.values()) {
				nomesGerencias.add(this.getNome());
			}
			return nomesGerencias;
		}



	}

	public enum TipoDivisao{
		ADULTO("DAAF","DIVISÃO DE ACOLHIMENTO DE ADULTOS E FAMILIAS"),
		INFANTOJUVENIL("DACA","DIVISÃO DE ACOLHIMENTO DE CRIANÇAS E ADOLESCENTES"),
		IDOSO("DAPI","DIVISÃO DE ACOLHIMENTO DE PESSOAS IDOSAS");

		private String sigla;
		private String nome;
		private List<TipoDivisao> divisoes;

		public String getNome() {
			return this.nome;
		}

		public String getSigla() {
			return this.sigla;
		}

		TipoDivisao(String sigla, String nome, TipoDivisao... divisoes){
			this.nome=nome;
			this.sigla=sigla;
			this.divisoes=Arrays.asList(divisoes);

		}

		public List<String> nomesDivisoes(){
			List<String> nomesDivisoes = new ArrayList<>();
			for (TipoDivisao divisoes : TipoDivisao.values()) {
				nomesDivisoes.add(this.getNome());
			}
			return nomesDivisoes;
		}


	}
	
	public enum TipoUnidade{
		
		
		ABRIGO("ABRIGO EMERGENCIAL"),
		CAP("CASA DE ACOLHIDA PERMANENTE"),
		CASA_PASSAGEM("CASA DE PASSAGEM"),
		CAT("CASA DE ACOLHIDA TEMPORÁRIA"),
		CRAS("CENTRO DE REFERÊNCIA DE ASSISTENCIA SOCIAL "),
		CREAS("CENTRO DE REFERÊNCIA ESPECIALIZADO DE ASSISTENCIA SOCIAL"),
		CENTRO_POP("CENTRO DE REFERÊNCIA ESPECIALIZADO PARA POPULAÇÃO EM SITUAÇÃO DE RUA"),
		LAR("CASA LAR"),
		RESTAURANTE("RESTAURANTE POPULAR");

		private String nome;
		private List<TipoUnidade> unidades;

		
		TipoUnidade(String nome, TipoUnidade... unidades){
			this.nome=nome;
			this.unidades=Arrays.asList(unidades);

		}
	}
	

}		



