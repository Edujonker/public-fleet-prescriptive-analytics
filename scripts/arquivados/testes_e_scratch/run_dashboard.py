#!/usr/bin/env python3
"""
Servidor local para visualização do Dashboard Interativo
Execute este script e abra o navegador em: http://localhost:8080/dashboard/
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 8080
os.chdir(Path(__file__).parent)

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def main():
    port = PORT
    for p in [8080, 8081, 8082, 8888, 3000]:
        try:
            with socketserver.TCPServer(("", p), CustomHandler) as httpd:
                print(f"\n=======================================================")
                print(f"🚀 DASHBOARD ACADÊMICO ATIVO")
                print(f"👉 Acesse no navegador: http://localhost:{p}/dashboard/")
                print(f"👉 Relatório em PDF:    http://localhost:{p}/relatorios/relatorio_dissertacao_completo.pdf")
                print(f"Pressione Ctrl+C para encerrar o servidor.")
                print(f"=======================================================\n")
                httpd.serve_forever()
        except OSError:
            continue

if __name__ == "__main__":
    main()
