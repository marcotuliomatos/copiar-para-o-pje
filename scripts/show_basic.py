#!/usr/bin/env python3
"""Exibe o Basic decodificado; não modifica o fonte canônico."""
from pathlib import Path
import xml.etree.ElementTree as ET

source = Path(__file__).resolve().parents[1] / 'extension/PJeCopy/Module1.xba'
print(ET.parse(source).getroot().text, end='')
