# Separação de repositórios — Ascend Card Game e Catálogo SRD

Data de decisão: 2026-10-18. Estado: **PLANEJADO; não executado no GitHub**.

## Decisão do administrador

- **Ascend Card Game** será o projeto do jogo: regras aprovadas, decisões da POC, motor, IA, interface, estado, testes e código de integração.
- **Catálogo SRD** será o projeto de conteúdos: catálogo de criaturas, cartas/IDs, coleções de referência, fichas e atributos, fontes, imagens e pesquisas. Manter no catálogo seu supervisor/pipeline de coleta, validação e publicação, pois estes atendem à construção dos dados, não ao duelo.
- Não duplicar fichas integrais, arte ou datasets extensos no Ascend. Usar adaptadores de leitura por ID; registrar versão SHA/commit da origem para reprodutibilidade.
- Não excluir o conteúdo existente antes de concluir a migração e validar seus vínculos.

## GitHub: situação verificada nesta etapa

- Original: `george-vepo/SRD-Card-Game-607-Supervisor`, **público**, branch padrão `main`; contém `docs/catalogo/`, `operational/research/`, `state/`, `tests/`, workflows e sites.
- Nome desejado para o original: `george-vepo/Catalogo-SRD`. **Renomeação pendente da ação do proprietário no GitHub** (a integração atual não oferece alterar nome/Settings do repositório).
- Novo repositório desejado: `george-vepo/Ascend-Card-Game`; **não existente na última verificação**. Sugestão: privado, com `README.md` inicial; sua criação exige o proprietário no GitHub.
- O antigo tem PRs abertos e GitHub Pages via `docs/`. Após renomear, conferir remotes, links, ações e URL de Pages. Não apagar/recriar o repositório para renomear.

## Fontes existentes da POC a migrar para o Ascend

Biblioteca ChatGPT: `/SRD Card Game/POC/`

1. `01_Regras/CONTRATO_DE_REGRAS.md` e `01_Regras/POC_v1.1...v2.1_*.md` — conservar decisões históricas, gerar um contrato atual de regras com precedência explícita.
2. `00_Governanca/DECISOES_E_PENDENCIAS.md`, `00_Governanca/DECISAO_*.md`, `00_Governanca/STATUS_ATUAL_PRE_PARTIDA.md` — decisões e pendências; separar estado de projeto de estado de partida.
3. `02_Interface/FLUXO_DE_TELAS.md`, `02_Interface/COMPONENTES_UI.md` — especificação da mesa, zonas e privacidade.
4. `04_Estado/SCHEMA_ESTADO_POC.json`, `04_Estado/TEMPLATE_PARTIDA_NAO_INICIADA.json` — contrato de estado e fixture **não iniciada**, nunca partida oficial ou dados ocultos.
5. `05_Testes/CASOS_TESTE.json`, `05_Testes/PLANO_TESTES.md`, `05_Testes/CHECKLIST_ANTES_EMBARALHAR.json` — cenários e verificação.
6. `07_Motor_Experimental/` — código, testes e evidência, avaliando módulos vigentes antes de integrar; não copiar indiscriminadamente todas as dezenas de pastas/versionamentos como produto ativo. O checkpoint v6.3 é um dos mais recentes verificados, mas não equivale por si só ao motor do jogo concluído.
7. `06_Prompts/PROMPT_MESTRE_POC.md` — diretrizes do árbitro e comandos, manter documentação sincronizada com regras aprovadas.

## Organização sugerida do Ascend

```text
Ascend-Card-Game/
  README.md
  docs/
    rules/             # contrato consolidado e versões históricas
    decisions/         # aprovações e pendências
    interface/         # mesa, privacidade e fluxos
    architecture/      # integração somente leitura ao Catálogo SRD
  ascend/
    game/              # zonas, fases, compra, evolução, suportes, pontuação
    combat/            # adaptação fiel do SRD e das fichas
    ai/                # estratégia do J2 sem informação oculta
    adapters/          # leitura por ID/cópia e commit de catálogo
    persistence/       # checkpoints, trilha auditável, idempotência
  schemas/
  tests/
  scripts/
  .github/workflows/
```

## Contrato entre repositórios

- Antigo (Catálogo SRD) é a **fonte de verdade dos dados mecânicos de criatura** e dos metadados/arte, inclusive distinção entre ficha integral e resumo de pesquisa.
- Novo (Ascend Card Game) é a **fonte de verdade das regras do jogo, decisões administrativas e código de resolução**.
- Chave: ID canônico do catálogo + ID exclusivo da cópia no deck/partida. Não inferir posse oficial da coleção pelas cópias virtuais POC.
- Adaptadores devem registrar revisão/commit consumida e exigir dados suficientes para a ação real; pendência de ficha não deve impedir antecipadamente testes estruturais.
- Não persistir mãos adversárias, ordem dos montes ou checkpoints de partidas reais em repositório público, issues, logs de CI ou página web.
- Não alterar a definição de regra durante a migração. Regras POC aprovadas prevalecem segundo seus registros.

## Sequência proposta

1. Proprietário renomeia o original **em Settings → General → Repository name** para `Catalogo-SRD`.
2. Proprietário cria repositório privado `Ascend-Card-Game` com README e disponibiliza à integração GitHub do ChatGPT (se necessário, ampliar o acesso da instalação ao novo repo).
3. Verificar IDs/URLs/branch padrão dos dois repositórios e a publicação do catálogo, sem alterar datasets.
4. Criar **branch de migração** no Ascend; importar docs de regras, schemas e testes; abrir PR para revisão.
5. Migrar módulos do motor com consolidação e regressão automatizada; não transportar estados de partidas reais.
6. Implementar adaptador de leitura por commit/ID ao Catálogo SRD. Executar testes de integração.
7. Validar PR e integrar à `main` somente com aprovação de revisão; manter o original intacto.

## Restrições atuais

Nenhum repositório foi renomeado/criado nesta etapa. Nenhuma carta, ficha, imagem, regra competitiva, dado oculto ou partida foi movida. Nenhum embaralhamento, compra ou combate oficial foi executado.