package app.suasflux.modulo.diagnostico.internal.domain;

import lombok.Getter;

@Getter
public enum FormaAcessoBasica {
	
	ESPONTANEA("Por demanda / procura espontânea"), 
	BUSCA("Por busca ativa"),
	REDE("Por encaminhamento da rede socioassistencial"),
	SETORIAL("Por encaminhamento das demais políticas públicas setoriais");

	private final String descricao;

	FormaAcessoBasica(String descricao) {
		this.descricao = descricao;
	}

	public String getDescricao() {
		return descricao;
	}

}
