#!/usr/bin/env bash
# Prints the lowercase SHA-256 of a keystore entry's certificate (same value apksigner shows).
set -e
KS=$1; ALIAS=$2; PASS=$3
export JAVA_HOME=/home/user/.cache/jdk17
TMP=$(mktemp -d)
"$JAVA_HOME/bin/keytool" -exportcert -keystore "$KS" -alias "$ALIAS" -storepass "$PASS" -file "$TMP/c.der" >/dev/null 2>&1
sha256sum "$TMP/c.der" | cut -d' ' -f1
rm -rf "$TMP"
