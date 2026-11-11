package app.suasflux.modulo.acompanhamento.internal.domain;


import lombok.Getter;

@Getter
public enum TipificacaoMedia {
	
	PAEFI("Serviço de Proteção e Atendimento Especializado a Fa-\r\n"
			+ "mílias e Indivíduos "), 
	ABORDAGEM("Serviço Especializado em Abordagem Social"),
    LA("Serviço de proteção social a adolescentes em cumpri-\r\n"
    		+ "mento de medida socioeducativa de Liberdade Assistida"),
    PSC("Serviço de proteção social a adolescentes em cumpri-\r\n"
    		+ "mento de medida socioeducativa de Prestação de Serviços à Comunidade"),
    PEPDIF("Serviço de Proteção Social Especial para Pessoas com Deficiência, "
    		+ "Idosas e suas Famílias\r\n"),
	SESR("Serviço Especializado para Pessoas em Situação de Rua");

	private final String descricao;

	TipificacaoMedia(String descricao) {
		this.descricao = descricao;
	}

	public String getDescricao() {
		return descricao;
	}

}
