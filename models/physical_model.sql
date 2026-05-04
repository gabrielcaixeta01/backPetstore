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
