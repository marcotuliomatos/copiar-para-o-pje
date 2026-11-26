# Copiar para o PJe

Extensão independente do LibreOffice Writer para copiar minutas completas ou seleções como HTML formatado e texto simples, visando à colagem no editor do Processo Judicial Eletrônico (PJe). Processamento local, sem serviço externo. Projeto pessoal, sem vínculo oficial com o CNJ, o PJe ou o LibreOffice.

**Base de desenvolvimento:** v0.8.4. **Ambiente de referência:** Arch Linux, KDE Plasma, Wayland, Writer e PJe do TJPI. A compatibilidade com outras instalações precisa ser verificada.

## Utilização

1. No Writer, abra **Ferramentas → Gerenciador de extensões**, adicione o OXT e reinicie o LibreOffice, se solicitado. O componente de menu de contexto utiliza Java UNO; se necessário, habilite um JRE compatível nas opções avançadas do LibreOffice.
2. Abra uma minuta de teste. Selecione o trecho desejado ou deixe sem seleção para copiar o documento inteiro.
3. Acione **Copiar para o PJe** pelo botão, menu ou `Ctrl+Shift+C` (personalizável). A cópia comum `Ctrl+C` permanece inalterada.
4. Cole com `Ctrl+V` no editor de destino. Confira o resultado antes de salvar, assinar ou protocolar.

O pacote original v0.8.4 está em `reference/`. Não confunda esse pacote imutável com uma versão gerada a partir de mudanças locais.

## Desenvolvimento rápido

Requisitos para build e testes estáticos: Python 3.10+ (biblioteca padrão; sem pip). `make` é opcional. A extensão continua implementada em LibreOffice Basic/UNO; Python é apenas ferramenta de desenvolvimento.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

O OXT gerado estará em `dist/Copiar_para_o_PJe_v0.8.4.oxt` (ou no caminho correspondente à versão declarada em `extension/description.xml`). O build preserva o conteúdo de cada arquivo, normaliza metadados do ZIP e exclui documentação, testes e dados locais. Com a mesma versão de Python/zlib e os mesmos fontes, o build produz bytes idênticos.

Para somente validar: `python3 scripts/build.py --check`. Com GNU Make: `make test`, `make check`, `make build`.

### Teste real do conversor

Com Writer, `unopkg`, `soffice` e Python com módulo `uno` disponíveis, execute **como usuário comum**:

```sh
python3 scripts/test_uno.py
```

Em distribuições que disponibilizam UNO no Python do sistema, use `/usr/bin/python3` em vez de um ambiente virtual. O script instala o OXT em perfil temporário, cria uma minuta sintética em memória, executa `Diagnostico` via UNO, analisa o HTML e encerra a instância isolada. Não usa o clipboard nem acessa o PJe.

## Estrutura

```text
AGENTS.md                 Instruções para agentes de desenvolvimento
README.md                 Uso e início rápido
CONTRIBUTING.md           Fluxo de manutenção
CHANGELOG.md              Histórico conhecido
extension/                Árvore original do pacote OXT (fonte canônico)
  PJeCopy/Module1.xba     Conversor Basic dentro de XML
  ContextJob.jar          Integração Java legada, preservada
  META-INF/               Manifesto do pacote
  icons/                  Recursos e créditos
scripts/                  Build, validação e teste UNO
tests/                   Testes estáticos e dados sintéticos
  fixtures/               Casos de regressão
docs/                    Arquitetura, testes, releases e pendências
reference/               OXT original e SHA-256
.github/workflows/        CI estática (opcional, se hospedado no GitHub)
```

## Documentação

- [AGENTS.md](AGENTS.md): regras permanentes, prioridades e contrato de conversão.
- [Arquitetura](docs/architecture.md): fluxo UNO, código Basic e componente Java.
- [Testes](docs/testing.md): níveis de verificação, checklist manual e diagnóstico.
- [Releases](docs/releasing.md): empacotamento, instalação e rollback.
- [Pendências](docs/backlog.md): melhorias candidatas, sem compromissos automáticos.
- [Proveniência](reference/README.md): origem do pacote e limites de licenciamento.

## Estado atual

Os arquivos da extensão são idênticos aos do OXT original v0.8.4. A infraestrutura de desenvolvimento foi criada separadamente. Testes estáticos e teste básico do conversor em Writer headless passaram na montagem do repositório; não houve teste da sessão gráfica nem da colagem no PJe real. Não há licença geral explícita no OXT de origem: nenhuma licença de redistribuição foi presumida. Consulte o mantenedor antes de publicar o projeto.
