package app.praxis.modulo.beneficio;

import lombok.Getter;

@Getter
public enum NaturezaOperacao {
	
	
	CREDITO("Cartão de Crédito"),
	DEBITO("Cartão de Débito"),
	DINHEIRO("Pagamento em dinheiro / espécie"),
	PIX("PIX - Pagamento Instântaneo"),
	SAQUE("Saque em Terminal Eletrônico");

	private final String descricao;

	NaturezaOperacao(String descricao) {
		this.descricao = descricao;
	}

	public String getDescricao() {
		return descricao;
	}

}
