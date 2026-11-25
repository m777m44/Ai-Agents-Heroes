package com.raf3ly.app;

import android.content.Context;
import android.content.SharedPreferences;

/** App settings. */
public class Prefs {
    private final SharedPreferences sp;

    public Prefs(Context c) {
        sp = c.getSharedPreferences("raf3ly", Context.MODE_PRIVATE);
    }

    /** x0 | uguu | tmpfiles */
    public String host() {
        return sp.getString("host", Hosts.CATBOX.id);
    }

    public void setHost(String h) {
        sp.edit().putString("host", h).apply();
    }

    public boolean autoCopy() {
        return sp.getBoolean("autocopy", true);
    }

    public void setAutoCopy(boolean v) {
        sp.edit().putBoolean("autocopy", v).apply();
    }

    public boolean haptics() {
        return sp.getBoolean("haptics", true);
    }

    public void setHaptics(boolean v) {
        sp.edit().putBoolean("haptics", v).apply();
    }

    public int accent() {
        return sp.getInt("accent", 0);
    }

    public void setAccent(int i) {
        sp.edit().putInt("accent", i).apply();
    }

    public boolean fallback() {
        return sp.getBoolean("fallback", true);
    }

    public void setFallback(boolean v) {
        sp.edit().putBoolean("fallback", v).apply();
    }

    public String sort() {
        return sp.getString("sort", "new");
    }

    public void setSort(String v) {
        sp.edit().putString("sort", v).apply();
    }

    // ---- custom platform ----
    public String customName() {
        return sp.getString("c_name", "");
    }

    public String customUrl() {
        return sp.getString("c_url", "");
    }

    public String customField() {
        return sp.getString("c_field", "file");
    }

    public void setCustom(String name, String url, String field) {
        sp.edit().putString("c_name", name).putString("c_url", url).putString("c_field", field).apply();
    }

    public void clearCustom() {
        sp.edit().remove("c_name").remove("c_url").remove("c_field").apply();
    }

    // ---- upload behaviour ----
    /** 0 = أصلي · 1 = ضغط عالي · 2 = ضغط متوسط */
    public int compression() {
        return sp.getInt("compress", 1);
    }

    public void setCompression(int v) {
        sp.edit().putInt("compress", v).apply();
    }

    public int parallel() {
        return sp.getInt("parallel", 1);
    }

    public void setParallel(int v) {
        sp.edit().putInt("parallel", v).apply();
    }

    public boolean welcomed() {
        return sp.getBoolean("welcomed", false);
    }

    public void setWelcomed(boolean v) {
        sp.edit().putBoolean("welcomed", v).apply();
    }

    public boolean keepHistory() {
        return sp.getBoolean("keep", true);
    }

    public void setKeepHistory(boolean v) {
        sp.edit().putBoolean("keep", v).apply();
    }
}
