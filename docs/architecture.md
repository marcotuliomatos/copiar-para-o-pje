# Arquitetura

A extensão original permanece em `extension/`, com a mesma estrutura de arquivos que o OXT. Este diretório é a fonte canônica; `reference/` é apenas referência histórica e rollback. `scripts/` não integra o OXT.

## Fluxo

```text
Writer / seleção
    → CopiarParaPJe
    → Converter → Blocos → Paragrafo / Trecho / Tabela / ImagemObjeto
    → conferências de integridade
    → fragmento HTML + texto simples
    → serialização UTF-8 + XTransferable
    → SystemClipboard
    → colagem manual no PJe
```

`Diagnostico(doc)` permite chamar o conversor sem publicar o clipboard. As rotinas `Estilo`, `Fonte`, `EstiloParagrafo`, `Escapar`, `Atributo`, `CssTexto`, `Numero` e `Pixels` concentram regras transversais. O HTML deve permanecer autocontido, convencional e sem atributos internos MCE. Consulte o contrato detalhado no AGENTS.md antes de alterar fórmulas de medidas, tratamento de vazios, imagens ou listas.

A integração de barra e menu Editar está em `Addons.xcu`; o atalho em `Accelerators.xcu`. `Jobs.xcu` e `ContextJob.components` registram o componente Java do menu de contexto. `description.xml` contém versão e identificador; `META-INF/manifest.xml` registra os componentes do pacote.

## Componente Java legado

O OXT contém `ContextJob.jar` com `local.pje.ContextJob` e `local.pje.ContextJob$Interceptor`, mas não contém seus fontes Java nem script de compilação. O JAR original é versionado e protegido por teste de igualdade de bytes. Não foi criado um fonte Java fictício nem um build supostamente equivalente. Para inspeção local, com JDK instalado:

```sh
jar tf extension/ContextJob.jar
javap -classpath extension/ContextJob.jar -p -c local.pje.ContextJob
javap -classpath extension/ContextJob.jar -p -c 'local.pje.ContextJob$Interceptor'
```

Recuperar o fonte original e uma cadeia de compilação verificável é uma pendência separada. O build atual empacota o JAR existente; não o recompila. Mudanças no Basic não exigem alterações no componente Java.
