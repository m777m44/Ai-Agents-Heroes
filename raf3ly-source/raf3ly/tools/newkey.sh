#!/usr/bin/env bash
# Creates a brand new publication keystore (RSA 3072, 30 years) and signs with it.
#   bash tools/newkey.sh <out.keystore> <alias> <password> "<CN name>" [org] [country]
set -e
ROOT=/home/user/raf3ly
export JAVA_HOME=/home/user/.cache/jdk17
KS=$1; ALIAS=$2; PASS=$3; CN=$4; ORG=${5:-Raf3ly}; C=${6:-EG}
[ -f "$KS" ] && { echo "refusing to overwrite $KS"; exit 1; }
"$JAVA_HOME/bin/keytool" -genkeypair -v -keystore "$KS" -alias "$ALIAS" \
  -keyalg RSA -keysize 3072 -validity 10950 -storetype JKS \
  -storepass "$PASS" -keypass "$PASS" \
  -dname "CN=$CN, OU=Editor True, O=$ORG, L=Cairo, C=$C"
bash "$ROOT/tools/setkey.sh" "$KS" "$ALIAS" "$PASS"
