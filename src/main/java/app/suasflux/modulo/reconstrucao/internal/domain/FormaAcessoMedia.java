package app.suasflux.modulo.reconstrucao.internal.domain;

import lombok.Getter;

@Getter
public enum FormaAcessoMedia {
	
	ESPONTANEA("Por demanda / procura espontânea"),
	PS("Por identificação e encaminhamento dos serviços de proteção"),
	VIGILANCIA("Por identificação e encaminhamento da vigilância social"), 
	REDE("Por encaminhamento da rede socioassistencial"),
	SETORIAL("Por encaminhamento das demais políticas públicas setoriais"),
	GARANTIA("Por encaminhamento dos demais órgãos do Sistema de Garantia de Direitos "),
	SEGURANCA("Por encaminhamento do Sistema de Segurança Pública");

	private final String descricao;

	FormaAcessoMedia(String descricao) {
		this.descricao = descricao;
	}

	public String getDescricao() {
		return descricao;
	}

}
