# Registrar combate simulado fora do site (resultado manual)

**Decisão do usuário:** a IA pode conduzir o combate no ChatGPT ou em outro processo. Em seguida o usuário informa o vencedor e os PV restantes no site. O site **não precisa resolver os ataques novamente**, mas continua responsável por aplicar zonas, PV e pontuação com controle de duplicidade.

## Interface

A POC não possuía um frontend web prévio; este incremento introduz o **primeiro formulário web demonstrativo** em `web/resultado-combate/`:

1. A mesa pública apresenta J1 × J2, campos, criaturas, CA, PV atuais/máximos, condições, combate e versão.
2. O usuário seleciona **J1 ou J2 vencedor**. A interface revela o nome da criatura desse campo e limita a entrada ao PV máximo informado pela ficha.
3. O usuário informa **PV restantes do vencedor (inteiro entre 1 e o máximo)**. O derrotado é sempre interpretado com **0 PV**.
4. O usuário confirma expressamente que a batalha foi simulada externamente e deseja registrar seu resultado.
5. A interface envia `POST /api/resultado` com `evento_id`, número de combate, versão e hash lidos de `GET /api/combate`. Após aceitação, mostra resultado, novo placar e a fase seguinte; um clique repetido com mesmo ID é idempotente.

**Origem registrada:** `CHATGPT_IA_EXTERNA_RESULTADO_MANUAL_NAO_VERIFICADO`. A opção de informar PV finais, inclusive maiores que os atuais dentro do máximo, **não valida cura, magia nem decisões anteriores**: é um resultado atestado pelo operador, não prova de conformidade SRD. Para homologação de resultado oficial, o backend futuro precisará de identidade, autenticação e política de confiabilidade da arbitragem externa.

## Motor

O comando `REGISTRAR_RESULTADO_EXTERNO_TESTE` foi implementado **somente na fixture experimental Roper × Giant Owl**. Em transação única:

- valida fase `COMBATE`, campos com duas criaturas, evento novo, número/versão/hash da leitura da mesa, vencedor válido, PV final e confirmação;
- registra PV restantes do vencedor, aplica o KO existente à criatura derrotada (`pv_atual=0`, `zona=CEMITERIO`), limpa vínculos temporários via `_ko`, marca +1 ponto e encerra a partida ao chegar a 3;
- mantém a criatura sobrevivente em campo, sem cura automática e sem compras entre KO e novo ciclo; preserva todas as 40 cópias, mãos, montes e ordem;
- registra evento encadeado e idempotente pelo `MotorPOC.apply`. Repetição sem alteração devolve o mesmo resultado; alterações após a leitura retornam conflito.

A ação **não** envia dados ocultos ao cliente. O novo campo `ultimo_resultado_externo` é projetado publicamente apenas com informação de combate e placar.

## Executar o site localmente (somente teste)

Pré-requisito: checkout do repositório `Ascend-Card-Game` e checkout Git local limpo do **Catálogo SRD na revisão exata** de `config/catalogo_srd.json`; Python 3.11+.

No diretório raiz do jogo:

```bash
# Substitua pelo caminho de checkout real do Catalogo-SRD na revisão pinada.
export CATALOGO_SRD_DIR="../Catalogo-SRD"
python experimental/integration/site_resultado_manual.py
```

No Windows PowerShell:

```powershell
$env:CATALOGO_SRD_DIR = "D:\\Repos\\Catalogo-SRD"
python experimental/integration/site_resultado_manual.py
```

Acesse **http://127.0.0.1:8765/** no navegador. O exemplo prepara uma **fixture de teste Roper × Giant Owl** com mãos fixas e iniciativa simulada identificada: **não inicia partida oficial**, nem embaralha cartas ou publica state privado. Recarregar/reiniciar essa demo recria a fixture; **não use essa demo para manter uma partida real**.

O servidor local aceita exclusivamente loopback, usa token de formulário e JSON restrito. **Não implantar esse servidor diretamente na Internet.** Autenticação de contas, autorização do jogador, HTTPS, storage privado e partidas reais ficam para o backend futuro.

## Testes e integração

- `tests/integration/test_registro_resultado_externo_web_real.py`: GET/POST reais via HTTP loopback, cartas/campos e PV com fichas externas pinadas, KO, preservação de mãos, placar, vitória aos 3, idempotência, atualização concorrente, privacidade, segurança de token/origem e formulário.
- Workflow `.github/workflows/validate-resultado-combate-web.yml`.
- O registro já usa `MotorPOC.apply` da fixture, **não** atualiza diretamente uma tabela de placar pela interface.

## Próxima etapa

Integrar esse formulário ao site de produção quando ele existir: login/permissões, seleção de partida/ciclo e seu checkpoint persistido, isolamento entre partidas e histórico com declaração externa. Adicionar campo opcional de referência de relatório da IA, se aprovado para a trilha de auditoria, sem tratá-lo como verdade por si só. A modalidade futura de IA que simula em background pode enviar o mesmo contrato **depois de validação pelo backend**; a UI manual continua disponível como alternativa.

**Partida oficial permanece não iniciada; placar J1 0 × 0 J2.**
