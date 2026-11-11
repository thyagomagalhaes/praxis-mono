package app.suasflux.modulo.acolhimento.internal.domain;

public enum FormaAcessoAlta {
	
	CRIANCA_ADOLESCENTE_JUDICIARIO("Acesso de crianças e adolescentes por determinação "
			+ "do Poder Judiciário"),
	CRIANCA_ADOLESCENTE_CONSELHO("Acesso de crianças e adolescentes por requisição do Conselho "
			+ "Tutelar. "
			+ "Nesse caso, a autoridade competente deverá ser comunica-\r\n"
			+ "da, conforme previsto no Artigo 93 do Estatuto da Criança e do Adolescente"),
	ADULTO_FAMILIA_ESPONTANEA("Acesso de adultos e famílias por demanda / procura espontânea"),
	ADULTO_FAMILIA_ABORDAGEM("Acesso de adultos e famílias por encaminhamento de agentes "
			+ "institucionais de Serviço Especializado em "
			+ "Abordagem Social"), 
	ADULTO_FAMILIA_PS("Acesso de adultos e famílias por identificação e encaminhamento "
			+ "dos serviços de proteção "),
	ADULTO_FAMILIA_SETORIAL("Acesso de adultos e famílias por encaminhamento das demais políticas "
			+ "públicas setoriais "),
	ADULTO_FAMILIA_GARANTIA("Acesso de adultos e famílias por encaminhamento dos demais órgãos "
			+ "do Sistema de Garantia de Direitos"),
	IDOSO_MULHER_PCD_PS("Acesso de Idosos, mulheres em situação de violência e pessoas com "
			+ "deficiência por identificação e encaminhamento dos serviços de proteção"),		
	IDOSO_MULHER_PCD_SETORIAL("Acesso de Idosos, mulheres em situação de violência e pessoas com "
			+ "deficiência por requisição de serviços de políticas públicas setoriais,"),
	IDOSO_MULHER_PCD_MP("Acesso de Idosos, mulheres em situação de violência e pessoas com "
			+ "deficiência por requisição do Ministério Público"),
	IDOSO_MULHER_PCD_PJ("Acesso de Idosos, mulheres em situação de violência e pessoas com "
			+ "deficiência por requisição do Poder Judiciário");

	private final String descricao;

	FormaAcessoAlta(String descricao) {
		this.descricao = descricao;
	}

	public String getDescricao() {
		return descricao;
	}


}
