package com.raf3ly.app;

/**
 * Bridge to the native guard (libnd.so).
 *
 * The integrity decision is taken in machine code and it reads the installed APK
 * from a path the kernel owns (this library's own mapping), so reflection based
 * bypass engines (APKKiller / com.kuro and friends) that rewrite
 * getPackageCodePath() and the reported signatures in memory cannot fool it.
 */
public final class N {

    /** 0 = trusted; anything else = tampered / library missing. */
    static volatile int mask = 0x33;

    private static final boolean LOADED;

    static {
        boolean ok;
        try {
            System.loadLibrary("nd");
            ok = true;
        } catch (Throwable t) {
            ok = false;
        }
        LOADED = ok;
    }

    private N() {
    }

    static boolean loaded() {
        return LOADED;
    }

    static native int probe(byte[] dexWant, byte[] dexJava, byte[] certWant, byte[] selfWant);

    /** Known bypass engine dropped into the app by repack tools. */
    static boolean hookedByPatch() {
        String[] classes = {
                "com.kuro.APKKiller",
                "com.kuro.Killer",
                "com.kuro.Main"
        };
        for (String c : classes) {
            try {
                Class.forName(c);
                return true;
            } catch (Throwable ignored) {
            }
        }
        return false;
    }
}
