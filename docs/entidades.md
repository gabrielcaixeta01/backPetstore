## Entidades principais

- Usuario
- Pet
- Categoria
- Tag
- Loja
- Servico ou Atendimento

### Usuario

Representa qualquer pessoa com acesso ao sistema, seja cliente ou funcionario.

Tipos de perfil aceitos no sistema:

- cliente
- funcionario
- admin_loja
- super_admin

- id
- nome
- email
- senha_hash
- telefone
- tipo_perfil
- data_cadastro
- ativo

#### Cliente

Extensao de Usuario para quem contrata os servicos.
No modelo fisico, a especializacao de Usuario em Cliente e Funcionario e disjunta: um usuario pertence a apenas um desses subtipos.

- cpf ou cnpj
- data_nascimento ou data_abertura, conforme o tipo de cliente
- endereco

#### Funcionario

Extensao de Usuario para quem realiza os atendimentos.

- cpf
- cargo (job_title)
- data_inicio (hired_at, do tipo Date, nao DateTime)
- salario (Decimal com 2 casas, obrigatorio)
- loja_id (obrigatorio, nao pode ser nulo)

#### Admin de Loja

Extensao de Usuario para perfil administrativo de uma unidade especifica.

- cpf
- cargo = admin_loja
- data_inicio
- loja_id (obrigatorio)

#### Super Admin

Extensao de Usuario para perfil administrativo de rede.

- cpf
- cargo = super_admin
- data_inicio
- escopo = rede
- criado_via_bootstrap (indica se foi usuario inicial criado direto no banco)

### Pet

Representa o animal cadastrado no sistema.

- id
- nome (2-120 caracteres, obrigatorio)
- especie (nao implementado no modelo atual)
- raca (breed, max 80 caracteres, obrigatorio)
- sexo (aceita: M, F, macho, femea, fêmea; normalizados; obrigatorio)
- data_nascimento (nao implementado no modelo atual)
- porte (size, obrigatorio)
- peso (weight, Decimal com 2 casas, >= 0, obrigatorio)
- observacoes_saude (health_notes, max 500 caracteres, opcional)
- categoria_id (obrigatorio)
- owner_id (id do usuario proprietario, obrigatorio)
- tags (lista de tags associadas, opcional)
- ativo (default true)

O pet deve mostrar apenas o dono atual no cadastro.

### Categoria

Classifica o pet por tipo ou grupo de atendimento.

- id
- nome
- descricao

### Tag

Usada para marcar caracteristicas importantes do pet.

- id
- nome
- descricao

Exemplos:

- idoso
- agressivo
- alergico
- precisa_sedacao
- primeiro_atendimento

Por enquanto, as tags servem apenas como informacao complementar e nao alteram regras de negocio.

### Loja

Representa uma unidade fisica da franquia.

- id
- nome
- cnpj
- telefone
- email
- cep
- endereco
- cidade
- estado
- ativo

### Servico / Atendimento

Representa um tipo de servico oferecido pela loja.

- id
- nome (2-80 caracteres, obrigatorio)
- descricao (max 500 caracteres, opcional)
- preco (Decimal com 2 casas, obrigatorio)

### Atendimento

Representa o registro de um atendimento realizado na loja.

- id
- data_hora (service_at, datetime, opcional; default null)
- status (aceita: agendado, em_andamento, concluido, cancelado; normalizados via aliases; obrigatorio)
- forma_pagamento (payment_method, aceita 8 variantes: dinheiro, cash, pix, cartao_credito, credit_card, cartao_debito, debit_card, boleto; normalizados para 4 valores canonicos; obrigatorio)
- observacoes (notes, max 500 caracteres, opcional)
- online (boolean, default false)
- servicos (lista de servicos prestados, obrigatorio; minimo 1 servico)
- loja_id (obrigatorio)
- pet_id (obrigatorio; pet deve pertencer ao cliente)
- cliente_id (obrigatorio)
- funcionario_id (employee_id, id do usuario com perfil funcionario, obrigatorio)

O atendimento nao tera etapas internas; apenas o status do processo sera acompanhado.
Um atendimento deve conter pelo menos um servico prestado, enquanto um servico pode aparecer em nenhum ou varios atendimentos.
Quando um atendimento eh criado, o sistema automaticamente registra os servicos com seus precos atuais em uma tabela de juncao.