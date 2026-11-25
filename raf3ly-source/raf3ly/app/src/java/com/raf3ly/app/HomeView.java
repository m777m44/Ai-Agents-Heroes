package com.raf3ly.app;

import android.content.Context;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.ArrayList;

/** Tab 0: dashboard — overview, quick actions, sparkline, recent files, platforms. */
public class HomeView {

    public final ScrollView root;
    private final MainActivity act;
    private final LinearLayout box;

    public HomeView(MainActivity a) {
        act = a;
        Context c = a;
        root = new ScrollView(c);
        root.setBackgroundColor(U.BG);
        root.setFillViewport(true);
        box = U.col(c);
        U.pad(box, c, 16, 6, 16, 26);
        root.addView(box, U.match());
        refresh();
    }

    public void refresh() {
        box.removeAllViews();
        Context c = act;

        box.addView(hero(c));
        box.addView(U.spacer(c, 16));
        box.addView(quickActions(c));
        box.addView(U.spacer(c, 20));

        box.addView(U.sectionHead(c, S.d(new int[]{150,76,183,160,187,62,10,145,23,215,162,210,141,137,132,104,10,160,82,198,130,158,224,196,14,41,95,25,1,206,61,74,106,111,233,49,218,71,131,168,4,30,186,4,144,231,55,6,84,56}), null, null));
        box.addView(chartCard(c));
        box.addView(U.spacer(c, 18));

        ArrayList<Entry> all = act.store.sorted("new");
        box.addView(U.sectionHead(c, S.d(new int[]{114,230,103,32,103,250,24,43,28,134,207,75,13,134,215,73,51,92,134,75,21,200,51,240,26,183,224,101,24,6,104,26,201,118,190,217,215}), all.isEmpty() ? null : S.d(new int[]{35,89,48,196,254,158,221,137,156,9,1,216,51,187,99,98,166,61,37,209,80,109,1,222}), new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.setTab(2);
            }
        }));
        box.addView(recentCard(c, all));
        box.addView(U.spacer(c, 18));

        box.addView(U.sectionHead(c, S.d(new int[]{209,181,89,123,24,203,136,84,53,213,79,121,17,4,185,118,68,114,71,247,79,59,113,211,31,178,26,34,154,153,191,196,222,29,131,44,207}), null, null));
        box.addView(platforms(c));
        box.addView(U.spacer(c, 16));
        box.addView(tip(c));
        box.addView(U.spacer(c, 14));
        box.addView(credits(c));
    }

    private View credits(Context c) {
        LinearLayout row = U.row(c);
        row.setGravity(Gravity.CENTER);
        U.pad(row, c, 0, 4, 0, 4);

        TextView t = U.tv(c, S.d(new int[]{14,23,201,228,178,68,78,150,243,198,211,189,108,168,168,178,99,164,182,199,185,252,186,82,100,125,139}) + Brand.DEV + " · @" + Brand.HANDLE, 10.5f, U.MUTED, true);
        t.setTextDirection(View.TEXT_DIRECTION_RTL);
        row.addView(t);

        TextView tg = U.tv(c, S.d(new int[]{12,23,189,48,247,169,174,172,43,160,130,164,192,41,33,150,165,80,128,250,34,198,12,213,239,18,8,25,249,0,163,155,137,22,245,68,226,5}), 10.5f, U.ACCENT2, true);
        tg.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.openTelegram();
            }
        });
        row.addView(tg);

        TextView yt = U.tv(c, S.d(new int[]{127,191,66,71,224,10,46,100,205,33,199,241,85,109,70,76,114,19,244,164,79,68,102,118,158,216,32,16,210,78,4,200,251,144}), 10.5f, U.ACCENT2, true);
        yt.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.openYoutube();
            }
        });
        row.addView(yt);
        return row;
    }

    // ---------------- hero ----------------

    private View hero(Context c) {
        LinearLayout hero = U.col(c);
        hero.setBackground(U.heroBg(c));
        U.pad(hero, c, 17, 16, 17, 15);

        LinearLayout top = U.row(c);
        TextView hi = U.tv(c, S.d(new int[]{244,187,133,99,125,103,17,17,236,231,40,95,15,56,223,212,79,137,205,96,142,85,98,89,25,37,124,48,225,148,39,47,10,1,8,192,90,217}), 13, 0xFFFFFFFF, true);
        top.addView(hi, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        TextView badge = U.tv(c, S.d(new int[]{109,32,101,232,1,162,78,217,83,84,235,229,231,18,167,196,111,196,16,97,72,164,217,25,22,77,43,164,21,143,231,93,83}), 9.5f, 0xFFFFFFFF, true);
        badge.setBackground(U.round(0x38FFFFFF, 20, c));
        U.pad(badge, c, 9, 4, 9, 4);
        top.addView(badge);
        hero.addView(top);

        LinearLayout big = U.row(c);
        U.pad(big, c, 0, 14, 0, 0);
        TextView files = U.tv(c, String.valueOf(act.store.count()), 36, 0xFFFFFFFF, true);
        big.addView(files);

        LinearLayout unitCol = U.col(c);
        LinearLayout.LayoutParams uclp = U.wrap();
        uclp.setMargins(U.dp(c, 11), 0, 0, 0);
        unitCol.addView(U.tv(c, S.d(new int[]{253,237,76,176,225,172,41,47,178,22,34,145,7,14,134,76,203,203,157,213,6,127,132,95,58,247,190,172,136,53,115,118,125}), 12, 0xFFFFFFFF, true));
        TextView tot = U.tv(c, S.d(new int[]{58,239,137,44,67,178,82,8,44,144,83,222,210,211,120,234,156,57,61,53,129,207,69,158,244,151,12,88,216}) + U.size(act.store.bytes()), 10.5f, 0xCCFFFFFF, false);
        U.pad(tot, c, 0, 3, 0, 0);
        unitCol.addView(tot);
        big.addView(unitCol, uclp);
        hero.addView(big);

        LinearLayout metrics = U.row(c);
        U.pad(metrics, c, 0, 15, 0, 0);
        metrics.addView(metric(c, R.drawable.ic_dl, String.valueOf(act.store.downloads()), S.d(new int[]{133,170,98,19,198,126,152,210,111,122,124,221,133,219,44,36,86,163,73,156,197,155,202,32,52,233})),
                U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        metrics.addView(metricDivider(c));
        metrics.addView(metric(c, R.drawable.ic_star, String.valueOf(act.store.favCount()), S.d(new int[]{186,81,228,160,213,105,134,35,80,23,63,23,72,106,10,89,93,181,0,94,193,67,66,22,102,220})),
                U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        metrics.addView(metricDivider(c));
        metrics.addView(metric(c, R.drawable.ic_bolt, U.size(act.store.bytesToday()), S.d(new int[]{211,207,253,128,229,134,173,168,107,101,108,25,217,57,134,67,115,112,223,184,58,128,96,3,221,163})),
                U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        hero.addView(metrics);
        return hero;
    }

    private View metric(Context c, int icon, String value, String label) {
        LinearLayout row = U.col(c);
        row.setGravity(Gravity.CENTER);

        LinearLayout top = U.row(c);
        top.setGravity(Gravity.CENTER);
        top.addView(U.icon(c, icon, 0xFFFFFFFF, 12));
        TextView v = U.tv(c, " " + value, 13, 0xFFFFFFFF, true);
        top.addView(v);
        row.addView(top);

        TextView l = U.tv(c, label, 9.5f, 0xD9FFFFFF, false);
        U.pad(l, c, 0, 4, 0, 0);
        row.addView(l);
        return row;
    }

    private View metricDivider(Context c) {
        View v = new View(c);
        v.setBackgroundColor(0x44FFFFFF);
        v.setLayoutParams(U.lp(1, U.dp(c, 28)));
        return v;
    }

    // ---------------- quick actions ----------------

    private View quickActions(Context c) {
        LinearLayout row = U.row(c);

        row.addView(actionCard(c, R.drawable.ic_up, S.d(new int[]{113,179,208,31,45,149,240,103,251,46,154,214,9,220,240,222,86,163,55,126,253,31,81,99,203,225,138,35,233,126,111,206,145}), S.d(new int[]{190,104,130,112,93,78,174,137,167,198,99,255,92,79,198,200,194,243,188,208,96,49,248,134,13,230,200,36,236,172,5,81,168,159,182}), new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.pickFiles();
            }
        }), U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        LinearLayout.LayoutParams p2 = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        p2.setMargins(U.dp(c, 10), 0, U.dp(c, 10), 0);
        row.addView(actionCard(c, R.drawable.ic_img, S.d(new int[]{38,230,64,204,151,27,183,109,155,40,181,181,6,163,65,142,140,113,2,16,142,139,146,44,52,76,61,245,216}), S.d(new int[]{116,132,81,96,224,88,155,115,156,121,37,26,239,14,196,10,44,66,71,52,242,124,186,95,2,7,141,192,185}), new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.pickImages();
            }
        }), p2);

        row.addView(actionCard(c, R.drawable.ic_camera, S.d(new int[]{155,52,66,123,162,252,59,125,238,94,18,65,208,119,160,236,5,110,73,19,219,109,181,239,185,32,78,2}), S.d(new int[]{254,145,228,251,15,77,139,2,84,152,75,113,99,14,121,220,146,166,238,200,63,174,157,33,249,192,57,59,91,90,94,213,143}), new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.takePhoto();
            }
        }), U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        return row;
    }

    private View actionCard(Context c, int icon, String title, String sub, View.OnClickListener cb) {
        LinearLayout card = U.col(c);
        card.setBackground(U.roundStroke(U.CARD, 18, U.STROKE, 1, c));
        U.pad(card, c, 8, 15, 8, 13);
        card.setGravity(Gravity.CENTER);

        card.addView(U.iconBadge(c, icon, U.ACCENT2, 44, 21));

        TextView t = U.tv(c, title, 12.5f, U.TEXT, true);
        t.setGravity(Gravity.CENTER);
        U.pad(t, c, 0, 10, 0, 0);
        card.addView(t);

        TextView s = U.tv(c, sub, 9.5f, U.MUTED, false);
        s.setGravity(Gravity.CENTER);
        U.pad(s, c, 0, 3, 0, 0);
        card.addView(s);
        card.setOnClickListener(cb);
        U.pressable(card);
        return card;
    }

    // ---------------- chart ----------------

    private View chartCard(Context c) {
        LinearLayout card = U.card(c);
        int[] data = act.store.last7();
        int max = 1, total = 0;
        for (int v : data) {
            max = Math.max(max, v);
            total += v;
        }

        LinearLayout head = U.row(c);
        head.addView(U.tv(c, String.valueOf(total), 20, U.TEXT, true));
        TextView unit = U.tv(c, S.d(new int[]{225,20,227,155,213,23,152,110,123,92,94,125,223,255,60,240,104,248,88,242,88,37,88,86,98,177,44,154,195,61,163,4,141,60,242,240,95,188,20,177,32,148,149}), 11, U.MUTED, false);
        U.pad(unit, c, 6, 4, 0, 0);
        head.addView(unit, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        head.addView(U.tv(c, S.d(new int[]{89,153,81,48,253,46,1,113,191,7,101,109,9,212,188,20,175,125,189,135,214,231,128,52,13}) + max, 10.5f, U.MUTED, false));
        card.addView(head);

        if (total == 0) {
            LinearLayout empty = U.col(c);
            empty.setGravity(Gravity.CENTER);
            U.pad(empty, c, 0, 16, 0, 12);
            empty.addView(U.icon(c, R.drawable.ic_chart, U.alpha(U.ACCENT2, 0x66), 30));
            TextView t = U.tv(c, S.d(new int[]{121,221,9,143,54,250,23,142,201,207,15,7,32,52,3,119,133,87,142,65,166,127,26,198,88,91,32,175,32,208,126,34,140,66,52,203,241,18,59,219,12,65,109,4,139,209,69,144,90,68,47,99,149,173,207,206,196,51,54,244,147,190,125,65,44,26,193,151,229,30,11,238,177,187,36,71}), 11.5f, U.MUTED, false);
            t.setGravity(Gravity.CENTER);
            U.pad(t, c, 0, 9, 0, 0);
            empty.addView(t);
            card.addView(empty);
            return card;
        }

        LinearLayout bars = U.row(c);
        bars.setGravity(Gravity.BOTTOM);
        LinearLayout.LayoutParams blp = U.matchH(U.dp(c, 96));
        blp.setMargins(0, U.dp(c, 14), 0, 0);
        card.addView(bars, blp);

        String[] labels = {S.d(new int[]{167,95,134,66,239,54,89,139,167,114,45,185,87,193,222,188,207,54,68,102}), S.d(new int[]{251,220,22,70,135,127,193,24,182,90,65,39,168,15,201,104,224,183,189,214}), S.d(new int[]{173,198,3,33,16,219,239,236,16,104,198,126,12,254,241,162,151,24,181,226}), S.d(new int[]{138,242,159,242,107,87,5,180,1,190,129,125,57,236,193,61,224,213,55,102}), S.d(new int[]{232,188,129,91,130,171,245,236,54,10,55,217,204,167,70,62,40,157,183,235}), S.d(new int[]{134,211,9,31,11,249,236,52,21,232,146,5,136,193,131,63,223,36,52,171,164,134}), S.d(new int[]{122,186,236,45,235,166,148,29,148,49,179,178,85,115,71,115,249,79,20,174,229,53,253,156,106,227})};
        for (int i = 0; i < 7; i++) {
            LinearLayout col = U.col(c);
            col.setGravity(Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);

            TextView v = U.tv(c, data[i] > 0 ? String.valueOf(data[i]) : "", 9, U.SUB, true);
            col.addView(v);

            View bar = new View(c);
            int h = Math.max(U.dp(c, 7), (int) (U.dp(c, 62) * data[i] / (float) max));
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(U.dp(c, 18), h);
            lp.setMargins(0, U.dp(c, 5), 0, U.dp(c, 6));
            bar.setLayoutParams(lp);
            bar.setBackground(i == 6 ? U.accentGrad(7, c) : U.round(U.CARD3, 7, c));
            col.addView(bar);

            TextView lab = U.tv(c, labels[i], 9, i == 6 ? U.ACCENT2 : U.MUTED, i == 6);
            lab.setGravity(Gravity.CENTER);
            col.addView(lab);

            bars.addView(col, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        }
        return card;
    }

    // ---------------- recent ----------------

    private View recentCard(Context c, ArrayList<Entry> all) {
        LinearLayout card = U.card(c);
        if (all.isEmpty()) {
            LinearLayout empty = U.col(c);
            empty.setGravity(Gravity.CENTER);
            U.pad(empty, c, 0, 12, 0, 12);
            empty.addView(U.icon(c, R.drawable.ic_up, U.alpha(U.ACCENT2, 0x77), 32));
            TextView t = U.tv(c, S.d(new int[]{136,100,239,180,72,15,5,244,138,255,146,6,141,218,159,106,99,70,210,57,56,211,167,194,27,167,48,81,231,232,87,171,115,172,228,231,187,75,114,13,130,144,193,106,77,120,51,148,42,212,112,182,152,15,132,44,154,201,24,103,32,219,119,197,228,62,29,159,54,247,209,17,85,241,226,146,245,154,98,230,65,30,175,1,41,101,14,184,231,185}), 11.5f, U.MUTED, false);
            t.setGravity(Gravity.CENTER);
            U.pad(t, c, 0, 9, 0, 0);
            empty.addView(t);
            card.addView(empty);
            return card;
        }
        for (int i = 0; i < Math.min(3, all.size()); i++) {
            final Entry e = all.get(i);
            if (i > 0) card.addView(U.divider(c));
            LinearLayout row = U.row(c);

            LinearLayout badge = U.col(c);
            badge.setGravity(Gravity.CENTER);
            badge.setBackground(U.round(U.alpha(e.isImage() ? U.ACCENT2 : U.ACCENT, 0x26), 13, c));
            badge.setLayoutParams(U.lp(U.dp(c, 42), U.dp(c, 42)));
            badge.addView(U.icon(c, e.isImage() ? R.drawable.ic_img : R.drawable.ic_file,
                    e.isImage() ? U.ACCENT2 : 0xFFA78BFA, 19));
            row.addView(badge);

            LinearLayout texts = U.col(c);
            LinearLayout.LayoutParams tlp = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
            tlp.setMargins(U.dp(c, 11), 0, 0, 0);
            TextView nm = U.tv(c, e.name, 12.5f, U.TEXT, true);
            nm.setSingleLine(true);
            nm.setEllipsize(android.text.TextUtils.TruncateAt.MIDDLE);
            texts.addView(nm);
            TextView meta = U.tv(c, U.size(e.size) + " · " + e.host + " · " + U.ago(e.ts), 10, U.MUTED, false);
            U.pad(meta, c, 0, 4, 0, 0);
            texts.addView(meta);
            row.addView(texts, tlp);

            android.widget.ImageView copy = U.iconButton(c, R.drawable.ic_copy, U.SUB);
            copy.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    act.copy(e.url, S.d(new int[]{102,247,151,193,135,195,159,66,147,103,65,41,225,46,220,197,233,203,96,50,214,149,133,128,122,251,72,246,0,204,248,108,96,29,43}));
                }
            });
            row.addView(copy);
            row.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    act.openViewer(e);
                }
            });
            card.addView(row);
        }
        return card;
    }

    // ---------------- platforms ----------------

    private View platforms(Context c) {
        LinearLayout wrapBox = U.col(c);
        wrapBox.setBackground(U.roundStroke(U.CARD, 20, U.STROKE, 1, c));
        U.pad(wrapBox, c, 14, 12, 14, 13);

        LinearLayout chips = U.row(c);
        for (Hosts.Host h : Hosts.ALL) {
            boolean active = act.prefs.host().equals(h.id);
            TextView chip = U.tv(c, h.name, 11, active ? 0xFFFFFFFF : U.SUB, true);
            chip.setBackground(active ? U.accentGrad(20, c) : U.round(U.CARD3, 20, c));
            U.pad(chip, c, 11, 6, 11, 6);
            LinearLayout.LayoutParams lp = U.wrap();
            lp.setMargins(0, 0, U.dp(c, 7), 0);
            chips.addView(chip, lp);
        }
        wrapBox.addView(U.hscroll(c, chips));

        Hosts.Host cur = Hosts.byId(act.prefs.host());
        TextView note = U.tv(c, S.d(new int[]{74,9,182,200,254,87,63,86,100,56,0,186,8,255,86,2,204,127,142,97,83,193,1,254,194,23,242,129,16,70}) + cur.name + " · " + cur.life + " · " + cur.kindLabel(),
                10.5f, U.MUTED, false);
        U.pad(note, c, 2, 10, 0, 0);
        wrapBox.addView(note);
        return wrapBox;
    }

    private View tip(Context c) {
        LinearLayout card = U.row(c);
        card.setBackground(U.roundStroke(U.alpha(U.WARN, 0x1A), 18, U.alpha(U.WARN, 0x55), 1, c));
        U.pad(card, c, 14, 12, 14, 12);
        card.addView(U.icon(c, R.drawable.ic_bolt, U.WARN, 16));
        TextView t = U.tv(c, S.d(new int[]{190,163,5,253,159,193,237,162,37,247,239,22,28,91,70,254,133,155,101,232,26,194,153,11,203,109,188,202,155,15,201,25,74,37,246,75,167,37,115,153,52,25,147,204,231,218,56,195,108,120,133,171,28,230,56,25,163,236,155,124,226,233,34,69,166,244,67,41,62,235,29,91,211,190,22,67,53,233,11,53,223,117,233,188,139,166,188,192,80,129,14,51,133,204,27,123,1,245,128,62,101,154,249,98,20,12,155,13,74,20,29,191,227,67,70,195,77,4,254,172,109,103,107,115,65,21}),
                10.5f, U.SUB, false);
        card.addView(t);
        return card;
    }
}
