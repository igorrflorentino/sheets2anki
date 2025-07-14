#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from card_templates import create_card_template

template = create_card_template()
print('Template gerado:', template)
print('Contém MATCH?', 'MATCH' in str(template))
print('Campos encontrados:', [k for k in str(template).split() if k.isupper()])
