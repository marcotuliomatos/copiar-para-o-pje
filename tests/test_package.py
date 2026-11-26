"""Testes estáticos; não simulam a conversão nem a colagem no PJe."""
import hashlib
from pathlib import Path
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from build import FILES, SOURCE, build, validate


class PackageTests(unittest.TestCase):
    def test_structure(self):
        self.assertRegex(validate(), r'^\d+\.\d+\.\d+$')

    def test_reproducible_build(self):
        with tempfile.TemporaryDirectory() as temp:
            a = build(Path(temp)/'a')
            b = build(Path(temp)/'b')
            self.assertEqual(a.read_bytes(), b.read_bytes())
            with zipfile.ZipFile(a) as z:
                self.assertEqual(sorted(z.namelist()), list(FILES))
                for name in FILES:
                    self.assertEqual(z.read(name), (SOURCE/name).read_bytes())

    def test_original_reference_integrity(self):
        for line in (ROOT/'reference/SHA256SUMS').read_text().splitlines():
            digest, name = line.split(maxsplit=1)
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), digest)

    def test_java_binary_preserved(self):
        # Atualizar este teste somente após recuperar fonte/build verificáveis.
        with zipfile.ZipFile(ROOT/'reference/Copiar_para_o_PJe_v0.8.4.oxt') as z:
            self.assertEqual(z.read('ContextJob.jar'), (SOURCE/'ContextJob.jar').read_bytes())

    def test_no_mce_attributes_in_basic(self):
        basic = ET.parse(SOURCE/'PJeCopy/Module1.xba').getroot().text
        # Barreira estática contra reintrodução dos nomes de atributos legados.
        self.assertIsNone(re.search(r'\b(?:data-mce-|mce_)[\w-]+\s*=', basic, re.I))

    def test_clipboard_contract_declared(self):
        basic = ET.parse(SOURCE/'PJeCopy/Module1.xba').getroot().text
        for mime in ('text/html', 'text/plain;charset=utf-16', 'text/plain;charset=utf-8'):
            self.assertIn('"'+mime+'"', basic)
        self.assertIn('Function Diagnostico(', basic)
        self.assertIn('Option Explicit', basic)


if __name__ == '__main__':
    unittest.main()
