#!/usr/bin/env python3
"""Valida e empacota a árvore OXT; sem dependências externas."""
import argparse
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'extension'
FILES = tuple(sorted('''Accelerators.xcu Addons.xcu ContextJob.components ContextJob.jar Jobs.xcu META-INF/manifest.xml PJeCopy/Module1.xba PJeCopy/dialog.xlb PJeCopy/script.xlb descricao-pt-BR.txt description-en.txt description.xml icons/NOTICE.txt icons/pje.svg icons/pje16.png icons/pje26.png icons/pje48.png'''.split()))
XML_SUFFIXES = {'.xml', '.xcu', '.xba', '.xlb', '.components', '.svg'}
D = '{http://openoffice.org/extensions/description/2006}'
M = '{http://openoffice.org/2001/manifest}'
X = '{http://www.w3.org/1999/xlink}'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(source=SOURCE):
    actual = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
    require(actual == set(FILES), f'Arquivos inesperados: {sorted(actual-set(FILES))}; ausentes: {sorted(set(FILES)-actual)}. Atualize a lista explicitamente se necessário.')
    for name in FILES:
        p = source / name
        require(not p.is_symlink(), f'Link simbólico não permitido: {name}')
        if p.suffix in XML_SUFFIXES:
            ET.parse(p)
    desc = ET.parse(source / 'description.xml').getroot()
    require(desc.find(D+'identifier').get('value') == 'local.pje.copiar', 'Identificador alterado')
    version = desc.find(D+'version').get('value')
    require(re.fullmatch(r'\d+\.\d+\.\d+', version), 'Versão deve ser X.Y.Z')
    for element in desc.iter():
        if element.tag in {D+'default', D+'src'}:
            require(element.get(X+'href') in FILES, 'Recurso de descrição ausente')
    manifest = ET.parse(source/'META-INF/manifest.xml').getroot()
    entries = {e.get(M+'full-path') for e in manifest.findall(M+'file-entry')}
    require(entries == {'PJeCopy/', 'Addons.xcu', 'Accelerators.xcu', 'Jobs.xcu', 'ContextJob.components'}, 'Manifest divergente: revisar registros UNO')
    for name in entries:
        require((source/name).exists(), f'Referência ausente: {name}')
    components = ET.parse(source/'ContextJob.components').getroot()
    uris = [e.get('uri') for e in components.iter() if e.tag.endswith('}component')]
    require(uris == ['ContextJob.jar'], 'Referência Java divergente')
    with zipfile.ZipFile(source/'ContextJob.jar') as jar:
        require(jar.testzip() is None, 'JAR corrompido')
        require({'META-INF/MANIFEST.MF', 'local/pje/ContextJob.class', 'local/pje/ContextJob$Interceptor.class'} <= set(jar.namelist()), 'Classes Java ausentes')
    return version


def build(output_dir=ROOT/'dist', source=SOURCE):
    version = validate(source)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f'Copiar_para_o_PJe_v{version}.oxt'
    tmp = output.with_suffix('.oxt.tmp')
    try:
        with zipfile.ZipFile(tmp, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for name in FILES:
                info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                z.writestr(info, (source/name).read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        with zipfile.ZipFile(tmp) as z:
            require(z.testzip() is None and set(z.namelist()) == set(FILES), 'OXT inválido')
            for name in FILES:
                require(z.read(name) == (source/name).read_bytes(), f'Conteúdo divergente: {name}')
        tmp.replace(output)
    finally:
        tmp.unlink(missing_ok=True)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Somente validar fontes')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'dist')
    args = parser.parse_args()
    print(f'Fontes válidos: {validate()}' if args.check else build(args.output_dir))
