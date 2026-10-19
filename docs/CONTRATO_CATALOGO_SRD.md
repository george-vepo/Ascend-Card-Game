# Contrato de leitura — Catálogo SRD

**Ascend Card Game NÃO armazena cartas, fichas, atributos de criaturas ou imagens.**

A origem externa está fixada em `config/catalogo_srd.json` pelo commit do Catálogo SRD. A leitura utiliza o checkout externo como somente leitura e registra hashes SHA-256 dos dois documentos de referência.

- Celestial: IDs originais de cópia `CE-001...CE-040`.
- Aberração: o catálogo contém **posição 1...40**, não um ID de cópia POC. O Ascend gera em memória `AB-POC-001...AB-POC-040`, somente para o estado de teste.
- São validados nome, tipo, ND e raridade; o mesmo nome pode existir em cópias diferentes.
- Faixas do ND seguem a POC: Comum 0–5, Incomum 6–10, Rara 11–15, Lendária 16–20, Mítica 21+; ND fora das faixas fica pendente.
- `HOMOLOGACAO_JOGO` e `status` são apenas **declarações de fonte**. O adaptador não homologa automaticamente criaturas, ataques, magias ou suportes.
- O **arquivo de origem não é alterado**. Não há embaralhamento, compra, combate nem estado oficial.

## Uso

Clone separadamente o Catálogo SRD. Para inspecionar o checkout sem alterar nada:

```bash
python tools/inspecionar_catalogo.py --catalogo /caminho/para/Catalogo-SRD
```

Por padrão, a revisão deve ser exatamente a do manifesto. Se o catálogo avançar, **revise os dados, atualize conscientemente o commit no manifesto e execute a regressão**. O teste de integração em CI usa checkout esparso, sem incluir os dados no commit do Ascend.

O código histórico continua em `experimental/legacy/`; sua compatibilidade com esse adaptador ainda está pendente de integração.
