#!/usr/bin/env bash
# Grava a chave do OpenAlex e o e-mail de contato no .env, confere se a chave está ativa
# e (opcionalmente) dispara a busca diária de artigos. A chave nunca é exibida.
#
# Uso (um comando):
#   bash scripts/configurar_chaves_api.sh
#
# A chave pode vir de duas formas:
#   1. da área de transferência: copie a chave no navegador (Settings → API key) e só tecle Enter;
#   2. digitada/colada no terminal (Ctrl+Shift+V); nada aparece na tela enquanto você cola.
set -uo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV="$RAIZ/.env"
touch "$ENV"
chmod 600 "$ENV"   # só o seu usuário lê o arquivo

ler_area_transferencia() {
    if command -v wl-paste >/dev/null 2>&1; then wl-paste --no-newline 2>/dev/null && return; fi
    if command -v xclip >/dev/null 2>&1; then xclip -o -selection clipboard 2>/dev/null && return; fi
    if command -v xsel >/dev/null 2>&1; then xsel --clipboard --output 2>/dev/null && return; fi
    return 1
}

gravar() {   # gravar NOME VALOR: substitui a linha se existir, senão acrescenta
    local nome="$1" valor="$2" tmp
    tmp="$(mktemp)"
    grep -v "^${nome}=" "$ENV" > "$tmp" || true
    printf '%s=%s\n' "$nome" "$valor" >> "$tmp"
    cat "$tmp" > "$ENV"
    rm -f "$tmp"
}

echo "== Chave do OpenAlex =="
echo "Copie a chave em https://openalex.org/settings/api-key"
read -rsp "Tecle Enter para usar o que está copiado, ou cole a chave (Ctrl+Shift+V) e tecle Enter: " CHAVE
echo
if [ -z "$CHAVE" ]; then
    CHAVE="$(ler_area_transferencia || true)"
    [ -z "$CHAVE" ] && { echo "Área de transferência vazia ou inacessível. Rode de novo e cole a chave."; exit 1; }
    echo "Chave lida da área de transferência."
fi
CHAVE="$(printf '%s' "$CHAVE" | tr -d '[:space:]')"

# Recusa o que claramente não é a chave de API
case "$CHAVE" in
    *openalex.org*|*magic-token*|http*)
        echo "Isso é um link (provavelmente o link de login), não a chave de API."
        echo "Abra o link no navegador e copie a chave em Settings → API key."
        exit 1 ;;
esac
if [ "${#CHAVE}" -lt 16 ]; then
    echo "O texto tem só ${#CHAVE} caracteres; não parece uma chave. Nada foi gravado."
    exit 1
fi

read -rp "E-mail de contato (o mesmo da conta OpenAlex): " EMAIL
EMAIL="$(printf '%s' "$EMAIL" | tr -d '[:space:]')"
if ! printf '%s' "$EMAIL" | grep -Eq '^[^@ ]+@[^@ ]+\.[^@ ]+$'; then
    echo "E-mail inválido. Nada foi gravado."
    exit 1
fi

echo
echo "== Conferindo a chave no OpenAlex (a consulta /rate-limit não gasta cota) =="
RESP="$(mktemp)"
COD="$(curl -s -o "$RESP" -w '%{http_code}' -H "Authorization: Bearer $CHAVE" "https://api.openalex.org/rate-limit")"
case "$COD" in
    200)
        echo "Chave ativa."
        python3 - "$RESP" <<'EOF' 2>/dev/null || true
import json, sys
d = json.load(open(sys.argv[1]))
def busca(o, chaves):
    if isinstance(o, dict):
        for k, v in o.items():
            if any(c in k.lower() for c in chaves) and not isinstance(v, (dict, list)):
                print(f"   {k}: {v}")
            busca(v, chaves)
busca(d, ("budget", "remaining", "limit", "used"))
EOF
        ;;
    401|403)
        if grep -q "key_not_activated" "$RESP"; then
            echo "A chave existe, mas ainda não foi ativada: abra o link 'Activate your OpenAlex API key' no seu e-mail."
            echo "Ela será gravada mesmo assim e passará a funcionar depois da ativação."
        else
            echo "O OpenAlex recusou a chave (HTTP $COD). Confira se copiou a chave inteira. Nada foi gravado."
            rm -f "$RESP"; unset CHAVE; exit 1
        fi ;;
    *)
        echo "Não foi possível conferir agora (HTTP $COD). A chave será gravada; a busca vai dizer se funciona." ;;
esac
rm -f "$RESP"

gravar OPENALEX_API_KEY "$CHAVE"
gravar OPENALEX_EMAIL "$EMAIL"
gravar UNPAYWALL_EMAIL "$EMAIL"
unset CHAVE
echo
echo "Gravado em .env (permissão 600, fora do git):"
for v in OPENALEX_API_KEY OPENALEX_EMAIL UNPAYWALL_EMAIL S2_API_KEY; do
    grep -q "^${v}=." "$ENV" && echo "   $v: definida" || echo "   $v: não definida"
done
git -C "$RAIZ" check-ignore -q "$ENV" && echo "   .env está no .gitignore" || echo "   ATENÇÃO: .env NÃO está no .gitignore"

# Limpa a área de transferência para a chave não ficar lá
if command -v wl-copy >/dev/null 2>&1; then wl-copy --clear 2>/dev/null || true
elif command -v xclip >/dev/null 2>&1; then printf '' | xclip -selection clipboard 2>/dev/null || true; fi

echo
read -rp "Rodar a busca de artigos agora (limite de 10.000 textos)? [s/N] " R
if [[ "$R" =~ ^[sS] ]]; then
    systemctl --user start --no-block busca-artigos.service \
        && echo "Busca iniciada. Acompanhe com: tail -f \"$RAIZ/artigos/atualizacoes/logs/$(date +%F).log\""
fi
