package com.raf3ly.app;

import android.content.Context;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Locale;

/**
 * Tiny runtime translation layer.
 * Arabic sources stay inline in the code; on non-Arabic devices every visible string
 * is translated using assets/i18n_en.txt (exact sentences first, then phrase rules).
 */
public class I18n {

    private static boolean en = false;
    private static boolean loaded = false;
    private static final HashMap<String, String> EXACT = new HashMap<>();
    private static final ArrayList<String[]> PHRASES = new ArrayList<>();

    public static void init(Context c) {
        String lang = Locale.getDefault().getLanguage();
        en = !"ar".equals(lang);
        if (!en || loaded) return;
        loaded = true;
        try {
            load(S.asset(c, "d.bin"));
        } catch (Throwable ignored) {
        }
    }

    /** Package-visible so the build can smoke-test the table on a desktop JVM. */
    static void load(java.io.InputStream in) {
        try {
            BufferedReader r = new BufferedReader(new InputStreamReader(in, "UTF-8"));
            String line;
            while ((line = r.readLine()) != null) {
                if (line.isEmpty() || line.startsWith("#")) continue;
                int tab = line.indexOf('\t');
                if (tab <= 0) continue;
                String left = line.substring(0, tab);
                String right = unescape(line.substring(tab + 1));
                if (left.startsWith("~")) {
                    PHRASES.add(new String[]{unescape(left.substring(1)), right});
                } else {
                    EXACT.put(unescape(left), right);
                }
            }
            r.close();
        } catch (Throwable ignored) {
        }
        Collections.sort(PHRASES, new Comparator<String[]>() {
            @Override
            public int compare(String[] a, String[] b) {
                return b[0].length() - a[0].length();
            }
        });
    }

    public static boolean english() {
        return en;
    }

    public static boolean rtl() {
        return !en;
    }

    private static String unescape(String s) {
        return s.replace("\\n", "\n").replace("\\t", "\t");
    }

    /** Translates a whole string (exact sentence first, then phrase replacements). */
    public static String t(String s) {
        if (!en || s == null || s.isEmpty()) return s;
        String exact = EXACT.get(s);
        if (exact != null) return exact;
        String out = s;
        for (String[] p : PHRASES) {
            if (out.contains(p[0])) out = out.replace(p[0], p[1]);
        }
        // all-or-nothing: never show a half-Arabic / half-English soup
        return hasArabic(out) ? s : out;
    }

    private static boolean hasArabic(String s) {
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c >= 0x0600 && c <= 0x06FF) return true;
        }
        return false;
    }

    /** Locale-aware short duration (12s / 3m / 2h). */
    public static String dur(long ms) {
        if (ms < 0) return "—";
        if (ms > 3500000L) return en ? "over an hour" : S.d(new int[]{211,16,150,59,136,176,245,23,129,80,47,168,35,247,45,19,188,34,0,37,175,24,243,63,62,157,226,43,81,89,118,15,204,54,163,115,45,1});
        long s = ms / 1000;
        if (s < 60) return s + (en ? "s" : S.d(new int[]{173,217,182,122,251,173,232,173,236,155,114,64,252,187,73,184,117,222}));
        long m = s / 60;
        if (m < 60) return m + (en ? "m " : S.d(new int[]{135,157,39,237,251,190,216,45,227,242,107,187,61,9,89,244,197,107,14})) + (s % 60) + (en ? "s" : S.d(new int[]{232,206,66,220,12,219,41,152,68,219,74,59,45,168,129,20,169,168}));
        return (m / 60) + (en ? "h " : S.d(new int[]{6,160,226,11,1,78,214,116,164,57,79,186,75,95,4,81,169,153,5})) + (m % 60) + (en ? "m" : S.d(new int[]{223,4,43,15,82,196,62,172,207,161,91,213,74,191,212,230,169,41}));
    }

    /** Relative time (now / 5 min ago / yesterday). */
    public static String ago(long ts) {
        long d = System.currentTimeMillis() - ts;
        if (d < 60000) return en ? "just now" : S.d(new int[]{28,68,80,225,196,255,159,51,168,95,46,231,118,162,143,174,17,180,18,57,47,114,58,44});
        if (d < 3600000) return en ? (d / 60000) + " min ago" : S.d(new int[]{159,99,139,166,36,119,216,99,178,169,174,234,151,141,97,36,220,248,243,228,120,34,232}) + (d / 60000) + S.d(new int[]{123,51,139,179,142,179,51,244,65,228,162,15,149,111,248,64,152,144,56,241,246,176,38,66,44,128,240});
        if (d < 86400000) return en ? (d / 3600000) + " hr ago" : S.d(new int[]{214,4,255,36,156,162,103,57,42,101,42,38,141,180,2,98,183,166,181,140,3,77,66}) + (d / 3600000) + S.d(new int[]{165,248,6,161,227,10,44,154,15,157,254,52,141,251,222,201,129,247,196,87,25,199,212,29,160});
        if (d < 604800000) return en ? (d / 86400000) + " days ago" : S.d(new int[]{146,232,240,18,65,60,248,178,232,162,115,248,116,91,65,196,155,55,250,139,4,138,62}) + (d / 86400000) + S.d(new int[]{240,110,227,37,44,190,193,87,155,45,8,53,14,7,7,224,228,134,86,87,75,35,77});
        return new java.text.SimpleDateFormat("d MMM yyyy", Locale.getDefault()).format(new java.util.Date(ts));
    }
}
