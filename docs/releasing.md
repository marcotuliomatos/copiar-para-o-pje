# Preparação de releases

1. Confirme a base e revise alterações e testes. Decida com o mantenedor o número de versão X.Y.Z; altere `extension/description.xml`, mantendo `local.pje.copiar`. Atualize `CHANGELOG.md`.
2. Rode `python3 -m unittest discover -s tests -v` e `python3 scripts/build.py`. Para outro destino use `python3 scripts/build.py --output-dir /caminho/local`.
3. Verifique o resultado com `unzip -t dist/*.oxt` e calcule SHA-256 do pacote específico (`sha256sum dist/Copiar_para_o_PJe_vX.Y.Z.oxt`, substituindo X.Y.Z pela versão real). O build valida o conjunto de arquivos, XML, manifesto, JAR e identidade. Se a estrutura mudar legitimamente, atualize a lista de arquivos no build e os testes de forma explícita.
4. Execute o teste UNO e o checklist de `docs/testing.md`. Não declare compatibilidade sem verificar o destino.
5. Entregue o OXT, versão, checksum, alterações, testes e limitações. Preserve o pacote anterior para rollback. Não crie tags/publicações remotas sem autorização.

O OXT é um ZIP instalável, não o ZIP do repositório. Nunca inclua `.git`, testes, scripts, minutas ou arquivos privados no OXT. A distribuição deve respeitar a situação de licenciamento indicada em `reference/README.md`.

## Rollback

Guarde o OXT da versão anterior. Em perfil autorizado, use o Gerenciador de extensões para remover a versão problemática e instalar a anterior (se necessário, reinicie o Writer). Não modifique ou apague perfis do LibreOffice. Confirme que a versão efetivamente instalada é a pretendida e repita o teste de cópia.
