# AGENTS.md — Copiar para o PJe

Instruções para agentes de desenvolvimento que atuem neste repositório. Aplicam-se a todo o projeto. A base técnica descrita abaixo corresponde aos pacotes OXT 0.8.3 e 0.8.4 inspecionados; confirme o estado atual do repositório antes de modificar qualquer arquivo.

## 1. Finalidade e prioridades

O **Copiar para o PJe** é uma extensão do LibreOffice Writer que converte o conteúdo de uma minuta, integral ou selecionado, em HTML formatado e o disponibiliza na área de transferência para colagem no editor do Processo Judicial Eletrônico (PJe).

O objetivo é permitir a redação no Writer e a transferência para o PJe com conteúdo íntegro, formatação fiel e texto editável, reduzindo o retrabalho. Não é um exportador genérico de HTML, um formatador de documentos, nem uma automação de peticionamento. A referência de compatibilidade é o PJe real, inclusive seu TinyMCE legado, e não apenas um navegador moderno.

Ordem de prioridades para decisões técnicas:

1. **Integridade:** não omitir, acrescentar, duplicar, alterar ou reordenar conteúdo indevidamente.
2. **Privacidade e segurança:** processamento local, sem exposição de dados judiciais.
3. **Compatibilidade:** produzir HTML que o editor do PJe consiga receber, exibir e editar.
4. **Fidelidade:** preservar as propriedades efetivas e a estrutura lógica do documento, dentro das capacidades do destino.
5. **Simplicidade:** reduzir a complexidade do código, do uso, da instalação e da manutenção, sem sacrificar as prioridades anteriores.

Se um elemento não puder ser convertido com segurança, cancelar a operação com mensagem clara em português, em vez de entregar conteúdo incompleto silenciosamente. Não sacrificar integridade para obter semelhança visual.

## 2. Ambiente, escopo e experiência de uso

- Ambiente de referência: Arch Linux, KDE Plasma, Wayland, LibreOffice Writer e PJe do TJPI. Não presumir compatibilidade comprovada com outras plataformas, versões do Writer ou instalações do PJe; tampouco introduzir dependências específicas de uma plataforma sem necessidade demonstrada.
- `Ctrl+C` permanece como a cópia nativa do Writer. `Ctrl+Shift+C` é o atalho padrão, personalizável, da extensão. Preservar o botão na barra padrão, o comando no menu Editar e a integração ao menu de contexto, restritos ao Writer.
- A colagem é efetuada pelo usuário. Não automatizar teclado, mouse, navegador, login, salvamento, assinatura ou protocolo no PJe.
- Não alterar texto, formatação, estilos, seleção ou estado do documento original para realizar a cópia. Não aplicar estilos PJe automaticamente.
- Não depender de X11, `wl-copy`, `wl-paste`, InputActions, macros pessoais ou serviços externos para a operação normal. Ferramentas específicas do ambiente podem ser usadas em diagnósticos locais.
- A automação pessoal de alternância de estilos no Writer é um projeto distinto. Não modificar nem incorporar sua configuração, seus atalhos ou suas dependências sem solicitação específica.

## 3. Arquitetura e base de código

Identificador da extensão: `local.pje.copiar`. Base corrigida inspecionada: `Copiar_para_o_PJe_v0.8.4.oxt`, versão declarada `0.8.4`. O OXT é um arquivo ZIP instalável; se o repositório partir somente dele, extrair e versionar os arquivos-fonte, mantendo o pacote original como referência. Não presumir que a extensão instalada, o pacote distribuído e a árvore de trabalho sejam idênticos.

| Componente | Responsabilidade |
| --- | --- |
| `PJeCopy/Module1.xba` | Conversor LibreOffice Basic/UNO, validações, serialização HTML/CSS e clipboard. O Basic está contido em XML: preservar UTF-8 e escaping XML. |
| `PJeCopy/script.xlb`, `PJeCopy/dialog.xlb` | Registro da biblioteca Basic. |
| `Addons.xcu` | Botão na barra padrão e entrada no menu Editar, após `.uno:Copy`. |
| `Accelerators.xcu` | Atalho `C_SHIFT_MOD1` no Writer. |
| `Jobs.xcu`, `ContextJob.components`, `ContextJob.jar` | Serviço Java UNO `local.pje.ContextJob`, acionado em `onDocumentOpened`, para integração do menu de contexto. Segundo a inspeção histórica do bytecode, insere o comando após `.uno:Copy` e evita duplicação; não realiza a conversão HTML. |
| `description.xml`, `META-INF/manifest.xml` | Identidade, versão, metadados e registro dos componentes. |
| `descricao-pt-BR.txt`, `description-en.txt`, `icons/` | Apresentação, ícones e créditos. Preservar `icons/NOTICE.txt`. |

O pacote 0.8.4 não contém fonte Java, script de build nem suíte de testes. Verificar se já existem no repositório. Preservar `ContextJob.jar` em alterações restritas ao Basic; não substituir binários sem fonte e processo de compilação verificáveis. A conversão não depende de reescrever a integração Java.

### Fluxo de execução

- Entrada única da interface: `PJeCopy.Module1.CopiarParaPJe`, por `vnd.sun.star.script:PJeCopy.Module1.CopiarParaPJe?language=Basic&location=application`.
- `Converter(doc)` retorna `Array(fragmentoHTML, textoOriginal)` ou sinaliza falha por `PjeFailure`. Sem seleção textual no corpo, converte o documento inteiro. Suporta seleção contínua de texto e seleção retangular simples de células; seleções descontínuas e outras situações não suportadas devem falhar explicitamente.
- `Blocos` percorre parágrafos e tabelas e estrutura listas. `Paragrafo` e `Trecho` leem propriedades efetivas via UNO. `EstiloParagrafo`, `Fonte`, `Estilo`, `Escapar`, `Atributo`, `CssTexto`, `Numero` e `Pixels` concentram regras de apresentação, escaping e unidades.
- `Tabela`/`TabelaSelecao`, `InfoLista`/`ComEstilosLista` e `ImagemObjeto` tratam estruturas específicas. Conferir os fluxos de objetos, listas e tabelas antes de modificar rotinas compartilhadas.
- `CopiarParaPJe` envolve o fragmento em HTML com `meta charset="utf-8"`, codifica-o em UTF-8 e publica os dados usando `SystemClipboard` e `CreateUnoListener("PJE_", "com.sun.star.datatransfer.XTransferable")`. As variáveis globais mantêm dados e listener disponíveis para a leitura posterior pelo consumidor do clipboard.
- `Diagnostico(doc)` permite obter a saída de `Converter` sem publicar no clipboard. Em falhas sinalizadas por `PjeFailure`, retorna `Array(PjeFailure, "")`. É um ponto de entrada útil para testes locais.

Preservar os formatos do `XTransferable`:

| MIME type | Representação UNO |
| --- | --- |
| `text/html` | `[]byte`, HTML UTF-8 |
| `text/plain;charset=utf-16` | `string`, texto Unicode |
| `text/plain;charset=utf-8` | `[]byte`, texto UTF-8 |

Não substituir a conversão própria via UNO pela cópia nativa ou exportação HTML genérica do Writer sem demonstrar equivalência de conteúdo, formatação e compatibilidade no PJe.

## 4. Contrato de conversão

### Integridade e falhas

Preservar as conferências existentes de `actual` contra `expected`, de texto e mapeamento das células, e da contagem de imagens na conversão integral. Elas são proteções importantes, mas não constituem prova suficiente de que o HTML serializado está correto. Testar também a estrutura e o conteúdo efetivamente emitidos.

A exceção atual de `Converter` para `expected = actual & Chr(10)` acrescenta uma quebra ao texto e um parágrafo vazio terminal ao HTML. Não removê-la nem ampliá-la sem teste de regressão. Não confundir essa exceção com um parágrafo vazio inserido antes do último item textual.

Preservar espaços significativos, tabulações, Unicode, acentos, entidades, quebras manuais, parágrafos vazios intencionais, sequência e limites de seleção. Não aplicar `Trim` ao conteúdo textual nem normalizações globais que possam alterar o sentido. Manter a representação em texto simples e a HTML coerentes com suas respectivas funções, levando em conta marcadores de listas e objetos.

Construir e validar os dados antes de publicar no clipboard. Uma conversão cancelada não deve substituir a cópia anterior por dados parciais, inclusive considerando o estado das variáveis globais usado pelo listener. Não mascarar falhas de conversão para continuar a cópia.

### HTML, CSS e compatibilidade

- Gerar HTML convencional, válido, autocontido, editável e proporcional à estrutura original. Priorizar elementos semânticos (`p`, `strong`, `em`, `u`, `ol`, `ul`, `li`, `table` etc.) e CSS inline compatível com o PJe.
- **Não emitir atributos internos do TinyMCE ou de outros editores**, tais como `mce_style`, `mce_href`, `data-mce-style`, `data-mce-href` e demais `mce_*`/`data-mce-*`. `Estilo` emite apenas `style`; links usam `href`. Não reintroduzir duplicações como suposta melhoria de compatibilidade.
- Não remover atributos ou elementos que o editor de destino gere legitimamente após a colagem. A restrição anterior aplica-se ao HTML produzido pela extensão.
- Manter escaping correto para texto, atributos, valores CSS e XML do módulo. Não confundir escaping de HTML com escaping de CSS ou XML. Não usar regex indiscriminada para transformar HTML ou remover parágrafos vazios.
- Não introduzir scripts, eventos executáveis, CSS externo, fontes remotas ou dependências de rede para renderizar a minuta. CSS embutido já utilizado em listas hierárquicas é permitido; preservar seu fallback caso o editor descarte a regra.
- Manter links com `href` escapado, `target="_blank"` e `rel="noopener noreferrer"`. Preservar e testar a rejeição de esquemas inseguros ou locais (`javascript:`, `data:`, `file:`); revisar variantes e normalização de URLs quando necessário. Não confundir links com os `data:image/png` gerados pela própria extensão.

### Formatação efetiva

Converter propriedades efetivas do Writer (herança, estilos personalizados e formatação direta), nunca presumir formatação a partir do nome de um estilo. Preservar, quando representáveis e aceitos pelo destino:

- Fontes e tamanhos, negrito, itálico, sublinhado, tachado, cores, realce, sobrescrito/subscrito, espaçamento de caracteres, maiúsculas/minúsculas via CSS sem reescrever o texto, capitulares e demais recursos já implementados.
- Parágrafos, títulos semânticos, alinhamento, recuos, margens, entrelinhas, bordas, fundos e separadores horizontais.
- Listas numeradas e com marcadores, níveis, continuidade/reinício, rótulos personalizados e hierárquicos. Não confundir `1)` digitado manualmente com lista UNO. Preservar rótulos de fallback e evitar sua duplicação quando CSS for aplicado.
- Tabelas, dimensões, células mescladas, alinhamentos, bordas, preenchimentos e seleção simples de células. Não achatar tabelas ou descartar células para contornar erros.
- Imagens PNG/base64, dimensões, ancoragem, posicionamento, recorte e rotação quando suportados; manter temporários removíveis e limite vigente de 20.000.000 bytes por PNG exportado. Imagens ancoradas à página e objetos sem representação segura devem provocar falha explícita.

### Mapeamentos específicos do PJe

Não tratar estas fórmulas como conversões físicas universais: são escolhas de compatibilidade da implementação atual.

| Propriedade UNO | Saída atual |
| --- | --- |
| `ParaFirstLineIndent` fora de listas | `text-indent: Numero(n * 8 / 2000)%` (2 cm → 8%) |
| `ParaLeftMargin` positivo fora de listas | `padding-left: Numero(n * 150 / 4000)px` (4 cm → 150 px) |
| Recuo incremental de listas | mesma escala `n * 150 / 4000` em px |
| Conversão geral `Pixels(n)` | `n * 96 / 2540` em px (unidade UNO: 1/100 mm) |

Manter `align` e CSS inline quando necessários para compatibilidade. Não uniformizar essas escalas, substituir `padding-left` por `margin-left` ou eliminar atributos HTML legados indiscriminadamente sem teste comparativo no PJe.

### Estilos de referência para testes, não regras de produção

Os estilos abaixo foram registrados no documento de referência da conversa original. Reproduzi-los em fixtures sintéticas, inclusive sua herança e variações; não hardcodificar nomes ou valores no conversor.

| Estilo | Propriedades observadas |
| --- | --- |
| `PJe - Normal` | Arial 10 pt, justificado, entrelinhas 150%, primeira linha 2 cm, margem inferior 0,25 cm. |
| `PJe - Título` | Arial 10 pt, negrito, maiúsculas por propriedade de estilo, justificado, sem recuo inicial, margem superior 0,75 cm, inferior 0,25 cm. |
| `PJe - Citação` | Arial 10 pt, itálico, justificado, recuo esquerdo 4,001 cm, sem recuo inicial, entrelinhas 150%, margem inferior 0,25 cm. |
| `PJe - Título Centralizado` | Herda Título, centralizado, também em itálico, margem superior zero. |

## 5. Regressão conhecida: atributos MCE e parágrafo vazio

**Estado confirmado nos pacotes:** na v0.8.3, `Estilo` duplicava `style` em `mce_style` e `Trecho` duplicava `href` em `mce_href`. A v0.8.4 remove ambas as emissões; não há referências a esses atributos nem a `data-mce-*` no Basic dessa versão. A comparação dos pacotes mostra alterações somente em `PJeCopy/Module1.xba` e `description.xml`. Isso comprova a correção no fonte, não a versão efetivamente instalada nem o resultado de colagem real.

**Histórico relatado no AGENTS.md original:** um ODT de referência tinha 134 parágrafos (129 com texto e 5 vazios intencionais). Duas capturas do HTML do clipboard eram idênticas (130.281 bytes, 134 parágrafos, 470 atributos `mce_style` duplicando `style`, dos quais 134 em `p` e 336 em `span`). No PJe havia 135 parágrafos, com um vazio adicional imediatamente antes do último item manual `4)`. O vazio não aparecia no HTML anterior à colagem. A remoção de `mce_style` do clipboard resolveu o sintoma na ocasião relatada. Essas observações históricas não foram reproduzidas nesta revisão e não demonstram a causa interna do TinyMCE nem resolução definitiva.

Se o sintoma reaparecer:

1. Confirmar versão instalada, perfil ativo do LibreOffice, comando associado ao atalho e ausência de instalações duplicadas ou macros antigas. Se necessário, reproduzir com perfil isolado e pacote conhecido.
2. Comparar, com documento sintético, quatro etapas: `Diagnostico(doc)`/`Converter`; HTML final imediatamente antes da publicação no clipboard; HTML efetivamente lido do clipboard; HTML do PJe imediatamente após colar. Registrar versões, formatos e contagens, não minutas reais.
3. No Wayland, `wl-paste --list-types` e `wl-paste --type text/html` podem auxiliar o diagnóstico. Testes A/B com o mesmo HTML, com e sem atributos MCE, na mesma posição de inserção e navegador, podem isolar o comportamento. `wl-copy --type text/html < arquivo.html` é apenas diagnóstico, pois não republica os formatos de texto simples.
4. Corrigir a primeira etapa que introduzir a divergência, não um efeito posterior sem causa demonstrada. Se o conversor já emite HTML limpo, não criar patch inócuo nele. Não eliminar todos os `<p><br></p>`; preservar vazios intencionais. Não modificar o PJe institucional sem autorização.

Manter a regressão mesmo que o problema deixe de ocorrer. Para investigações futuras, preferir documentação histórica separada (por exemplo, `docs/` ou registro de issues) a acumular transcrições de conversas neste arquivo.

## 6. Testes e critérios de aceite

Inspecionar testes e ferramentas existentes antes de criar novos. Se ainda não houver infraestrutura, introduzi-la de forma incremental e reproduzível. Usar fixtures ODT sintéticas, pequenas e representativas, com HTML e resultados estruturais esperados. Não usar documentos judiciais reais. Sempre que viável, executar UNO/LibreOffice em perfil isolado, testar `Diagnostico` e analisar o HTML com parser apropriado, além da inspeção estática.

Cobertura mínima a manter e ampliar:

| Área | Casos essenciais |
| --- | --- |
| Texto e seleção | Unicode, entidades, espaços consecutivos, tabulações, quebra manual, parágrafos vazios, seleção parcial no meio do parágrafo, documento integral, término com/sem quebra terminal. |
| Regressão MCE | Quatro parágrafos de citação iniciados por `1)` a `4)`, vazio intencional antes de outra seção; nenhum vazio extra entre `3)` e `4)`. Conferir quantidade, ordem e posição dos vazios e ausência de atributos MCE no HTML emitido. |
| Estilos | Quatro estilos de referência, herança, nomes diferentes ou ausentes, formatação direta e mista, fontes, cores, recuos, margens, entrelinhas. |
| Listas | Numeração simples, aninhada, retomada, reinício, marcadores personalizados/de imagem, fallback sem CSS. |
| Tabelas e objetos | Tabelas mescladas, seleção retangular simples e seleção complexa, imagens, ancoragem, recorte, rotação, separadores, limites de tamanho e objetos não suportados. |
| Links e segurança | URLs válidas, caracteres especiais, esquemas bloqueados, escaping de texto/atributos/CSS e imagens base64 geradas localmente. |
| Clipboard e falhas | Três formatos MIME declarados e representações corretas; cópia repetida, validade do listener, cancelamento sem perda da cópia anterior nem modificação do ODT. |
| Instalação e interface | Instalação, atualização e rollback; botão, menus, atalho personalizado e ausência de duplicação; `Ctrl+C` nativo e outras funcionalidades do Writer intactos. |
| PJe real | Colagem repetida integral e parcial, renderização e editabilidade, texto completo, listas, tabelas, imagens e cabeçalho do PJe preservado. |

Para cada bug, reproduzir o caso antes da correção quando viável e acrescentar regressão específica. Verificar tanto diferenças estruturais quanto visuais; uma comparação textual sozinha pode ignorar vazios, listas e imagens.

Distinguir explicitamente os níveis de verificação: (a) inspeção estática/XML/ZIP; (b) execução do conversor em LibreOffice/UNO; (c) clipboard em sessão gráfica; (d) colagem no PJe real. O sucesso em um nível não comprova os níveis seguintes. Testes no PJe somente em ambiente ou minuta de teste autorizados, sem salvar, assinar ou protocolar documento real. Se a sessão gráfica ou o PJe não estiver disponível, informar a limitação e fornecer roteiro manual reproduzível.

## 7. Privacidade e segurança operacional

- Não incluir dados judiciais reais, nomes, números de processo, credenciais ou textos sigilosos em fontes, testes, commits, screenshots, logs, prompts externos ou artefatos de diagnóstico. Gerar exemplos sintéticos.
- Não transmitir minutas, imagens ou conteúdo do clipboard a serviços externos, mesmo para depuração, conversão, telemetria ou IA. Não implementar atualização automática pela rede ou coleta de dados sem decisão expressa do mantenedor.
- Restringir temporários ao processamento necessário e removê-los inclusive nos caminhos de erro. Logs devem conter apenas metadados técnicos estritamente necessários (por exemplo, etapa, contagem ou versão).
- Não baixar dependências, executar scripts remotos ou alterar configurações do ambiente do usuário sem necessidade demonstrada e autorização. Não usar credenciais, sessões ou dados institucionais para testes autônomos.

## 8. Processo de trabalho e manutenção

Antes de editar, ler este arquivo, o código pertinente, os testes e o estado do repositório. As instruções do mantenedor e os fatos verificados no código prevalecem sobre descrições históricas; registrar contradições em vez de perpetuar hipóteses. Não tratar o inventário de funcionalidades deste arquivo como prova de que todas funcionam em execução.

- Identificar o comportamento esperado, reproduzir o problema e localizar sua origem antes de corrigir. Formular hipóteses como hipóteses e não como fatos.
- Fazer mudanças pequenas, coesas e justificadas. Não reescrever a extensão, mudar linguagem/arquitetura, remover recursos ou alterar regras específicas do PJe por conveniência. Mudanças de contrato, dependências ou comportamento de interface exigem decisão expressa do mantenedor.
- Manter `Option Explicit`, nomes e organização coerentes com o código existente, tipos UNO adequados, limites corretos de arrays (`UBound` é o último índice), escaping, propagação de `PjeFailure` e mensagens claras em português. Não silenciar erros capazes de causar perda de conteúdo.
- Preservar alterações preexistentes do mantenedor. Evitar reformatação maciça, mudanças cosméticas não solicitadas e arquivos gerados desnecessários. Não criar commits, tags, publicações ou instalações sem autorização.
- Consultar documentação primária do LibreOffice/UNO, HTML/CSS e TinyMCE quando necessário, identificando a versão relevante. Não confundir capacidades de versões modernas com as do editor de destino.
- Manter documentação, testes e comportamento sincronizados. Registrar decisões de compatibilidade não óbvias, justificativas e evidências de teste. Atualizar este AGENTS.md quando uma regra permanente ou a arquitetura mudar; não registrar nele cada tarefa concluída.

## 9. Empacotamento e entrega

Ao preparar uma versão instalável:

1. Usar o procedimento de build existente. Se ausente, criar/documentar procedimento reproduzível com os arquivos efetivamente presentes; não inventar comandos, scripts ou ferramentas já disponíveis.
2. Atualizar `description.xml` conforme o versionamento adotado e documentar as alterações. Preservar `local.pje.copiar`, metadados, registros UNO e créditos, salvo alteração explicitamente solicitada. Não incrementar versão automaticamente a cada edição de fonte.
3. Gerar ZIP com extensão `.oxt`, arquivos e diretórios do pacote diretamente na raiz, sem pasta envolvente. Excluir `.git`, `AGENTS.md`, documentação de desenvolvimento, testes, backups, temporários e dados judiciais. Preservar os componentes e recursos necessários, inclusive o JAR original quando não alterado.
4. Validar integridade ZIP, XML/XCU/XBA/XLB, referências do manifest, presença dos recursos necessários, identificador e versão. Comparar com a versão anterior e preservar pacote anterior para rollback. Verificar instalação/atualização quando o ambiente permitir.
5. Na entrega, disponibilizar o pacote verificável quando solicitado, indicar versão, arquivos alterados, justificativa, testes executados e resultados, limitações, riscos pendentes e decisões assumidas. Não alegar testes que não foram feitos, compatibilidade universal, correção definitiva de falhas intermitentes ou instalação no ambiente do usuário sem evidência.

Uma tarefa só deve ser considerada concluída no nível de verificação que foi efetivamente alcançado. Integridade e previsibilidade do conteúdo judicial têm precedência sobre a aparência de uma entrega bem-sucedida.
