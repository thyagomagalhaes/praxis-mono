--
-- Configuracoes iniciais
-- MySQL: USE set foreign_key_checks=0 para "desativar" ou set foreign_key_checks=0 "ativar" a chave 
-- estrangeira. auxilia na inserção de dados
--


-- Para "desativar" a chave estrangeira
SET session_replication_role = 'replica';


-- Para limpar carga existente
delete from bairro;



--
-- Inserindo dados na tabela "bairro"
--


INSERT INTO "bairro" (id, nome, subdistrito, municipio_id) VALUES
(1, 'Aflitos', 'RPA-3', 3315),
(2, 'Afogados', 'RPA-5', 3315),
(3, 'Água Fria', 'RPA-2', 3315),
(4, 'Alto do Mandú', 'RPA-3', 3315),
(5, 'Alto José Bonifácio', 'RPA-3', 3315),
(6, 'Alto Jose do Pinho', 'RPA-3', 3315),
(7, 'Alto Santa Terezinha', 'RPA-2', 3315),
(8, 'Apipucos', 'RPA-3', 3315),
(9, 'Areias', 'RPA-5', 3315),
(10, 'Arruda', 'RPA-2', 3315),
(11, 'Barro', 'RPA-5', 3315),
(12, 'Beberibe', 'RPA-2', 3315),
(13, 'Boa Viagem', 'RPA-6', 3315),
(14, 'Boa Vista', 'RPA-1', 3315),
(15, 'Bomba do Hemetério', 'RPA-2', 3315),
(16, 'Bongi', 'RPA-5', 3315),
(17, 'Brasilia Teimosa', 'RPA-6', 3315),
(18, 'Brejo da Guabiraba', 'RPA-3', 3315),
(19, 'Brejo de Beberibe', 'RPA-3', 3315),
(20, 'Cabanga', 'RPA-1', 3315),
(21, 'Caçote', 'RPA-5', 3315),
(22, 'Cajueiro', 'RPA-2', 3315),
(23, 'Campina do Barreto', 'RPA-2', 3315),
(24, 'Campo Grande', 'RPA-2', 3315),
(25, 'Casa Amarela', 'RPA-3', 3315),
(26, 'Casa Forte', 'RPA-3', 3315),
(27, 'Caxangá', 'RPA-4', 3315),
(28, 'Cidade Universitária', 'RPA-4', 3315),
(29, 'Coelhos', 'RPA-1', 3315),
(30, 'Cohab', 'RPA-6', 3315),
(31, 'Coqueiral', 'RPA-5', 3315),
(32, 'Cordeiro', 'RPA-4', 3315),
(33, 'Córrego do Jenipapo', 'RPA-3', 3315),
(34, 'Curado', 'RPA-5', 3315),
(35, 'Derby', 'RPA-3', 3315),
(36, 'Dois Irmãos', 'RPA-3', 3315),
(37, 'Dois Unidos', 'RPA-2', 3315),
(38, 'Encruzilhada', 'RPA-2', 3315),
(39, 'Engenho do Meio', 'RPA-4', 3315),
(40, 'Espinheiro', 'RPA-3', 3315),
(41, 'Estância', 'RPA-5', 3315),
(42, 'Fundão', 'RPA-2', 3315),
(43, 'Graças', 'RPA-3', 3315),
(44, 'Guabiraba', 'RPA-3', 3315),
(45, 'Hipódromo', 'RPA-2', 3315),
(46, 'Ibura', 'RPA-6', 3315),
(47, 'Ilha do Leite', 'RPA-1', 3315),
(48, 'Ilha do Retiro','RPA-4', 3315),
(49, 'Ilha Joana Bezerra', 'RPA-1', 3315),
(50, 'Imbiribeira', 'RPA-6', 3315),
(51, 'Ipsep', 'RPA-6', 3315),
(52, 'Iputinga', 'RPA-4', 3315),
(53, 'Jaqueira', 'RPA-3', 3315),
(54, 'Jardim São Paulo', 'RPA-5', 3315),
(55, 'Jiquiá', 'RPA-5', 3315),
(56, 'Jordão', 'RPA-6', 3315),
(57, 'Linha Do Tiro', 'RPA-2', 3315),
(58, 'Macaxeira', 'RPA-3', 3315),
(59, 'Madalena', 'RPA-4', 3315),
(60, 'Mangabeira', 'RPA-3', 3315),
(61, 'Mangueira', 'RPA-5', 3315),
(62, 'Monteiro', 'RPA-3', 3315),
(63, 'Morro da Conceição', 'RPA-3', 3315),
(64, 'Mustardinha', 'RPA-5', 3315),
(65, 'Nova Descoberta','RPA-3', 3315),
(66, 'Paissandú', 'RPA-1', 3315),
(67, 'Parnamirim', 'RPA-3', 3315),
(68, 'Passarinho', 'RPA-3', 3315),
(69, 'Pau Ferro', 'RPA-3', 3315),
(70, 'Peixinhos', 'RPA-2', 3315),
(71, 'Pina', 'RPA-6', 3315),
(72, 'Poço', 'RPA-3', 3315),
(73, 'Ponto de Parada', 'RPA-2', 3315),
(74, 'Porto da Madeira', 'RPA-2', 3315),
(75, 'Prado', 'RPA-4', 3315),
(76, 'Recife, bairro do', 'RPA-1', 3315),
(77, 'Rosarinho', 'RPA-2', 3315),
(78, 'San Martin', 'RPA-5', 3315),
(79, 'Sancho', 'RPA-5', 3315),
(80, 'Santana', 'RPA-3', 3315), 
(81, 'Santo Amaro', 'RPA-1', 3315),
(82, 'Santo Antônio', 'RPA-1', 3315),
(83, 'São José', 'RPA-1', 3315),
(84, 'Sitio dos Pintos', 'RPA-3', 3315),
(85, 'Soledade', 'RPA-1', 3315),
(86, 'Tamarineira', 'RPA-3', 3315),
(87, 'Tejipió', 'RPA-5', 3315),
(88, 'Torre', 'RPA-4', 3315),
(89, 'Torreão', 'RPA-2', 3315),
(90, 'Torrões', 'RPA-4', 3315),
(91, 'Totó', 'RPA-5', 3315),
(92, 'Várzea', 'RPA-4', 3315),
(93, 'Vasco da Gama', 'RPA-3', 3315),
(94, 'Zumbi', 'RPA-4', 3315);

-- Para "reativar" a chave estrangeira
SET session_replication_role = 'origin';



--
-- Name: cidade_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

-- SELECT pg_catalog.setval('public.cidade_id_seq', 1, false);


--
-- Name: cidade cidade_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

-- ALTER TABLE ONLY public.cidade ADD CONSTRAINT cidade_pkey PRIMARY KEY (id);
