#!/usr/bin/env bash
# Signs Raf3ly with YOUR OWN key and keeps the anti-tamper guard in sync.
#   bash tools/setkey.sh <keystore-file> <key-alias> <store-password>
set -e
ROOT=/home/user/raf3ly
KS=$1; ALIAS=$2; PASS=$3
[ -f "$KS" ] || { echo "keystore not found: $KS"; exit 1; }
SHA=$(bash "$ROOT/tools/cert-sha256.sh" "$KS" "$ALIAS" "$PASS")
echo "cert SHA-256: $SHA"
cat > "$ROOT/signing.conf" <<EOF
KEYSTORE=$KS
ALIAS=$ALIAS
STOREPASS=$PASS
EOF
bash "$ROOT/build.sh"
