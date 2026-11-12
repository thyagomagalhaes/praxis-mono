package app.suasflux.modulo.prevencao.internal.domain;

import lombok.Getter;

@Getter
public enum TipificacaoBasica {
	
	PAIF("Serviço de Proteção e Atendimento Integral à Família"), 
	SCFV("Serviço de Convivência e Fortalecimento de Vínculos"),
	PBDPDI("Serviço de Proteção Social Básica no Domicílio para\r\n"
			+ "Pessoas com Deficiência e Idosas");

	private final String descricao;

	TipificacaoBasica(String descricao) {
		this.descricao = descricao;
	}

	public String getDescricao() {
		return descricao;
	}


}
