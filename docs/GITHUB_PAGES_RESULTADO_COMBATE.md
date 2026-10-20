# GitHub Pages — interface de resultado manual (demonstração)

**Objetivo:** quando o usuário abrir `https://george-vepo.github.io/Ascend-Card-Game/`, apresentar a **interface de registro manual de batalha** no lugar do README/Jekyll.

## Configurar a publicação

1. Abra [Settings → Pages](https://github.com/george-vepo/Ascend-Card-Game/settings/pages).
2. Em **Build and deployment → Source**, escolha **GitHub Actions** (não `Deploy from a branch`). Essa escolha é necessária porque a interface está em uma subpasta, publicada na raiz da URL pelo artefato do workflow.
3. O workflow [`.github/workflows/deploy-pages.yml`](../.github/workflows/deploy-pages.yml) executa testes e publica automaticamente quando há mudanças relacionadas na `main`. Você também pode iniciá-lo na aba **Actions → Publicar Ascend Card Game no GitHub Pages → Run workflow**.
4. Confira o workflow: o job `build` deve passar; o `deploy` precisa terminar como `success`. Depois atualize a página (Ctrl+F5). Se o Pages ainda mostrar o README, verifique se **Source = GitHub Actions** e se o deploy foi concluído.
5. O endereço esperado do jogo é [https://george-vepo.github.io/Ascend-Card-Game/](https://george-vepo.github.io/Ascend-Card-Game/). O endereço só servirá a nova interface depois do deploy aprovado. Este repositório pode ser privado, mas **o site publicado pode ficar público** dependendo da política/plano do GitHub.

## Como usar a demonstração

- **Preparar combate:** transcrever os dados **públicos** de cada criatura (nome, ID único da cópia, PV máximos, PV atuais e CA opcional) obtidos da fonte apropriada. O site não copia nem inventa valores do Catálogo SRD.
- **Simular no ChatGPT:** fazer a arbitragem conforme fichas/regras aprovadas; não é o Pages que simula ataques ou sorteia dados.
- **Registrar desfecho:** selecionar J1/J2 vencedor, PV restantes positivos e até PV máximos, confirmar que a IA resolveu externamente. A interface registra +1 no placar local, manda a derrotada a um cemitério **de demonstração** com 0 PV e preserva a sobrevivente com PV restantes.
- **Preparar próximo combate:** a sobrevivente permanece identificada com os PV anteriores; só a criatura derrotada é substituída manualmente. Ao terceiro ponto, o registro local se encerra.
- **Atualizar página:** o estado é guardado no armazenamento local (`localStorage`) **somente neste navegador e origem**. O mesmo endereço no celular ou outra pessoa não enxerga esse estado. Limpar dados do navegador ou clicar em **Reiniciar demonstração** apaga esse progresso local.

## Limites importantes

**Esta é uma prova de interface e não um jogo oficial.** O GitHub Pages é hospedagem estática: ele não executa o servidor Python nem persiste a partida entre usuários. O modo local **não** conhece mãos, decks, ordem dos montes, ações, condições, habilidades, compras, todos os 40 IDs e as regras completas; portanto, o placar/PV registrados aqui **não são atualizações da partida oficial nem do motor**. Os resultados informados são explicitamente **não verificados**.

O backend local da [PR #40](https://github.com/george-vepo/Ascend-Card-Game/pull/40) continua em `web/resultado-combate/` e `experimental/integration/site_resultado_manual.py`; não foi substituído nem tornado publicamente acessível. A publicação estática usa `web/pages/` e reutiliza apenas os estilos CSS do formulário original.

**Segurança:** nunca inserir mão oculta, ordem do monte, identificadores secretos ou documentos privados na interface pública. Não atribuir privacidade a resultados persistidos em `localStorage` de um navegador compartilhado.

## Arquivos e testes

- `web/pages/index.html`: página publicada na raiz.
- `web/pages/core.js`: transições locais puras, status demo, validações de PV, vencedor, KO, vencedor aos três pontos, limite de cópias em campo e proteção contra registro duplicado.
- `web/pages/pages.js`: formulário e persistência local, sem chamadas ao backend.
- `web/pages/pages.css` + `web/resultado-combate/styles.css`: estilos responsivos.
- `tests/web/pages-core.test.cjs`: regressão Node do estado local.
- `.github/workflows/deploy-pages.yml`: testa, cria o artefato estático e publica no Pages pela branch `main`.

**Próximo estágio para um site compartilhado:** backend com autenticação, partidas persistentes, leituras de fichas do Catálogo SRD e transação de resultados no motor determinístico; o Pages pode continuar hospedando o frontend desse backend.
