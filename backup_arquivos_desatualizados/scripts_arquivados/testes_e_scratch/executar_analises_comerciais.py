#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de execução das análises comerciais e estratégicas da frota (PPGCAP/UDESC).
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.analises_comerciais import FleetCommercialAnalytics

if __name__ == "__main__":
    runner = FleetCommercialAnalytics()
    runner.run_all_analyses()
