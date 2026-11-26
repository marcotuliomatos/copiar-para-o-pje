# Testes e validação

## Níveis de verificação

| Nível | Comando ou procedimento | Alcance |
|---|---|---|
| Estático | `python3 -m unittest discover -s tests -v` | XML, manifesto, JAR, integridade da referência, ausência de nomes de atributos MCE e contrato MIME declarado, build reproduzível. |
| UNO | `python3 scripts/test_uno.py` | Instalação em perfil isolado e execução real de `Diagnostico` em documento sintético. |
| Clipboard gráfico | Checklist abaixo | Formatos efetivamente publicados, persistência e comportamento em sessão gráfica. |
| PJe real | Checklist abaixo | Renderização, integridade e editabilidade após a colagem real. |

O teste UNO usa `tests/fixtures/regressao-mce.json`, cria parágrafos Writer de verdade, compara os textos e a posição do vazio intencional e verifica os atributos do HTML com parser. Não é uma suíte completa de regressão, nem um substituto para testes de tabelas, imagens e seleção. Novos casos devem ser incorporados incrementalmente. Não introduzir documentos judiciais reais.

## Checklist manual para uma release

Use perfil de teste, Writer e uma minuta sintética; anote versões do sistema, LibreOffice, navegador e PJe. Não assine, protocole ou salve documentos judiciais reais.

- [ ] Instalação limpa e atualização do OXT; menu de contexto sem duplicação; botão, menu Editar, `Ctrl+Shift+C` e personalização do atalho; `Ctrl+C` nativo intacto.
- [ ] Documento completo e seleção parcial no meio do parágrafo; preservação do texto e do ODT original; cancelamento de seleção não suportada sem substituir clipboard anterior.
- [ ] Acentos, caracteres especiais, espaços, tabs, quebras manuais, parágrafos vazios intencionais e quatro itens manuais `1)` a `4)`, sem vazio adicional antes do quarto item.
- [ ] Estilos reais de referência do AGENTS.md, herança, formatação direta, entrelinhas, margens e recuos.
- [ ] Listas aninhadas, reinício e continuidade; tabelas e mesclagens; seleção de células; imagens, recorte, rotação e limites; hyperlinks e esquemas bloqueados.
- [ ] Clipboard: HTML UTF-8 e texto simples disponíveis, cópia repetida e nenhum atributo MCE antes da colagem. Confirmar os MIME expostos pela plataforma e as três representações UNO previstas no contrato.
- [ ] PJe: colagem repetida, preservação de conteúdo e vazios, links e editabilidade; cabeçalho do editor intacto; comparação visual e estrutural.
- [ ] Rollback para pacote conhecido, caso necessário.

Em Wayland, `wl-paste --list-types` e `wl-paste --type text/html` ajudam na inspeção, somente com dados sintéticos. Diferencie o HTML antes da publicação, o HTML efetivamente publicado e o HTML pós-colagem. A presença de atributos adicionados internamente pelo TinyMCE após a colagem não comprova emissão pela extensão. Não remover vazios indiscriminadamente.

## Validação inicial desta árvore

- Seis testes estáticos: passaram.
- LibreOffice 25.2.3.2 (headless, perfil temporário): teste do conversor passou, com seis parágrafos, texto integral e ausência de MCE.
- Área de transferência em sessão gráfica, interface e PJe real: não testados.
