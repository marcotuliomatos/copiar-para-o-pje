#!/usr/bin/env python3
"""Smoke test do conversor real em perfil temporário, sem clipboard ou PJe.
Executar com Python que disponibilize o módulo uno e como usuário comum.
"""
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import uuid

from build import ROOT, build


class Paragraphs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.paragraphs = []
        self.current = None
        self.forbidden = []

    def handle_starttag(self, tag, attrs):
        self.forbidden.extend(k for k, _ in attrs if k.startswith(('mce_', 'data-mce-')))
        if tag == 'p':
            self.current = []

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == 'p' and self.current is not None:
            self.paragraphs.append(''.join(self.current))
            self.current = None


def main():
    import uno
    if hasattr(os, 'geteuid') and os.geteuid() == 0:
        raise RuntimeError('Execute como usuário comum; unopkg não instala extensões pessoais como root.')
    for cmd in ('soffice', 'unopkg'):
        if not shutil.which(cmd):
            raise RuntimeError(f'Comando ausente: {cmd}')
    fixture = json.loads((ROOT/'tests/fixtures/regressao-mce.json').read_text(encoding='utf-8'))['paragraphs']
    with tempfile.TemporaryDirectory(prefix='pje-uno-') as tmp:
        tmp = Path(tmp)
        profile = '-env:UserInstallation=' + (tmp/'profile').as_uri()
        package = build(tmp/'dist')
        subprocess.run(['unopkg', profile, 'add', '--force', str(package)], check=True, timeout=60)
        pipe = 'pje_' + uuid.uuid4().hex
        connection = f'pipe,name={pipe};urp;StarOffice.ComponentContext'
        process = subprocess.Popen(['soffice', profile, '--headless', '--norestore', '--nodefault', '--nofirststartwizard', '--accept='+connection], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        desktop = doc = None
        try:
            local = uno.getComponentContext()
            resolver = local.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', local)
            for _ in range(100):
                try:
                    ctx = resolver.resolve('uno:'+connection)
                    break
                except Exception:
                    if process.poll() is not None:
                        raise RuntimeError('LibreOffice encerrou antes da conexão UNO.')
                    time.sleep(.2)
            else:
                raise RuntimeError('Conexão UNO não estabelecida.')
            desktop = ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)
            doc = desktop.loadComponentFromURL('private:factory/swriter', '_blank', 0, ())
            text = doc.Text
            insertion = text.createTextCursor()
            for i, paragraph in enumerate(fixture):
                if i:
                    text.insertControlCharacter(insertion, uno.getConstantByName('com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK'), False)
                    insertion.gotoEnd(False)
                text.insertString(insertion, paragraph, False)
                insertion.gotoEnd(False)
            cursor = doc.CurrentController.getViewCursor()
            cursor.gotoStart(False)
            provider = ctx.ServiceManager.createInstanceWithContext('com.sun.star.script.provider.MasterScriptProviderFactory', ctx).createScriptProvider('')
            script = provider.getScript('vnd.sun.star.script:PJeCopy.Module1.Diagnostico?language=Basic&location=application')
            result, _, _ = script.invoke((doc,), (), ())
            html, plain = result
            parser = Paragraphs()
            parser.feed(html)
            if plain != '\n'.join(fixture):
                raise AssertionError(f'Texto simples divergente ou diagnóstico retornou falha: {html!r}')
            if parser.paragraphs != fixture:
                raise AssertionError(f'Parágrafos divergentes: {parser.paragraphs!r}')
            if parser.forbidden:
                raise AssertionError(f'Atributos proibidos: {parser.forbidden!r}')
            print('OK: conversor UNO; seis parágrafos na ordem correta, vazio intencional preservado, texto integral, nenhum atributo MCE.')
        finally:
            try:
                if doc is not None:
                    doc.dispose()
                if desktop is not None:
                    desktop.terminate()
            finally:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == '__main__':
    main()
