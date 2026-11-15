#!/usr/bin/env bash
# Instala (ou remove) o agendamento diário da busca de artigos como timer systemd do usuário.
#
#   bash scripts/instalar_agendamento_diario.sh            # instala, horário padrão 08:00
#   HORA=07:30 bash scripts/instalar_agendamento_diario.sh  # outro horário
#   bash scripts/instalar_agendamento_diario.sh --remover   # desinstala
#
# Persistent=true: se o computador estiver desligado no horário, a busca roda
# assim que você ligar e entrar na sessão.

set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIDADES="$HOME/.config/systemd/user"
NOME="busca-artigos"

if [[ "${1:-}" == "--remover" ]]; then
    systemctl --user disable --now "$NOME.timer" 2>/dev/null || true
    rm -f "$UNIDADES/$NOME.service" "$UNIDADES/$NOME.timer"
    systemctl --user daemon-reload
    echo "Agendamento removido."
    exit 0
fi

HORA="${HORA:-08:00}"
mkdir -p "$UNIDADES"
chmod +x "$RAIZ/scripts/atualizacao_diaria_artigos.sh"

cat > "$UNIDADES/$NOME.service" <<EOF
[Unit]
Description=Busca diária de artigos (XAI, analítica e setor público)
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
ExecStart=/bin/bash "$RAIZ/scripts/atualizacao_diaria_artigos.sh"
Nice=10
EOF

cat > "$UNIDADES/$NOME.timer" <<EOF
[Unit]
Description=Agenda diária da busca de artigos

[Timer]
OnCalendar=*-*-* $HORA:00
Persistent=true
RandomizedDelaySec=10min

[Install]
WantedBy=timers.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now "$NOME.timer"
echo "Agendamento instalado: todos os dias às $HORA."
systemctl --user list-timers "$NOME.timer" --no-pager
