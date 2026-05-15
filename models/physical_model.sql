CREATE TABLE users (
	id INTEGER PRIMARY KEY,
	name VARCHAR(120) NOT NULL,
	email VARCHAR(255) NOT NULL UNIQUE,
	password_hash VARCHAR(255) NOT NULL,
	phone VARCHAR(20) NOT NULL,
	profile_type VARCHAR(20) NOT NULL,
	cpf VARCHAR(14),
	cnpj VARCHAR(18),
	active BOOLEAN NOT NULL DEFAULT TRUE,
	is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clients (
	user_id INTEGER NOT NULL,
	client_type VARCHAR(20) NOT NULL,
	cep VARCHAR(9) NOT NULL,
	state CHAR(2) NOT NULL,
	city VARCHAR(120) NOT NULL,
	PRIMARY KEY (user_id),
	CONSTRAINT fk_clients_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE stores (
	id INTEGER PRIMARY KEY,
	name VARCHAR(120) NOT NULL,
	cnpj VARCHAR(18) NOT NULL UNIQUE,
	phone VARCHAR(20) NOT NULL,
	email VARCHAR(255) NOT NULL UNIQUE,
	active BOOLEAN NOT NULL DEFAULT TRUE,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	cep VARCHAR(9) NOT NULL,
	city VARCHAR(120) NOT NULL,
	state CHAR(2) NOT NULL,
	street VARCHAR(255) NOT NULL,
	neighborhood VARCHAR(120) NOT NULL,
	number VARCHAR(20) NOT NULL
);

CREATE TABLE employees (
	user_id INTEGER NOT NULL,
	employee_code VARCHAR(20) NOT NULL UNIQUE,
	job_title VARCHAR(80) NOT NULL,
	salary DECIMAL(10,2) NOT NULL,
	hired_at DATE NOT NULL,
	store_id INTEGER NOT NULL,
	PRIMARY KEY (user_id),
	CONSTRAINT fk_employees_store FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
	CONSTRAINT fk_employees_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TRIGGER tr_clients_bi_disjoint
BEFORE INSERT ON clients
FOR EACH ROW
BEGIN
	SELECT CASE
		WHEN (SELECT profile_type FROM users WHERE id = NEW.user_id) <> 'cliente' THEN
			RAISE(ABORT, 'User must have profile_type cliente to be inserted into clients')
		WHEN EXISTS (SELECT 1 FROM employees WHERE user_id = NEW.user_id) THEN
			RAISE(ABORT, 'User is already registered as employee')
	END;
END;

CREATE TRIGGER tr_clients_bu_disjoint
BEFORE UPDATE ON clients
FOR EACH ROW
BEGIN
	SELECT CASE
		WHEN (SELECT profile_type FROM users WHERE id = NEW.user_id) <> 'cliente' THEN
			RAISE(ABORT, 'User must have profile_type cliente to remain in clients')
		WHEN EXISTS (SELECT 1 FROM employees WHERE user_id = NEW.user_id) THEN
			RAISE(ABORT, 'User is already registered as employee')
	END;
END;

CREATE TRIGGER tr_employees_bi_disjoint
BEFORE INSERT ON employees
FOR EACH ROW
BEGIN
	SELECT CASE
		WHEN (SELECT profile_type FROM users WHERE id = NEW.user_id) <> 'funcionario' THEN
			RAISE(ABORT, 'User must have profile_type funcionario to be inserted into employees')
		WHEN EXISTS (SELECT 1 FROM clients WHERE user_id = NEW.user_id) THEN
			RAISE(ABORT, 'User is already registered as client')
	END;
END;

CREATE TRIGGER tr_employees_bu_disjoint
BEFORE UPDATE ON employees
FOR EACH ROW
BEGIN
	SELECT CASE
		WHEN (SELECT profile_type FROM users WHERE id = NEW.user_id) <> 'funcionario' THEN
			RAISE(ABORT, 'User must have profile_type funcionario to remain in employees')
		WHEN EXISTS (SELECT 1 FROM clients WHERE user_id = NEW.user_id) THEN
			RAISE(ABORT, 'User is already registered as client')
	END;
END;

CREATE TABLE appointments (
	id INTEGER PRIMARY KEY,
	final_value DECIMAL(10,2) NOT NULL,
	service_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	payment_method VARCHAR(20) NOT NULL,
	status VARCHAR(20) NOT NULL,
	online BOOLEAN NOT NULL DEFAULT FALSE,
	notes VARCHAR(500),
	store_id INTEGER NOT NULL,
	client_id INTEGER NOT NULL,
	employee_id INTEGER NOT NULL,
	pet_id INTEGER NOT NULL,
	CONSTRAINT fk_appointments_store FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
	CONSTRAINT fk_appointments_client FOREIGN KEY (client_id) REFERENCES clients(user_id),
	CONSTRAINT fk_appointments_employee FOREIGN KEY (employee_id) REFERENCES employees(user_id),
	CONSTRAINT fk_appointments_pet FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
);

CREATE TABLE services (
	id INTEGER PRIMARY KEY,
	name VARCHAR(120) NOT NULL,
	description VARCHAR(500),
	price DECIMAL(10,2) NOT NULL
);

CREATE TABLE appointment_services (
	appointment_id INTEGER NOT NULL,
	service_id INTEGER NOT NULL,
	charged_value DECIMAL(10,2) NOT NULL,
	ordered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	delivered_at TIMESTAMP,
	notes VARCHAR(500),
	PRIMARY KEY (appointment_id, service_id),
	CONSTRAINT fk_appointment_services_appointment FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
	CONSTRAINT fk_appointment_services_service FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

CREATE TABLE categories (
	id INTEGER PRIMARY KEY,
	name VARCHAR(80) NOT NULL UNIQUE,
	description VARCHAR(255)
);

CREATE TABLE pets (
	id INTEGER PRIMARY KEY,
	name VARCHAR(120) NOT NULL,
	breed VARCHAR(80) NOT NULL,
	sex VARCHAR(20) NOT NULL,
	size VARCHAR(20) NOT NULL,
	weight DECIMAL(6,2) NOT NULL,
	health_notes VARCHAR(500),
	category_id INTEGER NOT NULL,
	owner_id INTEGER NOT NULL,
	CONSTRAINT fk_pets_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
	CONSTRAINT fk_pets_owner FOREIGN KEY (owner_id) REFERENCES clients(user_id) ON DELETE CASCADE
);

CREATE TABLE tags (
	id INTEGER PRIMARY KEY,
	name VARCHAR(80) NOT NULL UNIQUE,
	description VARCHAR(255)
);

CREATE TABLE pet_tags (
	pet_id INTEGER NOT NULL,
	tag_id INTEGER NOT NULL,
	PRIMARY KEY (pet_id, tag_id),
	CONSTRAINT fk_pet_tags_pet FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
	CONSTRAINT fk_pet_tags_tag FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Keeps final_value synchronized with the sum of appointment item values.
CREATE TRIGGER tr_appointment_services_ai
AFTER INSERT ON appointment_services
BEGIN
	UPDATE appointments
	SET final_value = COALESCE((
		SELECT SUM(charged_value)
		FROM appointment_services
		WHERE appointment_id = NEW.appointment_id
	), 0)
	WHERE id = NEW.appointment_id;
END;

CREATE TRIGGER tr_appointment_services_au
AFTER UPDATE ON appointment_services
BEGIN
	UPDATE appointments
	SET final_value = COALESCE((
		SELECT SUM(charged_value)
		FROM appointment_services
		WHERE appointment_id = NEW.appointment_id
	), 0)
	WHERE id = NEW.appointment_id;

	UPDATE appointments
	SET final_value = COALESCE((
		SELECT SUM(charged_value)
		FROM appointment_services
		WHERE appointment_id = OLD.appointment_id
	), 0)
	WHERE id = OLD.appointment_id;
END;

CREATE TRIGGER tr_appointment_services_ad
AFTER DELETE ON appointment_services
BEGIN
	UPDATE appointments
	SET final_value = COALESCE((
		SELECT SUM(charged_value)
		FROM appointment_services
		WHERE appointment_id = OLD.appointment_id
	), 0)
	WHERE id = OLD.appointment_id;
END;


-- ==========================================
-- DADOS DE EXEMPLO (SEED)
-- Senhas: usuarios comuns = 'senha123'
--         admin (id=12)   = 'admin123'
-- ==========================================

INSERT INTO users (id, name, email, password_hash, phone, profile_type, cpf, cnpj, active, is_superuser, created_at) VALUES
	(1,  'Ana Paula',      'ana.paula@exemplo.com',      '$pbkdf2-sha256$29000$DcFY672XkvIeA.B8b60VYg$60msYdWp1w3tN.VnlcWXxwWz4X5DW4Eo6qFunbGBNHs', '11990001111', 'cliente',    '111.111.111-11', NULL, TRUE,  FALSE, '2026-01-10 09:00:00'),
	(2,  'Bruno Lima',     'bruno.lima@exemplo.com',     '$pbkdf2-sha256$29000$KgWgNCYEYMw55zwnpNQ6hw$ihzmeKRMQ3W8ibNvURIrGaLEebNKDa9iXjh9lZ4hvcM', '11990002222', 'cliente',    '222.222.222-22', NULL, TRUE,  FALSE, '2026-01-11 09:10:00'),
	(3,  'Carla Souza',    'carla.souza@exemplo.com',    '$pbkdf2-sha256$29000$xLhXKuX8nxOi1Ppf6z3nvA$TXreeCXbloslP9sBxKYZEnuBRCXWIpmTjQRklU3YkZc', '11990003333', 'cliente',    '333.333.333-33', NULL, TRUE,  FALSE, '2026-01-12 09:20:00'),
	(4,  'Diego Martins',  'diego.martins@exemplo.com',  '$pbkdf2-sha256$29000$yRlD6H2PsRbC2Ns75zzHGA$jUDkfQlFOBvMrNrWOsOr/Dg6Oy79H1g4t4Dz8V9LwvY', '11990004444', 'cliente',    '444.444.444-44', NULL, TRUE,  FALSE, '2026-01-13 09:30:00'),
	(5,  'Elisa Rocha',    'elisa.rocha@exemplo.com',    '$pbkdf2-sha256$29000$ei.FUOrde./9vxcihLAW4g$jXImZBDSCP15L/owqzhdxSkdK5Ad39gbDZdQoJDNxNs',  '11990005555', 'cliente',    '555.555.555-55', NULL, TRUE,  FALSE, '2026-01-14 09:40:00'),
	(6,  'Fabio Costa',    'fabio.costa@exemplo.com',    '$pbkdf2-sha256$29000$gvA.J2Tsfc95710rReidEw$nzfTaHhKMYQWGvmABORGCChGcuX.kMM1kxTE8eiFN5U', '11991111111', 'funcionario','666.666.666-66', NULL, TRUE,  FALSE, '2026-01-15 10:00:00'),
	(7,  'Gabriela Nunes', 'gabriela.nunes@exemplo.com', '$pbkdf2-sha256$29000$WYtxznlPaW1N6R2DsFYK4Q$hg5q/0ytfnegkvjex.pUkA/GlkKVLsqKTaJc80cKM3A',  '11992222222', 'funcionario','777.777.777-77', NULL, TRUE,  FALSE, '2026-01-16 10:10:00'),
	(8,  'Heitor Alves',   'heitor.alves@exemplo.com',   '$pbkdf2-sha256$29000$2FvrPcfYe89Zq1XK2TsH4A$jJQB/k3MPSjKF7gekteQHxr0fW9TB8KDXKk2XEHfbhw',  '11993333333', 'funcionario','888.888.888-88', NULL, TRUE,  FALSE, '2026-01-17 10:20:00'),
	(9,  'Isabela Melo',   'isabela.melo@exemplo.com',   '$pbkdf2-sha256$29000$KwUAwBgDgHCOcU4JQYhxzg$.vzlrUZlxZ.iErwS49L8x.15mbBcbIfBz3eUkxOEmhs',  '11994444444', 'funcionario','999.999.999-99', NULL, TRUE,  FALSE, '2026-01-18 10:30:00'),
	(10, 'Joao Pedro',     'joao.pedro@exemplo.com',     '$pbkdf2-sha256$29000$ByCEkLJ2DiEEgBCCcG5t7Q$umHQU9hhwabdzGUnvQzd3KJvSoMTf56nlytrz11Ijn8',  '11995555555', 'funcionario','000.000.000-00', NULL, TRUE,  FALSE, '2026-01-19 10:40:00'),
	(11, 'Marina Prado',   'marina.prado@exemplo.com',   '$pbkdf2-sha256$29000$5xwj5JwTonSO8T7H.D/HmA$Zq.zwsjv4ALiE1SdO2EBbS6GB7J6k7nwu20rnqDhiRo',  '11996666666', 'cliente',    '123.456.789-00', NULL, TRUE,  FALSE, '2026-01-20 11:00:00'),
	(12, 'Admin Apex',     'admin@exemplo.com',          '$pbkdf2-sha256$29000$oRSC8H5vjZGS0rpXijFGaA$oWnHGV6BaVHm0SeqqfyICrIhJdtlpZchgJ2ooelLK/0',  '11997777777', 'funcionario','012.012.012-01', NULL, TRUE,  TRUE,  '2026-01-21 11:30:00');

INSERT INTO clients (user_id, client_type, cep, state, city) VALUES
	(1,  'pessoa_fisica', '01001-000', 'SP', 'Sao Paulo'),
	(2,  'pessoa_fisica', '20040-020', 'RJ', 'Rio de Janeiro'),
	(3,  'pessoa_fisica', '30110-040', 'MG', 'Belo Horizonte'),
	(4,  'pessoa_fisica', '80010-000', 'PR', 'Curitiba'),
	(5,  'pessoa_fisica', '40020-000', 'BA', 'Salvador'),
	(11, 'pessoa_fisica', '70040-010', 'DF', 'Brasilia');

INSERT INTO stores (id, name, cnpj, phone, email, active, created_at, cep, city, state, street, neighborhood, number) VALUES
	(1, 'Petshop GC Paulista',  '10.000.000/0001-01', '1130001001', 'paulista@petshopgc.com',  TRUE, '2026-01-01 08:00:00', '01310-100', 'Sao Paulo',     'SP', 'Av Paulista',           'Bela Vista', '1000'),
	(2, 'Petshop GC Centro RJ', '10.000.000/0001-02', '2130002002', 'centrorj@petshopgc.com',  TRUE, '2026-01-01 08:10:00', '20031-170', 'Rio de Janeiro', 'RJ', 'Rua Primeiro de Marco', 'Centro',     '200'),
	(3, 'Petshop GC Savassi',   '10.000.000/0001-03', '3130003003', 'savassi@petshopgc.com',   TRUE, '2026-01-01 08:20:00', '30140-070', 'Belo Horizonte', 'MG', 'Rua Pernambuco',        'Savassi',    '300'),
	(4, 'Petshop GC Batel',     '10.000.000/0001-04', '4130004004', 'batel@petshopgc.com',     TRUE, '2026-01-01 08:30:00', '80420-090', 'Curitiba',       'PR', 'Av do Batel',           'Batel',      '400'),
	(5, 'Petshop GC Barra',     '10.000.000/0001-05', '7130005005', 'barra@petshopgc.com',     TRUE, '2026-01-01 08:40:00', '40140-110', 'Salvador',       'BA', 'Av Oceanica',           'Barra',      '500');

INSERT INTO employees (user_id, employee_code, job_title, salary, hired_at, store_id) VALUES
	(6,  'EMP-0001', 'banhista',     2200.00, '2026-01-20', 1),
	(7,  'EMP-0002', 'tosador',      2600.00, '2026-01-21', 2),
	(8,  'EMP-0003', 'veterinario',  5500.00, '2026-01-22', 3),
	(9,  'EMP-0004', 'recepcionista',2100.00, '2026-01-23', 4),
	(10, 'EMP-0005', 'adestrador',   3200.00, '2026-01-24', 5),
	(12, 'EMP-0006', 'gerente',      6800.00, '2026-01-25', 1);

INSERT INTO categories (id, name, description) VALUES
	(1, 'Canino',  'Pets do tipo cao'),
	(2, 'Felino',  'Pets do tipo gato'),
	(3, 'Ave',     'Aves domesticas'),
	(4, 'Coelho',  'Coelhos de companhia'),
	(5, 'Roedor',  'Roedores de pequeno porte');

-- sex usa os valores normalizados pelo service: 'M' (macho) ou 'F' (femea)
INSERT INTO pets (id, name, breed, sex, size, weight, health_notes, category_id, owner_id) VALUES
	(1, 'Thor',   'Labrador',          'M', 'grande',  28.50, 'Sem restricoes',               1, 1),
	(2, 'Luna',   'Siames',            'F', 'pequeno',  4.20, 'Alergia leve',                 2, 2),
	(3, 'Pipoca', 'Calopsita',         'F', 'pequeno',  0.09, 'Acompanha crescimento de bico', 3, 3),
	(4, 'Nino',   'Mini Lop',          'M', 'medio',    1.80, 'Sensivel a ruido',              4, 4),
	(5, 'Bolt',   'Porquinho-da-india','M', 'pequeno',  1.10, 'Dieta controlada',              5, 5),
	(6, 'Mel',    'Shih Tzu',          'F', 'pequeno',  6.40, 'Precisa de tosa mensal',        1, 1),
	(7, 'Zeus',   'Golden Retriever',  'M', 'grande',  31.20, 'Historico de dermatite',        1, 1),
	(8, 'Mia',    'Persa',             'F', 'medio',    4.80, 'Exige escovacao diaria',        2, 11);

INSERT INTO tags (id, name, description) VALUES
	(1, 'idoso',               'Pet com idade avancada'),
	(2, 'alergico',            'Pet com historico de alergia'),
	(3, 'agressivo',           'Pet com comportamento reativo'),
	(4, 'precisa_sedacao',     'Pet pode demandar sedacao em procedimentos'),
	(5, 'primeiro_atendimento','Primeiro atendimento do pet na rede'),
	(6, 'retorno',             'Pet em atendimento de retorno');

INSERT INTO pet_tags (pet_id, tag_id) VALUES
	(1, 1), (1, 6),
	(2, 2),
	(3, 5),
	(4, 4),
	(5, 3),
	(6, 5),
	(7, 2),
	(8, 6);

INSERT INTO services (id, name, description, price) VALUES
	(1, 'Banho',                'Banho completo com secagem',              80.00),
	(2, 'Tosa',                 'Tosa higienica e estetica',               95.00),
	(3, 'Consulta Veterinaria', 'Consulta clinica geral',                 180.00),
	(4, 'Vacinacao',            'Aplicacao de vacina conforme protocolo', 140.00),
	(5, 'Adestramento Basico',  'Sessao inicial de comandos basicos',     220.00),
	(6, 'Hidratacao de Pelagem','Tratamento hidratante para pele e pelo',  60.00),
	(7, 'Corte de Unhas',       'Corte e acabamento de unhas',             35.00);

-- payment_method e status usam os valores NORMALIZADOS pelo service (exatamente como o service armazena)
-- payment_method: 'pix' | 'cartão de crédito' | 'cartão de débito' | 'dinheiro' | 'transferência bancária'
-- status:         'agendado' | 'em andamento' | 'concluído' | 'cancelado'
-- final_value sera recalculado pelos triggers apos o INSERT em appointment_services
INSERT INTO appointments (id, final_value, service_at, payment_method, status, online, notes, store_id, client_id, employee_id, pet_id) VALUES
	(1, 0.00, '2026-02-01 10:00:00', 'pix',               'concluído', FALSE, 'Atendimento tranquilo',               1, 1,  6, 1),
	(2, 0.00, '2026-02-02 11:00:00', 'cartão de crédito', 'concluído', FALSE, 'Tosa com tesoura',                    2, 2,  7, 2),
	(3, 0.00, '2026-02-03 15:30:00', 'cartão de débito',  'concluído', TRUE,  'Consulta por teleorientacao',         3, 3,  8, 3),
	(4, 0.00, '2026-02-04 09:15:00', 'dinheiro',          'concluído', FALSE, 'Vacinacao anual',                     4, 4,  9, 4),
	(5, 0.00, '2026-02-05 16:45:00', 'pix',               'agendado',  FALSE, 'Primeira sessao de adestramento',     5, 5, 10, 5),
	(6, 0.00, '2026-02-06 10:30:00', 'pix',               'concluído', FALSE, 'Pacote banho + hidratacao',           1, 1,  6, 6),
	(7, 0.00, '2026-02-06 14:00:00', 'cartão de crédito', 'concluído', FALSE, 'Pacote completo de higiene',          1, 1, 12, 7),
	(8, 0.00, '2026-02-07 09:00:00', 'cartão de débito',  'agendado',  FALSE, 'Retorno com vacina e corte de unhas', 1, 11, 12, 8);

INSERT INTO appointment_services (appointment_id, service_id, charged_value, notes) VALUES
	(1, 1,  80.00, 'Banho completo realizado'),
	(2, 2,  95.00, 'Tosa finalizada com sucesso'),
	(3, 3, 180.00, 'Consulta clinica registrada'),
	(4, 4, 140.00, 'Vacina aplicada sem intercorrencias'),
	(5, 5, 220.00, 'Sessao inicial concluida'),
	(6, 1,  80.00, 'Banho de manutencao'),
	(6, 6,  60.00, 'Hidratacao de pelagem concluida'),
	(7, 1,  80.00, 'Banho premium'),
	(7, 2,  95.00, 'Tosa estetica'),
	(7, 7,  35.00, 'Corte de unhas'),
	(8, 4, 140.00, 'Dose de reforco aplicada'),
	(8, 7,  35.00, 'Unhas aparadas');


-- ==========================================
-- DADOS ADICIONAIS — SEED EXPANDIDO
-- Senha de todos os novos usuarios: 'senha123'
-- ==========================================

-- Novas lojas (ids 6-9)
INSERT INTO stores (id, name, cnpj, phone, email, active, created_at, cep, city, state, street, neighborhood, number) VALUES
	(6, 'Petshop GC Copacabana', '10.000.000/0001-06', '2130006006', 'copacabana@petshopgc.com', TRUE, '2026-01-02 08:00:00', '22010-000', 'Rio de Janeiro', 'RJ', 'Av Atlantica',    'Copacabana', '600'),
	(7, 'Petshop GC Lourdes',    '10.000.000/0001-07', '3130007007', 'lourdes@petshopgc.com',    TRUE, '2026-01-02 08:10:00', '30170-070', 'Belo Horizonte', 'MG', 'Av do Contorno',  'Lourdes',    '700'),
	(8, 'Petshop GC Boa Viagem', '10.000.000/0001-08', '8130008008', 'boaviagem@petshopgc.com',  TRUE, '2026-01-02 08:20:00', '51011-000', 'Recife',         'PE', 'Av Boa Viagem',   'Boa Viagem', '800'),
	(9, 'Petshop GC Moema',      '10.000.000/0001-09', '1130009009', 'moema@petshopgc.com',      TRUE, '2026-01-02 08:30:00', '04077-020', 'Sao Paulo',      'SP', 'Av Ibirapuera',   'Moema',      '900');

-- Novos usuarios clientes (ids 13-25)
INSERT INTO users (id, name, email, password_hash, phone, profile_type, cpf, cnpj, active, is_superuser, created_at) VALUES
	(13, 'Renata Oliveira',  'renata.oliveira@exemplo.com',  '$pbkdf2-sha256$29000$DcFY672XkvIeA.B8b60VYg$60msYdWp1w3tN.VnlcWXxwWz4X5DW4Eo6qFunbGBNHs', '11990013333', 'cliente',    '013.013.013-13', NULL, TRUE, FALSE, '2026-01-22 09:00:00'),
	(14, 'Samuel Dias',      'samuel.dias@exemplo.com',      '$pbkdf2-sha256$29000$KgWgNCYEYMw55zwnpNQ6hw$ihzmeKRMQ3W8ibNvURIrGaLEebNKDa9iXjh9lZ4hvcM', '21990014444', 'cliente',    '014.014.014-14', NULL, TRUE, FALSE, '2026-01-22 09:10:00'),
	(15, 'Tatiana Ferreira', 'tatiana.ferreira@exemplo.com', '$pbkdf2-sha256$29000$xLhXKuX8nxOi1Ppf6z3nvA$TXreeCXbloslP9sBxKYZEnuBRCXWIpmTjQRklU3YkZc', '31990015555', 'cliente',    '015.015.015-15', NULL, TRUE, FALSE, '2026-01-22 09:20:00'),
	(16, 'Ubirajara Silva',  'ubi.silva@exemplo.com',        '$pbkdf2-sha256$29000$yRlD6H2PsRbC2Ns75zzHGA$jUDkfQlFOBvMrNrWOsOr/Dg6Oy79H1g4t4Dz8V9LwvY', '41990016666', 'cliente',    '016.016.016-16', NULL, TRUE, FALSE, '2026-01-22 09:30:00'),
	(17, 'Vanessa Costa',    'vanessa.costa@exemplo.com',    '$pbkdf2-sha256$29000$ei.FUOrde./9vxcihLAW4g$jXImZBDSCP15L/owqzhdxSkdK5Ad39gbDZdQoJDNxNs',  '71990017777', 'cliente',    '017.017.017-17', NULL, TRUE, FALSE, '2026-01-22 09:40:00'),
	(18, 'Wagner Barbosa',   'wagner.barbosa@exemplo.com',   '$pbkdf2-sha256$29000$gvA.J2Tsfc95710rReidEw$nzfTaHhKMYQWGvmABORGCChGcuX.kMM1kxTE8eiFN5U', '19990018888', 'cliente',    '018.018.018-18', NULL, TRUE, FALSE, '2026-01-22 09:50:00'),
	(19, 'Ximena Torres',    'ximena.torres@exemplo.com',    '$pbkdf2-sha256$29000$WYtxznlPaW1N6R2DsFYK4Q$hg5q/0ytfnegkvjex.pUkA/GlkKVLsqKTaJc80cKM3A',  '51990019999', 'cliente',    '019.019.019-19', NULL, TRUE, FALSE, '2026-01-23 09:00:00'),
	(20, 'Yara Andrade',     'yara.andrade@exemplo.com',     '$pbkdf2-sha256$29000$2FvrPcfYe89Zq1XK2TsH4A$jJQB/k3MPSjKF7gekteQHxr0fW9TB8KDXKk2XEHfbhw',  '85990020000', 'cliente',    '020.020.020-20', NULL, TRUE, FALSE, '2026-01-23 09:10:00'),
	(21, 'Zeca Rodrigues',   'zeca.rodrigues@exemplo.com',   '$pbkdf2-sha256$29000$KwUAwBgDgHCOcU4JQYhxzg$.vzlrUZlxZ.iErwS49L8x.15mbBcbIfBz3eUkxOEmhs',  '48990021111', 'cliente',    '021.021.021-21', NULL, TRUE, FALSE, '2026-01-23 09:20:00'),
	(22, 'Amanda Lima',      'amanda.lima@exemplo.com',      '$pbkdf2-sha256$29000$ByCEkLJ2DiEEgBCCcG5t7Q$umHQU9hhwabdzGUnvQzd3KJvSoMTf56nlytrz11Ijn8',  '62990022222', 'cliente',    '022.022.022-22', NULL, TRUE, FALSE, '2026-01-23 09:30:00'),
	(23, 'Bernardo Farias',  'bernardo.farias@exemplo.com',  '$pbkdf2-sha256$29000$5xwj5JwTonSO8T7H.D/HmA$Zq.zwsjv4ALiE1SdO2EBbS6GB7J6k7nwu20rnqDhiRo',  '11990023333', 'cliente',    '023.023.023-23', NULL, TRUE, FALSE, '2026-01-24 09:00:00'),
	(24, 'Camila Esteves',   'camila.esteves@exemplo.com',   '$pbkdf2-sha256$29000$DcFY672XkvIeA.B8b60VYg$60msYdWp1w3tN.VnlcWXxwWz4X5DW4Eo6qFunbGBNHs', '21990024444', 'cliente',    '024.024.024-24', NULL, TRUE, FALSE, '2026-01-24 09:10:00'),
	(25, 'Danilo Queiroz',   'danilo.queiroz@exemplo.com',   '$pbkdf2-sha256$29000$KgWgNCYEYMw55zwnpNQ6hw$ihzmeKRMQ3W8ibNvURIrGaLEebNKDa9iXjh9lZ4hvcM', '31990025555', 'cliente',    '025.025.025-25', NULL, TRUE, FALSE, '2026-01-24 09:20:00');

-- Novos usuarios funcionarios (ids 26-35)
INSERT INTO users (id, name, email, password_hash, phone, profile_type, cpf, cnpj, active, is_superuser, created_at) VALUES
	(26, 'Pedro Santos',     'pedro.santos@exemplo.com',     '$pbkdf2-sha256$29000$xLhXKuX8nxOi1Ppf6z3nvA$TXreeCXbloslP9sBxKYZEnuBRCXWIpmTjQRklU3YkZc', '11991260001', 'funcionario','026.026.026-26', NULL, TRUE, FALSE, '2026-01-25 10:00:00'),
	(27, 'Larissa Mendes',   'larissa.mendes@exemplo.com',   '$pbkdf2-sha256$29000$yRlD6H2PsRbC2Ns75zzHGA$jUDkfQlFOBvMrNrWOsOr/Dg6Oy79H1g4t4Dz8V9LwvY', '11991270002', 'funcionario','027.027.027-27', NULL, TRUE, FALSE, '2026-01-25 10:10:00'),
	(28, 'Ricardo Gomes',    'ricardo.gomes@exemplo.com',    '$pbkdf2-sha256$29000$ei.FUOrde./9vxcihLAW4g$jXImZBDSCP15L/owqzhdxSkdK5Ad39gbDZdQoJDNxNs',  '11991280003', 'funcionario','028.028.028-28', NULL, TRUE, FALSE, '2026-01-25 10:20:00'),
	(29, 'Claudia Pereira',  'claudia.pereira@exemplo.com',  '$pbkdf2-sha256$29000$gvA.J2Tsfc95710rReidEw$nzfTaHhKMYQWGvmABORGCChGcuX.kMM1kxTE8eiFN5U', '11991290004', 'funcionario','029.029.029-29', NULL, TRUE, FALSE, '2026-01-25 10:30:00'),
	(30, 'Fernando Lima',    'fernando.lima@exemplo.com',    '$pbkdf2-sha256$29000$WYtxznlPaW1N6R2DsFYK4Q$hg5q/0ytfnegkvjex.pUkA/GlkKVLsqKTaJc80cKM3A',  '11991300005', 'funcionario','030.030.030-30', NULL, TRUE, FALSE, '2026-01-26 10:00:00'),
	(31, 'Patricia Souza',   'patricia.souza@exemplo.com',   '$pbkdf2-sha256$29000$2FvrPcfYe89Zq1XK2TsH4A$jJQB/k3MPSjKF7gekteQHxr0fW9TB8KDXKk2XEHfbhw',  '11991310006', 'funcionario','031.031.031-31', NULL, TRUE, FALSE, '2026-01-26 10:10:00'),
	(32, 'Eduardo Carvalho', 'eduardo.carvalho@exemplo.com', '$pbkdf2-sha256$29000$KwUAwBgDgHCOcU4JQYhxzg$.vzlrUZlxZ.iErwS49L8x.15mbBcbIfBz3eUkxOEmhs',  '11991320007', 'funcionario','032.032.032-32', NULL, TRUE, FALSE, '2026-01-26 10:20:00'),
	(33, 'Simone Martins',   'simone.martins@exemplo.com',   '$pbkdf2-sha256$29000$ByCEkLJ2DiEEgBCCcG5t7Q$umHQU9hhwabdzGUnvQzd3KJvSoMTf56nlytrz11Ijn8',  '11991330008', 'funcionario','033.033.033-33', NULL, TRUE, FALSE, '2026-01-26 10:30:00'),
	(34, 'Rodrigo Freitas',  'rodrigo.freitas@exemplo.com',  '$pbkdf2-sha256$29000$5xwj5JwTonSO8T7H.D/HmA$Zq.zwsjv4ALiE1SdO2EBbS6GB7J6k7nwu20rnqDhiRo',  '11991340009', 'funcionario','034.034.034-34', NULL, TRUE, FALSE, '2026-01-27 10:00:00'),
	(35, 'Nathalia Campos',  'nathalia.campos@exemplo.com',  '$pbkdf2-sha256$29000$DcFY672XkvIeA.B8b60VYg$60msYdWp1w3tN.VnlcWXxwWz4X5DW4Eo6qFunbGBNHs', '11991350010', 'funcionario','035.035.035-35', NULL, TRUE, FALSE, '2026-01-27 10:10:00');

-- Novos clientes
INSERT INTO clients (user_id, client_type, cep, state, city) VALUES
	(13, 'pessoa_fisica', '01310-100', 'SP', 'Sao Paulo'),
	(14, 'pessoa_fisica', '22010-000', 'RJ', 'Rio de Janeiro'),
	(15, 'pessoa_fisica', '30140-070', 'MG', 'Belo Horizonte'),
	(16, 'pessoa_fisica', '80420-090', 'PR', 'Curitiba'),
	(17, 'pessoa_fisica', '40140-110', 'BA', 'Salvador'),
	(18, 'pessoa_fisica', '13010-010', 'SP', 'Campinas'),
	(19, 'pessoa_fisica', '90010-180', 'RS', 'Porto Alegre'),
	(20, 'pessoa_fisica', '60175-047', 'CE', 'Fortaleza'),
	(21, 'pessoa_fisica', '88010-400', 'SC', 'Florianopolis'),
	(22, 'pessoa_fisica', '74010-010', 'GO', 'Goiania'),
	(23, 'pessoa_fisica', '01415-001', 'SP', 'Sao Paulo'),
	(24, 'pessoa_fisica', '20071-004', 'RJ', 'Rio de Janeiro'),
	(25, 'pessoa_fisica', '30150-370', 'MG', 'Belo Horizonte');

-- Novos funcionarios
INSERT INTO employees (user_id, employee_code, job_title, salary, hired_at, store_id) VALUES
	(26, 'EMP-0007', 'banhista',      2300.00, '2026-01-28', 2),
	(27, 'EMP-0008', 'tosadora',      2700.00, '2026-01-28', 3),
	(28, 'EMP-0009', 'veterinario',   5800.00, '2026-01-29', 6),
	(29, 'EMP-0010', 'recepcionista', 2200.00, '2026-01-29', 6),
	(30, 'EMP-0011', 'adestrador',    3400.00, '2026-01-30', 7),
	(31, 'EMP-0012', 'banhista',      2400.00, '2026-01-30', 7),
	(32, 'EMP-0013', 'veterinario',   5600.00, '2026-01-31', 8),
	(33, 'EMP-0014', 'gerente',       7000.00, '2026-01-31', 8),
	(34, 'EMP-0015', 'tosador',       2800.00, '2026-02-01', 9),
	(35, 'EMP-0016', 'banhista',      2200.00, '2026-02-01', 9);

-- Novos pets (ids 9-30)
-- category_id: 1=Canino | 2=Felino | 3=Ave | 4=Coelho | 5=Roedor
INSERT INTO pets (id, name, breed, sex, size, weight, health_notes, category_id, owner_id) VALUES
	(9,  'Rex',        'Pastor Alemao',          'M', 'grande',  35.00, 'Sem restricoes',                      1, 13),
	(10, 'Nala',       'Ragdoll',                'F', 'medio',    5.20, 'Alergia alimentar ao trigo',           2, 14),
	(11, 'Florentina', 'Calopsita',              'F', 'pequeno',  0.08, 'Crescimento de bico monitorado',       3, 15),
	(12, 'Docinho',    'Angora',                 'M', 'medio',    2.10, 'Escovacao semanal necessaria',         4, 16),
	(13, 'Chispinha',  'Hamster Anao',           'F', 'pequeno',  0.15, 'Necessita roda giratoria',             5, 17),
	(14, 'Max',        'Bulldog Frances',        'M', 'pequeno', 12.00, 'Problema respiratorio leve',           1, 18),
	(15, 'Cleopatra',  'Siames',                 'F', 'pequeno',  3.90, 'Rins sensiveis - dieta especial',      2, 19),
	(16, 'Piu',        'Periquito Australiano',  'M', 'pequeno',  0.05, 'Sem restricoes',                       3, 20),
	(17, 'Bolinha',    'Lop Holandes',           'M', 'pequeno',  1.50, 'Dieta rica em feno',                   4, 21),
	(18, 'Pinky',      'Porquinho-da-india',     'F', 'pequeno',  0.95, 'Animal muito sociavel',                5, 22),
	(19, 'Duke',       'Rottweiler',             'M', 'grande',  42.00, 'Adestrado e sociavel',                 1, 13),
	(20, 'Lala',       'Maine Coon',             'F', 'grande',   7.50, 'Pelo longo requer grooming frequente', 2, 14),
	(21, 'Whisky',     'Poodle Toy',             'M', 'pequeno',  3.20, 'Tosa mensal recomendada',              1, 3),
	(22, 'Belinha',    'Pinscher',               'F', 'pequeno',  2.80, 'Sem restricoes',                       1, 4),
	(23, 'Pompom',     'Persa',                  'F', 'medio',    4.10, 'Pelo comprido requer cuidado diario',  2, 5),
	(24, 'Tobias',     'Beagle',                 'M', 'medio',   15.00, 'Muito curioso e hiperativo',            1, 11),
	(25, 'Fifi',       'Yorkshire Terrier',      'F', 'pequeno',  2.50, 'Tosa quinzenal recomendada',           1, 18),
	(26, 'Simba',      'Shiba Inu',              'M', 'medio',   10.50, 'Muito ativo e independente',           1, 23),
	(27, 'Frida',      'Scottish Fold',          'F', 'medio',    4.30, 'Articulacao monitorada regularmente',  2, 24),
	(28, 'Gordo',      'Lhasa Apso',             'M', 'pequeno',  7.20, 'Tosa higienica mensal',                1, 25),
	(29, 'Toto',       'Border Collie',          'M', 'grande',  20.00, 'Alta energia - precisa de atividade',  1, 1),
	(30, 'Nina',       'Gato Angora',            'F', 'medio',    3.60, 'Pelo requer cuidado diario',           2, 2);

-- Tags para os novos pets
INSERT INTO pet_tags (pet_id, tag_id) VALUES
	(9,  5), (9,  3),
	(10, 2),
	(11, 5),
	(12, 4),
	(13, 3),
	(14, 2), (14, 4),
	(15, 1), (15, 2),
	(16, 5),
	(17, 4),
	(18, 5),
	(19, 3),
	(20, 1), (20, 6),
	(21, 5),
	(22, 5),
	(23, 1),
	(24, 3),
	(25, 6),
	(26, 5),
	(27, 1), (27, 4),
	(28, 6),
	(29, 3),
	(30, 2);

-- Novos atendimentos (ids 9-35)
-- final_value sera recalculado pelos triggers apos INSERT em appointment_services
INSERT INTO appointments (id, final_value, service_at, payment_method, status, online, notes, store_id, client_id, employee_id, pet_id) VALUES
	(9,  0.00, '2026-02-10 10:00:00', 'pix',                  'concluído',    FALSE, 'Primeiro atendimento, pet tranquilo',        1, 13,  6, 9),
	(10, 0.00, '2026-02-11 11:00:00', 'cartão de crédito',    'concluído',    FALSE, 'Tosa estetica finalizada',                   2, 14,  7, 10),
	(11, 0.00, '2026-02-12 09:30:00', 'dinheiro',             'concluído',    FALSE, 'Consulta de rotina',                         3, 15,  8, 11),
	(12, 0.00, '2026-02-13 14:00:00', 'pix',                  'concluído',    FALSE, 'Higiene rapida',                             4, 16,  9, 12),
	(13, 0.00, '2026-02-14 16:00:00', 'cartão de débito',     'concluído',    FALSE, 'Sessao de sociabilizacao incluida',          5, 17, 10, 13),
	(14, 0.00, '2026-02-15 10:00:00', 'transferência bancária','concluído',   FALSE, 'Pacote banho e tosa completo',               1, 18,  6, 14),
	(15, 0.00, '2026-02-16 11:30:00', 'pix',                  'em andamento', FALSE, 'Em progresso',                               2, 19, 26, 15),
	(16, 0.00, '2026-02-17 09:00:00', 'cartão de crédito',    'concluído',    TRUE,  'Teleorientacao veterinaria',                 3, 20,  8, 16),
	(17, 0.00, '2026-02-18 10:30:00', 'pix',                  'concluído',    FALSE, 'Vacinacao anual em dia',                     6, 21, 28, 17),
	(18, 0.00, '2026-02-19 14:30:00', 'dinheiro',             'concluído',    FALSE, 'Primeira sessao - progresso otimo',          7, 22, 30, 18),
	(19, 0.00, '2026-02-20 09:00:00', 'cartão de débito',     'concluído',    FALSE, 'Check-up completo com vacinacao',            8, 23, 32, 26),
	(20, 0.00, '2026-02-21 11:00:00', 'pix',                  'concluído',    FALSE, 'Tosa estetica e hidratacao',                 9, 24, 34, 27),
	(21, 0.00, '2026-02-22 10:00:00', 'cartão de crédito',    'concluído',    FALSE, 'Higiene completa com corte de unhas',        1, 25, 12, 28),
	(22, 0.00, '2026-02-23 15:00:00', 'pix',                  'agendado',     FALSE, 'Sessao de adestramento avancado',            2, 13, 26, 19),
	(23, 0.00, '2026-02-24 09:30:00', 'dinheiro',             'concluído',    FALSE, 'Banho e escovacao de pelo longo',            3, 14, 27, 20),
	(24, 0.00, '2026-02-25 10:00:00', 'cartão de débito',     'concluído',    FALSE, 'Consulta de rotina - Border saudavel',       6,  1, 28, 29),
	(25, 0.00, '2026-02-26 11:00:00', 'pix',                  'concluído',    FALSE, 'Tratamento hidratante realizado',             7,  2, 31, 30),
	(26, 0.00, '2026-02-27 14:00:00', 'cartão de crédito',    'agendado',     FALSE, 'Tosa estetica agendada',                     8,  3, 33, 21),
	(27, 0.00, '2026-02-28 09:00:00', 'transferência bancária','concluído',   FALSE, 'Banho simples realizado',                    9,  4, 35, 22),
	(28, 0.00, '2026-03-01 10:30:00', 'pix',                  'concluído',    FALSE, 'Check-up com protocolo de vacinas',          1,  5,  6, 23),
	(29, 0.00, '2026-03-02 11:00:00', 'cartão de débito',     'em andamento', FALSE, 'Corte de unhas em andamento',               4, 11,  9, 24),
	(30, 0.00, '2026-03-03 09:00:00', 'dinheiro',             'concluído',    FALSE, 'Adestramento basico - excelente resposta',   5, 15, 10, 11),
	(31, 0.00, '2026-03-04 14:30:00', 'pix',                  'cancelado',    FALSE, 'Cliente remarcou para outra data',           2, 16,  7, 12),
	(32, 0.00, '2026-03-05 10:00:00', 'cartão de crédito',    'concluído',    FALSE, 'Consulta e prescricao realizadas',           6, 17, 28, 13),
	(33, 0.00, '2026-03-06 11:00:00', 'pix',                  'agendado',     FALSE, 'Tosa quinzenal agendada',                    9, 18, 34, 25),
	(34, 0.00, '2026-03-07 09:30:00', 'cartão de débito',     'concluído',    FALSE, 'Adestramento - comandos basicos dominados',  7, 19, 30, 15),
	(35, 0.00, '2026-03-08 10:00:00', 'transferência bancária','concluído',   FALSE, 'Vacinacao e higiene completa',               3, 20,  8, 16);

-- Servicos dos novos atendimentos
INSERT INTO appointment_services (appointment_id, service_id, charged_value, notes) VALUES
	(9,  1,  80.00, 'Banho completo realizado com sucesso'),
	(10, 2,  95.00, 'Tosa estetica finalizada'),
	(11, 3, 180.00, 'Consulta clinica de rotina'),
	(12, 7,  35.00, 'Corte de unhas realizado'),
	(13, 5, 220.00, 'Adestramento com sociabilizacao incluida'),
	(14, 1,  80.00, 'Banho premium'),
	(14, 2,  95.00, 'Tosa estetica inclusa no pacote'),
	(15, 1,  80.00, 'Banho em andamento'),
	(16, 3, 180.00, 'Consulta via teleorientacao'),
	(17, 4, 140.00, 'Vacinacao anual aplicada'),
	(18, 5, 220.00, 'Adestramento - primeira sessao'),
	(19, 3, 180.00, 'Check-up completo'),
	(19, 4, 140.00, 'Vacinacao incluida no check-up'),
	(20, 2,  95.00, 'Tosa estetica realizada'),
	(20, 6,  60.00, 'Hidratacao de pelagem inclusa'),
	(21, 1,  80.00, 'Banho completo'),
	(21, 7,  35.00, 'Corte de unhas'),
	(22, 5, 220.00, 'Adestramento avancado agendado'),
	(23, 1,  80.00, 'Banho com escovacao de pelo longo'),
	(24, 3, 180.00, 'Consulta veterinaria de rotina'),
	(25, 1,  80.00, 'Banho com produtos hidratantes'),
	(25, 6,  60.00, 'Hidratacao profunda de pelagem'),
	(26, 2,  95.00, 'Tosa agendada'),
	(27, 1,  80.00, 'Banho simples'),
	(28, 3, 180.00, 'Consulta geral'),
	(28, 4, 140.00, 'Protocolo de vacinas atualizado'),
	(29, 7,  35.00, 'Corte de unhas em andamento'),
	(30, 5, 220.00, 'Sessao de adestramento basico'),
	(31, 2,  95.00, 'Tosa cancelada pelo cliente'),
	(32, 3, 180.00, 'Consulta e prescricao'),
	(33, 2,  95.00, 'Tosa quinzenal agendada'),
	(34, 5, 220.00, 'Adestramento - comandos basicos'),
	(35, 4, 140.00, 'Vacinacao anual'),
	(35, 7,  35.00, 'Corte de unhas incluido');
