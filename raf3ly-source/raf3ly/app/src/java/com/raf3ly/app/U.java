package com.raf3ly.app;

import android.content.Context;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.os.Build;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.HorizontalScrollView;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/** Design system: colors, shapes, typography, formatters. */
public class U {

    // surfaces
    public static final int BG = 0xFF0A0D13;
    public static final int CARD = 0xFF131926;
    public static final int CARD2 = 0xFF1A2231;
    public static final int CARD3 = 0xFF212B3C;
    public static final int STROKE = 0xFF2B3852;
    public static final int DIVIDER = 0xFF222D40;
    public static final int TEXT = 0xFFEDF2F9;
    public static final int SUB = 0xFFBCC7D8;
    public static final int MUTED = 0xFF98A5BA;
    public static final int FAINT = 0xFF74829A;
    public static final int SUCCESS = 0xFF22C55E;
    public static final int DANGER = 0xFFFF5C6C;
    public static final int WARN = 0xFFF5A524;
    public static final int STAR = 0xFFFFC53D;

    // dynamic accent (theme)
    public static int ACCENT = 0xFF7C5CFF;
    public static int ACCENT2 = 0xFF00D2FF;

    public static final String[] ACCENT_NAMES = {S.d(new int[]{235,2,162,5,244,237,188,252,4,95,153,101,228,221,109,6,19,201,186,99,235,192,206,108,81,168,189,184}), S.d(new int[]{67,20,41,130,251,200,196,120,91,255,230,92,149,174,208,40,27,99,161,228,109,68,113,60}), S.d(new int[]{5,52,31,205,59,41,26,134,153,61,201,4,13,217,5,11,77,182,212,185,237,95,156,221}), S.d(new int[]{72,33,100,98,21,31,65,136,160,51,133,254,206,201,41,55,116,149,186,3,175,174,254,82}), S.d(new int[]{26,248,229,247,187,210,119,148,159,31,49,27,140,18,168,242,189,63,172,178,216,93,58,94,98,210,54,168,28,179}), S.d(new int[]{33,186,184,234,100,150,8,17,8,113,159,135,79,183,242,245,66,48,196,86,68,200,59,229,120,96})};
    private static final int[][] ACCENTS = {
            {0xFF7C5CFF, 0xFF00D2FF},
            {0xFF3B82F6, 0xFF22D3EE},
            {0xFFEC4899, 0xFFF59E0B},
            {0xFF10B981, 0xFFA3E635},
            {0xFFF97316, 0xFFFF4D6D},
            {0xFF6366F1, 0xFF38BDF8}
    };

    public static void setAccent(int idx) {
        if (idx < 0 || idx >= ACCENTS.length) idx = 0;
        ACCENT = ACCENTS[idx][0];
        ACCENT2 = ACCENTS[idx][1];
    }

    public static int accentAt(int idx) {
        if (idx < 0 || idx >= ACCENTS.length) idx = 0;
        return ACCENTS[idx][0];
    }

    public static int accent2At(int idx) {
        if (idx < 0 || idx >= ACCENTS.length) idx = 0;
        return ACCENTS[idx][1];
    }

    public static int count() {
        return ACCENTS.length;
    }

    /** translucent version of a color (alpha 0..255). */
    public static int alpha(int color, int a) {
        return (color & 0x00FFFFFF) | (a << 24);
    }

    // ---------- metrics / shapes ----------

    public static int dp(Context c, float v) {
        return Math.round(v * c.getResources().getDisplayMetrics().density);
    }

    public static GradientDrawable round(int color, float radiusDp, Context c) {
        GradientDrawable d = new GradientDrawable();
        d.setShape(GradientDrawable.RECTANGLE);
        d.setColor(color);
        d.setCornerRadius(dp(c, radiusDp));
        return d;
    }

    public static GradientDrawable roundStroke(int color, float radiusDp, int strokeColor, float swDp, Context c) {
        GradientDrawable d = round(color, radiusDp, c);
        d.setStroke(Math.max(1, dp(c, swDp)), strokeColor);
        return d;
    }

    public static GradientDrawable grad(int a, int b, float radiusDp, Context c) {
        GradientDrawable d = new GradientDrawable(GradientDrawable.Orientation.TL_BR, new int[]{a, b});
        d.setCornerRadius(dp(c, radiusDp));
        return d;
    }

    public static GradientDrawable accentGrad(float radiusDp, Context c) {
        return grad(ACCENT, ACCENT2, radiusDp, c);
    }

    /** soft gradient surface used for hero cards. */
    public static GradientDrawable heroBg(Context c) {
        GradientDrawable d = new GradientDrawable(GradientDrawable.Orientation.TL_BR,
                new int[]{alpha(ACCENT, 0xFF), alpha(ACCENT2, 0xE0)});
        d.setCornerRadius(dp(c, 26));
        return d;
    }

    public static void pressable(View v) {
        if (Build.VERSION.SDK_INT >= 21) {
            Drawable bg = v.getBackground();
            if (bg != null) {
                v.setBackground(new RippleDrawable(ColorStateList.valueOf(0x33FFFFFF), bg, null));
            }
        }
    }

    // ---------- text ----------

    public static TextView tv(Context c, String s, float sizeSp, int color, boolean bold) {
        TextView t = new TextView(c);
        t.setTextSize(sizeSp);
        t.setTextColor(color);
        t.setText(I18n.t(s));
        t.setTextDirection(I18n.rtl() ? View.TEXT_DIRECTION_RTL : View.TEXT_DIRECTION_LTR);
        t.setIncludeFontPadding(false);
        t.setTypeface(Typeface.create(bold ? "sans-serif-medium" : "sans-serif",
                bold ? Typeface.BOLD : Typeface.NORMAL));
        return t;
    }

    /** secondary caption text */
    public static TextView cap(Context c, String s) {
        return tv(c, s, 11f, MUTED, false);
    }

    // ---------- layout ----------

    public static LinearLayout col(Context c) {
        LinearLayout l = new LinearLayout(c);
        l.setOrientation(LinearLayout.VERTICAL);
        return l;
    }

    public static LinearLayout row(Context c) {
        LinearLayout l = new LinearLayout(c);
        l.setOrientation(LinearLayout.HORIZONTAL);
        l.setGravity(Gravity.CENTER_VERTICAL);
        return l;
    }

    public static LinearLayout.LayoutParams lp(int w, int h) {
        return new LinearLayout.LayoutParams(w, h);
    }

    public static LinearLayout.LayoutParams lpw(int w, int h, float weight) {
        return new LinearLayout.LayoutParams(w, h, weight);
    }

    public static LinearLayout.LayoutParams match() {
        return new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT);
    }

    public static LinearLayout.LayoutParams matchH(int h) {
        return new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, h);
    }

    public static LinearLayout.LayoutParams wrap() {
        return new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT);
    }

    public static LinearLayout.LayoutParams margins(LinearLayout.LayoutParams p, Context c,
                                                    float l, float t, float r, float b) {
        p.setMargins(dp(c, l), dp(c, t), dp(c, r), dp(c, b));
        return p;
    }

    public static View spacer(Context c, int hDp) {
        View v = new View(c);
        v.setLayoutParams(lp(1, dp(c, hDp)));
        return v;
    }

    public static void pad(View v, Context c, float l, float t, float r, float b) {
        v.setPadding(dp(c, l), dp(c, t), dp(c, r), dp(c, b));
    }

    public static LinearLayout card(Context c) {
        LinearLayout box = col(c);
        box.setBackground(roundStroke(CARD, 20, STROKE, 1, c));
        pad(box, c, 16, 16, 16, 16);
        return box;
    }

    // ---------- components ----------

    /** Section heading with accent bar + optional trailing action. */
    public static LinearLayout sectionHead(Context c, String title, String action, View.OnClickListener cb) {
        LinearLayout row = row(c);
        View bar = new View(c);
        bar.setBackground(accentGrad(4, c));
        row.addView(bar, lp(dp(c, 3), dp(c, 15)));

        TextView t = tv(c, "  " + title, 14.5f, TEXT, true);
        row.addView(t, lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        if (action != null) {
            TextView a = tv(c, action, 11.5f, ACCENT2, true);
            pad(a, c, 8, 4, 0, 4);
            if (cb != null) {
                a.setOnClickListener(cb);
                pressable(a);
            }
            row.addView(a);
        }
        pad(row, c, 2, 0, 4, 10);
        return row;
    }

    public static TextView chip(Context c, String label, boolean active) {
        TextView t = tv(c, label, 12f, active ? 0xFFFFFFFF : SUB, true);
        t.setPadding(dp(c, 14), dp(c, 8), dp(c, 14), dp(c, 8));
        t.setBackground(active ? accentGrad(30, c) : roundStroke(CARD2, 30, STROKE, 1, c));
        return t;
    }

    public static TextView button(Context c, String label, boolean primary) {
        TextView t = tv(c, label, 13.5f, primary ? 0xFFFFFFFF : TEXT, true);
        t.setGravity(Gravity.CENTER);
        t.setPadding(dp(c, 16), dp(c, 13), dp(c, 16), dp(c, 13));
        t.setBackground(primary ? accentGrad(16, c) : roundStroke(CARD2, 16, STROKE, 1, c));
        pressable(t);
        return t;
    }

    public static TextView smallButton(Context c, String label, int color) {
        TextView t = tv(c, label, 11.5f, color, true);
        t.setPadding(dp(c, 12), dp(c, 7), dp(c, 12), dp(c, 7));
        t.setBackground(round(alpha(color, 0x22), 20, c));
        pressable(t);
        return t;
    }

    public static ImageView icon(Context c, int res, int tint, int sizeDp) {
        ImageView iv = new ImageView(c);
        iv.setImageResource(res);
        iv.setColorFilter(tint);
        iv.setScaleType(ImageView.ScaleType.FIT_CENTER);
        iv.setLayoutParams(lp(dp(c, sizeDp), dp(c, sizeDp)));
        return iv;
    }

    public static ImageView iconButton(Context c, int res, int tint) {
        ImageView iv = icon(c, res, tint, 18);
        int s = dp(c, 36);
        iv.setLayoutParams(lp(s, s));
        iv.setPadding(dp(c, 9), dp(c, 9), dp(c, 9), dp(c, 9));
        iv.setBackground(roundStroke(CARD2, 13, STROKE, 1, c));
        pressable(iv);
        return iv;
    }

    /** round icon badge with translucent accent background */
    public static LinearLayout iconBadge(Context c, int res, int tint, int boxDp, int iconDp) {
        LinearLayout b = col(c);
        b.setGravity(Gravity.CENTER);
        b.setLayoutParams(lp(dp(c, boxDp), dp(c, boxDp)));
        b.setBackground(round(alpha(tint, 0x22), 14, c));
        b.addView(icon(c, res, tint, iconDp), lp(dp(c, iconDp), dp(c, iconDp)));
        return b;
    }

    public static ProgressBar progress(Context c, int heightDp) {
        ProgressBar p = new ProgressBar(c, null, android.R.attr.progressBarStyleHorizontal);
        p.setMax(1000);
        p.setProgressDrawable(c.getResources().getDrawable(R.drawable.progress_horizontal, null));
        p.setLayoutParams(matchH(dp(c, heightDp)));
        return p;
    }

    public static View divider(Context c) {
        View v = new View(c);
        v.setBackgroundColor(DIVIDER);
        v.setLayoutParams(margins(matchH(1), c, 0, 10, 0, 10));
        return v;
    }

    public static HorizontalScrollView hscroll(Context c, View child) {
        HorizontalScrollView h = new HorizontalScrollView(c);
        h.setHorizontalScrollBarEnabled(false);
        h.setLayoutParams(match());
        h.addView(child, wrap());
        return h;
    }

    // ---------- formatters ----------

    public static String size(long b) {
        if (b < 0) return "—";
        if (b < 1024) return b + " B";
        double k = b / 1024.0;
        if (k < 1024) return String.format(Locale.US, "%.1f KB", k);
        double m = k / 1024.0;
        if (m < 1024) return String.format(Locale.US, "%.1f MB", m);
        return String.format(Locale.US, "%.2f GB", m / 1024.0);
    }

    public static String speed(long bps) {
        if (bps <= 0) return "0 KB/s";
        if (bps < 1024) return bps + " B/s";
        double k = bps / 1024.0;
        if (k < 1024) return String.format(Locale.US, "%.0f KB/s", k);
        return String.format(Locale.US, "%.1f MB/s", k / 1024.0);
    }

    public static String dur(long ms) {
        return I18n.dur(ms);
    }

    public static String date(long ts) {
        return new SimpleDateFormat("d MMM yyyy · h:mm a", Locale.getDefault()).format(new Date(ts));
    }

    public static String shortDate(long ts) {
        return new SimpleDateFormat("d MMM · h:mm a", Locale.getDefault()).format(new Date(ts));
    }

    public static String num(int n) {
        return String.format(Locale.US, "%,d", n);
    }

    public static String pct(long done, long total) {
        if (total <= 0) return "0%";
        return Math.min(100, (int) (done * 100 / total)) + "%";
    }

    public static String ago(long ts) {
        return I18n.ago(ts);
    }
}
