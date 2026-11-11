package app.suasflux.modulo.acolhimento.internal.domain;

import lombok.Getter;

@Getter
public enum TipificacaoAlta {
	
	SAI("Serviço de Acolhimento Institucional"), 
	SAR("Serviço de Acolhimento em República"),
	SAFA("Serviço de Acolhimento em Família Acolhedora"),
	EMERGENCIAL("Serviço de proteção em situações de calamidades pú-\r\n"
			+ "blicas e de emergências");

	private final String descricao;

	TipificacaoAlta(String descricao) {
		this.descricao = descricao;
	}

	public String getDescricao() {
		return descricao;
	}

}
