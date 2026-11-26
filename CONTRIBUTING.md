# Desenvolvimento e contribuição

Leia primeiro `AGENTS.md`. A regra principal é conservar a integridade da minuta. Uma pequena correção bem testada vale mais do que uma reescrita ampla.

## Fluxo de trabalho

1. Registre comportamento esperado, observado, versões e um exemplo sintético mínimo; nunca anexe uma minuta real.
2. Identifique a etapa onde aparece a divergência: UNO, geração HTML, clipboard ou editor do PJe.
3. Acrescente teste de regressão quando possível. Modifique apenas os componentes necessários; preserve o JAR se não houver fonte e build verificáveis.
4. Execute os testes estáticos e o build. Execute UNO e a validação manual conforme o risco da alteração. Não transforme testes que falham em testes que passam por relaxamento injustificado de expectativas.
5. Revise o diff, em especial texto Basic dentro de XML, manifesto, identidade da extensão e regras de escaping. Documente alterações, testes efetivos e limitações.

Para iniciar o histórico local após extrair este ZIP, se desejar:

```sh
git init -b main
git add .
git diff --cached --stat
git commit -m "Importa base v0.8.4 e infraestrutura de desenvolvimento"
```

Esses comandos são opcionais e ficam sob controle do mantenedor. Não há histórico Git anterior fabricado no pacote. Não publique o repositório antes de decidir licenciamento e revisar os metadados originais. Não altere credenciais, perfis do LibreOffice nem instalações institucionais sem autorização.

## Edição

O fonte canônico é `extension/PJeCopy/Module1.xba`. Edite o XML com cuidado: o texto Basic contém entidades como `&amp;` e `&lt;`. Para leitura sem escaping, `python3 scripts/show_basic.py` imprime apenas o texto Basic; não mantenha uma segunda cópia editável divergente. Não reformatar o arquivo inteiro por causa de um bug localizado.

Versionamento segue a versão X.Y.Z em `extension/description.xml`; alterações de desenvolvimento não exigem incremento imediato. Consulte `docs/releasing.md` ao preparar uma entrega. O workflow de CI roda somente validação estática, sem acesso a dados do PJe.
