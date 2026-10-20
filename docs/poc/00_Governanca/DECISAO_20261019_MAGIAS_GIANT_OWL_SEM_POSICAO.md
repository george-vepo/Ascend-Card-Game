# Decisão normativa: magias da Giant Owl sem posicionamento — issue #30

**Delegação expressa do administrador, 19/10/2026:** árbitro/engenharia autorizado a escolher, registrar e implementar a solução mais coerente sem nova consulta. **Status:** decisão aprovada; ver PR de implementação e CI para distinguir regra de código integrado.

## Fontes e classificação

- **SRD 5.2.1**, Giant Owl p. 352, Spellcasting sem componentes, usando Wisdom: *Detect Evil and Good* e *Detect Magic* à vontade, *Clairvoyance* 1/dia.
- Descrições integrais: *Detect Evil and Good* e *Detect Magic* p. 123, *Clairvoyance* p. 115; concentração e dano: glossário p. 179.
- Fonte externa verificável de criatura e identidade: Catálogo SRD pinado pelo `config/catalogo_srd.json`. Não copiar conjuntos de dados nem alterar fichas/ordem dos montes.
- **HOMEbrew aprovada aqui:** substituição do domínio físico de 30 pés pela **totalidade do campo público e nada além dele**, já que o Card Game não tem arena, posição, alcance ou bloqueios geométricos. Não atribuir essa tradução ao SRD. Não remover economia de ações, salvaguardas, concentração ou privacidade.

## 1. Detect Evil and Good

**Ação:** Spellcasting, **uma Action** da Giant Owl em seu turno (sem componentes). **Alcance traduzido:** apenas as criaturas **ativas e públicas** nos dois campos. **Efeito:** lista uma vez as criaturas já públicas de tipos SRD *Aberration, Celestial, Elemental, Fey, Fiend, Undead*; nesta fixture, Roper (Aberration) e a própria Owl (Celestial). Não declara espécie/ND/identidades ocultas em mão/monte, não vê através de paredes fictícias e não infere posição. Detectar *Hallow* só é possível quando seu efeito público estiver oficialmente registrado e verificado; enquanto inexistente na fixture, retornar **desconhecido/não homologado**, não `false` categórico.

**Concentração:** até 10 minutos, representados por até 100 rodadas de 6 segundos. Consulta pública do efeito corrente é gratuita e não constitui conjuração ou Action.

## 2. Detect Magic

**Ação:** Spellcasting, **uma Action** em seu turno. **Efeito:** detecta a presença somente de efeitos mágicos explicitamente registrados com origem **pública, verificável** no campo. No recorte atual o único registro público mágico conhecido é a concentração em magia da própria Owl; Tentacle/Grappled/Poisoned do Roper **não são** magia. Não inferir magia da inexistência de atributos catalogados.

A conjuração **não fornece escola ou aura gratuitamente**: o SRD exige Action subsequente para examinar aura/escola. Esta inspeção **não está implementada** sem efeito mágico adicional com metadados da escola comprovados; o resultado informa `aura_escola_revelada=false`. O registro de concentração pública da própria Owl não revela novas informações ocultas.

**Concentração:** até 10 minutos ou 100 rodadas.

## 3. Clairvoyance

**Norma final nesta POC: INAPLICÁVEL e rejeitada sem custo**, não apenas aguardando rolagem. O texto SRD exige **10 minutos de conjuração** e **sensor em uma localização**. Não há localização nem mecanismo aprovado de conjuração prolongada fora de turno nesta fixture. Não inventar campo, sensor, visão, som, posição, ação instantânea, recurso consumido ou acesso a mãos adversárias. Seu limite da ficha **1/dia** continua documentado, mas **nunca consumido** por tentativa inválida.

## Concentração e custos — aplicáveis aos dois Detect

- **Action consumida no lançamento**, mudando para o próximo turno apenas após a transação completa e verificável; detecções à vontade não consomem carga diária.
- No início de uma nova magia com concentração, a anterior da Owl termina.
- Recebido dano não letal, testar **salvaguarda de Constituição** com bônus **+1 extraído estritamente da ficha externa** da Giant Owl, com d20 simulado explícito. CD `min(30, max(10, dano_aplicado // 2))`. Cada Bite com dano exige seu próprio teste enquanto a concentração permanecer ativa; primeiro fracasso encerra a concentração.
- **Sem d20 exigido:** evento completo fica **PENDENTE sem mutação** de PV, condições, recursos, turno, zonas, placar ou histórico aceito. d20 inválido rejeita a ação com a mesma garantia transacional. Dano zero/erro não provoca teste.
- **KO:** remove a concentração antes de concluir o confronto. O criador pode encerrar concentração voluntariamente sem Action, inclusive fora da própria vez.
- **Prazo:** expira no início do turno da Owl na rodada `rodada_inicio + 100` (10 minutos a seis segundos/rodada), se ainda ativa. A engine de combate auditável não concede duração indefinida.
- **Não introduzir** recursos adicionais, escolas não verificadas, alvos fora do campo, exploração de dados privados ou benefícios não descritos.

## Validação

`src/ascend/magias_owl_poc.py`: salvaguarda de Constituição derivada da ficha, categorização SRD verificada e detecção estrita do campo público. `MotorRoperBasico`: `CONJURAR_MAGIA_OWL_TESTE`, `ENCERRAR_CONCENTRACAO_OWL_TESTE`, `prevalidar_conjuracao_owl()`, integração de salvaguarda de concentração em Bite e Multiattack, expiração temporal e cleanup de KO. Testes em `tests/integration/test_owl_spellcasting_publico_real.py`.

**Limite:** somente fixture Roper × Giant Owl, não combate SRD integral. Partida oficial não iniciada; placar J1 0 × 0 J2.
