

-- 1. Tabela de Bairros
CREATE TABLE bairros (
    id_bairro SERIAL PRIMARY KEY,
    codigo_ibge_municipio CHAR(7) NOT NULL,
    codigo_bairro_oficial VARCHAR(20),
    nome_bairro VARCHAR(120) NOT NULL,
    zona_administrativa VARCHAR(50),
    is_especial BOOLEAN DEFAULT FALSE,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (codigo_ibge_municipio, nome_bairro)
);

-- 2. Tabela de Territórios
CREATE TABLE territorios (
    id_territorio SERIAL PRIMARY KEY,
    id_bairro INT NOT NULL REFERENCES bairros(id_bairro) ON DELETE RESTRICT,
    id_equipamento_ref INT NOT NULL, -- FK para tabela de unidades (CRAS/CREAS/Centro POP)
    codigo_territorio VARCHAR(30) UNIQUE NOT NULL,
    nome_territorio VARCHAR(150) NOT NULL,
    apelido_local VARCHAR(150),
    tipo_zona VARCHAR(30) NOT NULL CHECK (
        tipo_zona IN ('URBANA_CENTRAL', 'URBANA_PERIFERICA', 'RURAL', 'COMUNIDADE_TRADICIONAL', 'CENA_USO_RUA')
    ),
    referencia_geografica TEXT,
    area_poligono GEOMETRY(MultiPolygon, 4674),
    possui_equipe_volante BOOLEAN DEFAULT FALSE,
    oficializado BOOLEAN DEFAULT TRUE,
    is_fallback BOOLEAN DEFAULT FALSE,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_bairro, nome_territorio)
);

-- Índices para performance de busca e mapa
CREATE INDEX idx_territorios_bairro ON territorios(id_bairro);
CREATE INDEX idx_territorios_poligono ON territorios USING GIST (area_poligono);

-- Garante que cada bairro tenha no máximo UM território marcado como fallback
CREATE UNIQUE INDEX idx_unico_fallback_por_bairro 
ON territorios(id_bairro) WHERE (is_fallback = TRUE);

-- 3. Tabela de Endereço Familiar (com histórico e status)
CREATE TABLE familia_enderecos (
    id_endereco SERIAL PRIMARY KEY,
    id_familia INT NOT NULL, -- FK para tabela de familias
    id_bairro INT NOT NULL REFERENCES bairros(id_bairro) ON DELETE RESTRICT,
    id_territorio INT NOT NULL REFERENCES territorios(id_territorio) ON DELETE RESTRICT,
    status_territorializacao VARCHAR(30) NOT NULL DEFAULT 'PENDENTE_ANALISE' CHECK (
        status_territorializacao IN ('VINCULADO_AUTO', 'VINCULADO_MANUAL', 'PENDENTE_ANALISE', 'SITUACAO_RUA')
    ),
    cep CHAR(8),
    logradouro VARCHAR(150),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    ponto_referencia TEXT,
    coordenada GEOMETRY(Point, 4674),
    endereco_atual BOOLEAN DEFAULT TRUE,
    data_inicio DATE NOT NULL DEFAULT CURRENT_DATE,
    data_fim DATE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para consultas rápidas de prontuário e georreferenciamento
CREATE INDEX idx_familia_enderecos_familia ON familia_enderecos(id_familia);
CREATE INDEX idx_familia_enderecos_territorio ON familia_enderecos(id_territorio);
CREATE INDEX idx_familia_enderecos_pendentes ON familia_enderecos(status_territorializacao) WHERE status_territorializacao = 'PENDENTE_ANALISE';
CREATE INDEX idx_familia_enderecos_ponto ON familia_enderecos USING GIST (coordenada);

-- Regra de integridade: Uma família só pode ter UM endereço ativo (atual = TRUE) por vez
CREATE UNIQUE INDEX idx_familia_unico_endereco_atual 
ON familia_enderecos(id_familia) WHERE (endereco_atual = TRUE);