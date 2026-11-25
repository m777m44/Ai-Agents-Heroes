package com.raf3ly.app;

import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.os.Build;
import android.os.Debug;
import android.os.Process;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.InputStream;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

/**
 * Integrity guard.
 *
 * The app dies (SecurityException on a worker thread + killProcess) when:
 *   - the APK is re-signed with any certificate other than the release key
 *     (and, once set, the Play App Signing key),
 *   - a debugger is attached,
 *   - a hooking framework (Frida / Xposed / LSPosed) is present.
 *
 * The expected certificate digest is stored scrambled, so it is not readable with
 * "strings classes.dex" and cannot be swapped by a one-line patch.
 */
public final class Guard {

    private static final int K = 0x3F;

    /** SHA-256 of the release certificate, XOR-scrambled (K) char by char. */
    private static final char[] E = {
            0x000C, 0x000F, 0x005D, 0x005D, 0x005B, 0x0059, 0x0007, 0x005B, 0x000C, 0x0009, 0x005D, 0x005D,
            0x005E, 0x005E, 0x005E, 0x0059, 0x000F, 0x000E, 0x000A, 0x0007, 0x005B, 0x005A, 0x005D, 0x005B,
            0x000B, 0x005E, 0x0009, 0x000A, 0x005E, 0x005D, 0x005E, 0x0006, 0x000A, 0x000B, 0x0059, 0x000A,
            0x000C, 0x0059, 0x005B, 0x005C, 0x0007, 0x0006, 0x000F, 0x005C, 0x000D, 0x000F, 0x000D, 0x000C,
            0x005D, 0x005E, 0x005B, 0x0008, 0x0006, 0x005E, 0x000F, 0x000F, 0x000F, 0x000B, 0x0006, 0x0009,
            0x005C, 0x0008, 0x005C, 0x000D,
    };

    /**
     * SHA-256 of the Play App Signing certificate (scrambled the same way).
     * Empty = Play re-signed builds are refused. After the first upload to the
     * Play Console copy the digest from "App integrity" and fill it in here.
     */
    private static final char[] P = {
    };

    private static volatile boolean verified = false;
    private static volatile boolean intact = false;

    private Guard() {
    }

    private static String unscramble(char[] a) {
        char[] o = new char[a.length];
        for (int i = 0; i < a.length; i++) o[i] = (char) (a[i] ^ K);
        return new String(o);
    }

    public static void verify(Context ctx) {
        if (ctx == null) return;
        try {
            if (Debug.isDebuggerConnected() || Debug.waitingForDebugger()) {
                die();
                return;
            }
            if (hooked()) {
                die();
                return;
            }
            Context app = ctx.getApplicationContext();
            String[] hashes = certHashes(app);
            if (hashes == null || hashes.length != 1 || hashes[0] == null) {
                die();
                return;
            }
            String actual = hashes[0];
            boolean ok = actual.equals(unscramble(E));
            if (!ok) {
                String play = unscramble(P);
                ok = play.length() == 64 && actual.equals(play);
            }
            if (!ok) {
                die();
                return;
            }
            if (!codeIntact(app)) {
                die();
                return;
            }
            if (smuggledOriginal(app)) {
                die();
                return;
            }
            if (!nativeIntact(app, actual)) {
                die();
                return;
            }
            verified = true;
            intact = true;
        } catch (Throwable t) {
            // never let the guard be bypassed by breaking it
            die();
        }
    }

    /** Background re-check: a cracker that survives launch still gets caught later. */
    public static void watch(final Context ctx) {
        Thread t = new Thread(new Runnable() {
            @Override
            public void run() {
                java.util.Random r = new java.util.Random();
                while (true) {
                    try {
                        Thread.sleep(25000 + r.nextInt(20000));
                    } catch (InterruptedException ignored) {
                    }
                    try {
                        boolean ok = intact && N.mask == 0 && codeIntact(ctx);
                        if (ok) ok = nativeIntact(ctx, unscramble(E));
                        if (!ok) {
                            intact = false;
                            N.mask = 0x33;
                            die();
                            return;
                        }
                    } catch (Throwable t) {
                        intact = false;
                        die();
                        return;
                    }
                }
            }
        }, "w");
        t.setDaemon(true);
        t.start();
    }

    public static boolean isVerified() {
        return verified;
    }

    /** True only when the signature AND the byte code are exactly as shipped. */
    public static boolean intact() {
        return intact;
    }

    /** Cheap re-check used by screens / uploads: die if the process is no longer trusted. */
    public static void check() {
        if (!intact) die();
    }

    /**
     * Compares the SHA-256 of classes.dex inside the installed APK with the digest
     * that was recorded at build time (stored encrypted in assets/i.bin).
     * Any patched instruction changes the digest.
     */
    private static boolean codeIntact(Context ctx) {
        byte[] want = null;
        try {
            byte[] all = S.assetRaw(ctx, "i.bin");
            if (all != null && all.length >= 32) {
                want = new byte[32];
                System.arraycopy(all, 0, want, 0, 32);
            }
        } catch (Throwable t) {
            want = null;
        }
        byte[] got = dexDigest(ctx);
        if (want == null) {
            // assets missing/unreadable: fall back to the signature check only
            return true;
        }
        if (got == null) {
            // cannot read our own APK: do not brick the app, signature check already passed
            return true;
        }
        return Arrays.equals(want, got);
    }

    private static byte[] hexToBytes(String hex) {
        if (hex == null || hex.length() < 64) return null;
        byte[] out = new byte[32];
        for (int i = 0; i < 32; i++) {
            out[i] = (byte) Integer.parseInt(hex.substring(i * 2, i * 2 + 2), 16);
        }
        return out;
    }

    /**
     * Hands every digest to libnd.so. The native code compares them with the APK
     * it reads itself from the kernel-owned install path; Java only obeys.
     */
    private static boolean nativeIntact(Context ctx, String certHex) {
        if (!N.loaded()) return false;
        if (N.hookedByPatch()) return false;
        byte[] want = null, selfTable = null;
        try {
            byte[] all = S.assetRaw(ctx, "i.bin");
            if (all != null && all.length >= 160) {
                want = new byte[32];
                System.arraycopy(all, 0, want, 0, 32);
                selfTable = new byte[128];
                System.arraycopy(all, 32, selfTable, 0, 128);
            }
        } catch (Throwable ignored) {
        }
        byte[] certWant = hexToBytes(certHex);
        byte[] certGot = null;
        String[] hashes = certHashes(ctx);
        if (hashes != null && hashes.length == 1) certGot = hexToBytes(hashes[0]);
        byte[] dexGot = dexDigest(ctx);
        int m;
        try {
            m = N.probe(want, dexGot, certWant, selfTable);
        } catch (Throwable t) {
            m = 0x44;
        }
        N.mask = m;
        return m == 0;
    }

    /**
     * APKKiller drops the untouched original APK into the patched package
     * (assets/original.apk) and redirects the app to it. Presence = tampered.
     */
    private static boolean smuggledOriginal(Context ctx) {
        try {
            String[] assets = ctx.getAssets().list("");
            if (assets != null) {
                for (String a : assets) {
                    String n = a.toLowerCase(java.util.Locale.US);
                    if (n.endsWith(".apk")) return true;
                }
            }
        } catch (Throwable ignored) {
        }
        try {
            java.io.File cache = ctx.getCacheDir();
            if (cache != null) {
                java.io.File[] files = cache.listFiles();
                if (files != null) {
                    for (java.io.File f : files) {
                        if (f.getName().toLowerCase(java.util.Locale.US).endsWith(".apk")) return true;
                    }
                }
            }
        } catch (Throwable ignored) {
        }
        return false;
    }

    private static byte[] dexDigest(Context ctx) {
        ZipFile zip = null;
        try {
            zip = new ZipFile(ctx.getPackageCodePath());
            ZipEntry e = zip.getEntry("classes.dex");
            if (e == null) return null;
            InputStream in = zip.getInputStream(e);
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] buf = new byte[16384];
            int n;
            while ((n = in.read(buf)) > 0) md.update(buf, 0, n);
            in.close();
            return md.digest();
        } catch (Throwable t) {
            return null;
        } finally {
            try {
                if (zip != null) zip.close();
            } catch (Throwable ignored) {
            }
        }
    }

    /** ptrace / tracer detection (returns true when a tracer is attached). */
    private static boolean traced() {
        BufferedReader r = null;
        try {
            r = new BufferedReader(new FileReader("/proc/self/status"));
            String line;
            while ((line = r.readLine()) != null) {
                if (line.startsWith("TracerPid:")) {
                    String v = line.substring(10).trim();
                    return !v.isEmpty() && !"0".equals(v);
                }
            }
        } catch (Throwable ignored) {
        } finally {
            try {
                if (r != null) r.close();
            } catch (Throwable ignored) {
            }
        }
        return false;
    }

    /** Cheap Frida / Xposed / LSPosed detection. */
    private static boolean hooked() {
        if (traced()) return true;
        String[] pkgs = {
                "de.robv.android.xposed.XposedBridge",
                "de.robv.android.xposed.XC_MethodHook",
                "org.lsposed.lspd.core.Main",
                "com.saurik.substrate.MS"
        };
        for (String p : pkgs) {
            try {
                Class.forName(p);
                return true;
            } catch (Throwable ignored) {
            }
        }
        BufferedReader r = null;
        try {
            r = new BufferedReader(new FileReader("/proc/self/maps"));
            String line;
            while ((line = r.readLine()) != null) {
                if (line.contains("frida") || line.contains("gum-js-loop")
                        || line.contains("xposed") || line.contains("lspd")) {
                    return true;
                }
            }
        } catch (Throwable ignored) {
        } finally {
            try {
                if (r != null) r.close();
            } catch (Throwable ignored) {
            }
        }
        return false;
    }

    private static String[] certHashes(Context ctx) {
        try {
            PackageManager pm = ctx.getPackageManager();
            String pkg = ctx.getPackageName();
            if (Build.VERSION.SDK_INT >= 28) {
                PackageInfo info = pm.getPackageInfo(pkg, PackageManager.GET_SIGNING_CERTIFICATES);
                if (info.signingInfo == null) return null;
                Signature[] sigs;
                if (info.signingInfo.hasMultipleSigners()) {
                    sigs = info.signingInfo.getApkContentsSigners();
                } else {
                    sigs = info.signingInfo.getSigningCertificateHistory();
                }
                return digest(sigs);
            } else {
                PackageInfo info = pm.getPackageInfo(pkg, PackageManager.GET_SIGNATURES);
                return digest(info.signatures);
            }
        } catch (Throwable t) {
            return null;
        }
    }

    private static String[] digest(Signature[] sigs) {
        if (sigs == null || sigs.length == 0) return null;
        String[] out = new String[sigs.length];
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            for (int i = 0; i < sigs.length; i++) {
                md.reset();
                byte[] h = md.digest(sigs[i].toByteArray());
                StringBuilder sb = new StringBuilder();
                for (byte b : h) sb.append(String.format("%02x", b));
                out[i] = sb.toString();
            }
            return out;
        } catch (Throwable t) {
            return null;
        }
    }

    /** Kill the process and raise a visible crash. */
    private static void die() {
        intact = false;
        verified = false;
        try {
            Thread t = new Thread(new Runnable() {
                @Override
                public void run() {
                    throw new SecurityException("Raf3ly: integrity check failed");
                }
            }, "guard");
            t.start();
        } catch (Throwable ignored) {
        }
        try {
            Process.killProcess(Process.myPid());
        } catch (Throwable ignored) {
        }
        System.exit(9);
    }
}
