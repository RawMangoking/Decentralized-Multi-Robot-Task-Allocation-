#!/bin/bash
set -e

ALL_PEERS=("fleet-manager-0" "fleet-manager-1" "fleet-manager-2")
SELF_ADDR="${HOSTNAME}.fleet-manager:4321"

PARTNERS=""
for peer in "${ALL_PEERS[@]}"; do
    if [ "$peer" != "$HOSTNAME" ]; then
        if [ -z "$PARTNERS" ]; then
            PARTNERS="${peer}.fleet-manager:4321"
        else
            PARTNERS="${PARTNERS},${peer}.fleet-manager:4321"
        fi
    fi
done

echo "Starting as $SELF_ADDR with partners $PARTNERS"
exec ros2 run swarm_agent fleet_manager "$SELF_ADDR" "$PARTNERS"
