# 🛡️ Relatório de Auditoria de Segurança DevSecOps & 'Security by Design'

**Data da Emissão:** 15/11/2026 15:38:53  
**Score Geral de Segurança:** `82.0/100.0`  
**Arquivos Analisados:** `532`  

## 1. Conformidade de Bancos de Dados & Armazenamento

| Motor / Banco | Caminho | Status | Criptografia / Proteção | Políticas |
| :--- | :--- | :---: | :--- | :--- |
| **Mongita Disk Engine (MongoDB Compatible)** | `sistema_gestao_frotas/dados/mongodb_data` | `APROVADO` | Ativa (Controle de acesso por permissão de SO e Argon2id para senhas) | Mínimo 8 caracteres, maiúscula, minúscula, números e caractere especial (rejeita puramente numéricas) |
| **SQLite 3 (sistema_seguro.db)** | `dados/sistema_seguro.db` | `APROVADO` | Modo Read-Only / Analítico Confinado | OK |
| **SQLite 3 (resultados_dissertacao.db)** | `dados/resultados_dissertacao.db` | `APROVADO` | Modo Read-Only / Analítico Confinado | OK |

## 2. Matriz de Ameaças Detectadas no Código e Sugestões de Correção

### 1. [HIGH] Algoritmo de Hashing Fraco / Depreciado (MD5 / SHA1)

- **Categoria:** `A02:2021 - Cryptographic Failures`
- **Localização:** `scripts/gerar_relatorio_pbs.py` (Linha 277)
- **Trecho do Código:**
```
hashes = {hashlib.md5(p.read_bytes()).hexdigest() for p in arquivos}
```
- **Diagnóstico de Ameaça:** Uso de funções hash vulneráveis a colisões para fins de segurança ou senhas.
- **💡 Correção e Melhoria Recomendada:**
> Para senhas, utilize exclusivamente Argon2id ou Bcrypt com salt. Para integridade geral de arquivos, prefira SHA-256 ou SHA-512.

### 2. [HIGH] Algoritmo de Hashing Fraco / Depreciado (MD5 / SHA1)

- **Categoria:** `A02:2021 - Cryptographic Failures`
- **Localização:** `scripts/rsl_prisma.py` (Linha 354)
- **Trecho do Código:**
```
md5 = hashlib.md5(path.read_bytes()).hexdigest()
```
- **Diagnóstico de Ameaça:** Uso de funções hash vulneráveis a colisões para fins de segurança ou senhas.
- **💡 Correção e Melhoria Recomendada:**
> Para senhas, utilize exclusivamente Argon2id ou Bcrypt com salt. Para integridade geral de arquivos, prefira SHA-256 ou SHA-512.

### 3. [HIGH] Algoritmo de Hashing Fraco / Depreciado (MD5 / SHA1)

- **Categoria:** `A02:2021 - Cryptographic Failures`
- **Localização:** `scripts/gerar_protocolo_e_relatorio_rsl.py` (Linha 40)
- **Trecho do Código:**
```
h = hashlib.md5()
```
- **Diagnóstico de Ameaça:** Uso de funções hash vulneráveis a colisões para fins de segurança ou senhas.
- **💡 Correção e Melhoria Recomendada:**
> Para senhas, utilize exclusivamente Argon2id ou Bcrypt com salt. Para integridade geral de arquivos, prefira SHA-256 ou SHA-512.


## 3. Práticas de Segurança em Vigor no Sistema (FROTAGOV)

1. **Política de Senhas Fortes:** Validação dupla (Frontend & Backend Pydantic v2) exigindo no mínimo 8 caracteres com letras maiúsculas, minúsculas, números e caracteres especiais (proibição absoluta de senhas puramente numéricas).
2. **Identificação por CPF:** Normalização e validação de formato e unicidade no banco de dados.
3. **Hashing Criptográfico:** Credenciais processadas com algoritmos resistentes a ataques de força bruta (Argon2id/Bcrypt).
4. **RBAC Granular:** Controle de acesso baseado em 5 papéis funcionais (`ADMIN`, `GESTOR_FROTA`, `OPERADOR`, `MOTORISTA`, `AUDITOR`).

## 4. Auditoria de Bibliotecas, Patches e Atualizações de Segurança (SCA)

| Biblioteca | Versão Instalada | Papel no Sistema | Status de Segurança |
| :--- | :---: | :--- | :---: |
| **`fastapi`** | `0.143.0` | Framework Web & Roteamento REST | `ATUALIZADO (SEGURO)` |
| **`starlette`** | `1.8.0` | Núcleo ASGI & Middleware | `ATUALIZADO (SEGURO)` |
| **`uvicorn`** | `0.54.0` | Servidor ASGI de Produção | `ATUALIZADO (SEGURO)` |
| **`pydantic`** | `2.14.1` | Validação de Schemas e Contratos de Dados | `ATUALIZADO (SEGURO)` |
| **`cryptography`** | `48.0.1` | Criptografia Simétrica AES-256-GCM e AEAD | `ATUALIZADO (SEGURO)` |
| **`argon2-cffi`** | `25.1.0` | Hashing de Senhas (Argon2id - Padrão Ouro) | `ATUALIZADO (SEGURO)` |
| **`bcrypt`** | `5.0.0` | Hashing Secundário com Salt | `ATUALIZADO (SEGURO)` |
| **`pyjwt`** | `2.15.1` | Emissão e Validação de Tokens JWT | `ATUALIZADO (SEGURO)` |
| **`httpx`** | `0.28.1` | Cliente HTTP Assíncrono para Telemetria | `ATUALIZADO (SEGURO)` |
| **`pymongo`** | `4.19.0` | Driver de Banco de Dados NoSQL | `ATUALIZADO (SEGURO)` |
| **`weasyprint`** | `70.0` | Motor de Compilação Segura de Relatórios PDF | `ATUALIZADO (SEGURO)` |
