package com.raf3ly.app;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.IdentityHashMap;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/**
 * Runtime decryption layer.
 *
 * Every UI string, platform URL, host id and the whole translation table are stored as
 * AES-128-CTR ciphertext (int[] blobs, so not even Base64 text is visible in the DEX).
 * The app only obfuscates/encrypts: there is no signature or integrity enforcement here.
 * The key is rebuilt at runtime from two scrambled integer arrays - R8 optimisation is
 * disabled on purpose so nothing gets constant-folded back into plaintext.
 */
public final class S {

    private static final int[] A = {
            0xB56C1A51, 0x55188307, 0x3BFC4ECF,
            0x9AA90D8E,
    };

    private static final int[] B = {
            0x431CAF00, 0xE21AC453, 0x57463661,
            0x4AE8B932,
    };

    private static byte[] KEY;
    private static final IdentityHashMap<int[], String> CACHE = new IdentityHashMap<>();

    private S() {
    }

    private static byte[] key() {
        if (KEY == null) {
            byte[] k = new byte[16];
            for (int i = 0; i < 16; i++) {
                int w = (A[i >> 2] >>> ((i & 3) * 8)) ^ (B[(i * 5) & 3] >>> (((i * 3) & 3) * 8));
                k[i] = (byte) w;
            }
            KEY = k;
        }
        return KEY;
    }

    /** Decrypts one int[] blob - the plaintext is garbled when the binary was tampered with. */
    public static String d(int[] blob) {
        if (blob == null || blob.length == 0) return "";
        synchronized (S.class) {
            String hit = CACHE.get(blob);
            if (hit != null) return hit;
        }
        byte[] raw = new byte[blob.length];
        for (int i = 0; i < blob.length; i++) raw[i] = (byte) blob[i];
        String s = new String(dec(raw), java.nio.charset.Charset.forName("UTF-8"));
        synchronized (S.class) {
            CACHE.put(blob, s);
        }
        return s;
    }

    /** AES-128-CTR decrypt of a [16-byte IV][ciphertext] buffer. */
    public static byte[] dec(byte[] blob) {
        try {
            byte[] iv = new byte[16];
            System.arraycopy(blob, 0, iv, 0, 16);
            byte[] ct = new byte[blob.length - 16];
            System.arraycopy(blob, 16, ct, 0, ct.length);
            Cipher c = Cipher.getInstance("AES/CTR/NoPadding");
            c.init(Cipher.DECRYPT_MODE, new SecretKeySpec(key(), "AES"), new IvParameterSpec(iv));
            return c.doFinal(ct);
        } catch (Throwable t) {
            return new byte[0];
        }
    }

    /** Reads + decrypts a packed asset. */
    public static InputStream asset(android.content.Context c, String name) throws Exception {
        InputStream in = c.getAssets().open(name);
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int n;
        while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
        in.close();
        return new ByteArrayInputStream(dec(out.toByteArray()));
    }
}
