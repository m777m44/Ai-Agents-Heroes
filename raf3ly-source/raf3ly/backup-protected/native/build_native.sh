#!/usr/bin/env bash
# Cross-compiles the guard library for every shipped ABI (needs the cached NDK).
set -e
NDK=/home/user/.cache/android-ndk/android-ndk-r26d
BIN=$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin
SRC=/home/user/raf3ly/app/src/native/guard.c
OUT=/home/user/raf3ly/app/src/jniLibs
[ -d "$NDK" ] || { echo "NDK missing: $NDK"; exit 1; }
build() {
  "$BIN/$1" -shared -fPIC -O2 -Wl,--build-id=none -s -fvisibility=hidden -o "$OUT/$2/libnd.so" "$SRC"
  echo "built $2: $(stat -c%s "$OUT/$2/libnd.so") bytes"
}
build aarch64-linux-android21-clang arm64-v8a
build armv7a-linux-androideabi21-clang armeabi-v7a
build x86_64-linux-android21-clang x86_64
build i686-linux-android21-clang x86
