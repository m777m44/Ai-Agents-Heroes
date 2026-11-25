package com.raf3ly.app;

import android.content.Context;
import android.view.Gravity;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

/** Tab 1: upload queue with live counters, cancel and retry. */
public class UploadView {

    public final ScrollView root;
    private final MainActivity act;
    private final LinearLayout box;

    private TextView cPending, cSpeed, cDone;
    private LinearLayout overallCard;
    private ProgressBar overallBar;
    private TextView overallPct, overallMeta;
    private LinearLayout queueBox;
    private TextView emptyHint;
    private LinearLayout queueSection;

    private final ArrayList<Row> rows = new ArrayList<>();
    private final Set<Integer> notified = new HashSet<>();

    public UploadView(MainActivity a) {
        act = a;
        Context c = a;
        root = new ScrollView(c);
        root.setBackgroundColor(U.BG);
        root.setFillViewport(true);

        box = U.col(c);
        U.pad(box, c, 16, 4, 16, 26);
        root.addView(box, U.match());

        box.addView(picker());
        box.addView(U.spacer(c, 14));
        box.addView(counters());
        box.addView(U.spacer(c, 14));
        box.addView(overallCard());
        box.addView(U.spacer(c, 12));

        queueSection = U.col(c);
        queueSection.addView(U.sectionHead(c, S.d(new int[]{230,223,86,189,226,49,151,49,135,165,4,139,186,217,248,4,13,160,192,36,207,103,95,222,237,13,157,215,153,168,168,215,244,22,10,125,1}), S.d(new int[]{169,132,229,36,20,63,68,103,86,18,94,168,60,2,230,254,58,248,124,247,124,147,128,103,123,194,116,54,213,131,184,94,233,130,198,15,247,89,193,128,32}), new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.uploader.clearFinished();
            }
        }));
        queueBox = U.col(c);
        queueSection.addView(queueBox);
        box.addView(queueSection);

        box.addView(U.spacer(c, 16));
        box.addView(hostNote());

        refresh();
    }

    private View picker() {
        Context c = act;
        LinearLayout card = U.col(c);
        card.setBackground(U.roundStroke(U.CARD, 22, U.STROKE, 1, c));
        U.pad(card, c, 16, 18, 16, 16);

        LinearLayout top = U.row(c);
        LinearLayout circle = U.col(c);
        circle.setGravity(Gravity.CENTER);
        circle.setLayoutParams(U.lp(U.dp(c, 58), U.dp(c, 58)));
        circle.setBackground(U.round(U.alpha(U.ACCENT, 0x26), 29, c));
        circle.addView(U.icon(c, R.drawable.ic_up, U.ACCENT2, 26));
        top.addView(circle);

        LinearLayout texts = U.col(c);
        LinearLayout.LayoutParams tlp = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        tlp.setMargins(U.dp(c, 13), 0, 0, 0);
        texts.addView(U.tv(c, S.d(new int[]{114,217,39,96,232,57,90,216,183,20,189,60,110,210,222,181,193,24,155,33,218,126,17,97,185,168,90,79,106,26,21,59,66,111,34,121,127,110,145,215}), 16, U.TEXT, true));
        TextView sub = U.tv(c, S.d(new int[]{23,123,108,251,48,30,41,189,236,113,35,24,236,26,101,134,242,152,216,214,148,39,185,184,208,134,229,111,205,59,242,114,125,94,144,47,52,16,163,31,156,223,136,39,6,197,180,44,96,34,172,253,174,26,86,130,34,116,217,159,107,90,16,66,11,39,10,96,163,11,1,138,152,45,40,54,65,110,51,45,220,227,29,42,125,112}), 11, U.MUTED, false);
        U.pad(sub, c, 0, 4, 0, 0);
        texts.addView(sub);
        top.addView(texts, tlp);
        card.addView(top);

        LinearLayout actions = U.row(c);
        U.pad(actions, c, 0, 16, 0, 0);

        TextView b1 = U.button(c, S.d(new int[]{232,95,226,236,120,87,168,26,73,200,188,85,178,69,204,25,197,182,183,82,93,150,138,60,87,59,223,164,38,121,251}), true);
        b1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.pickFiles();
            }
        });
        actions.addView(b1, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        TextView b2 = U.button(c, S.d(new int[]{33,215,4,17,152,155,214,96,248,138,21,143,41,79,61,199,152,111,62,35,177,237}), false);
        LinearLayout.LayoutParams p2 = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        p2.setMargins(U.dp(c, 8), 0, U.dp(c, 8), 0);
        b2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.pickImages();
            }
        });
        actions.addView(b2, p2);

        TextView b3 = U.button(c, "📷", false);
        b3.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.takePhoto();
            }
        });
        actions.addView(b3, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        card.addView(actions);

        TextView hint = U.tv(c, S.d(new int[]{7,76,14,161,67,117,60,118,240,160,127,191,179,125,84,196,235,66,222,140,95,10,108,68,26,128,181,210,181,18,65,134,123,161,87,29,11}) + Hosts.byId(act.prefs.host()).name
                + " · " + Hosts.byId(act.prefs.host()).life, 10.5f, U.FAINT, false);
        hint.setGravity(Gravity.CENTER);
        U.pad(hint, c, 0, 11, 0, 0);
        card.addView(hint);
        return card;
    }

    private View counters() {
        Context c = act;
        LinearLayout row = U.row(c);

        LinearLayout a = statCard(c, S.d(new int[]{143,145,109,41,116,107,63,94,224,146,221,175,231,254,158,37,84,172,105,212,132,45,211,103,12,120,54,19,177,214,84,254,249,85,119,249,100}), "0", U.ACCENT2, R.drawable.ic_up);
        cPending = (TextView) a.getTag();
        row.addView(a, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        LinearLayout b = statCard(c, S.d(new int[]{37,126,185,126,177,4,193,45,175,21,165,110,168,4,253,37,111,19,27,61}), "0", U.SUCCESS, R.drawable.ic_check);
        cDone = (TextView) b.getTag();
        LinearLayout.LayoutParams lpb = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        lpb.setMargins(U.dp(c, 9), 0, U.dp(c, 9), 0);
        row.addView(b, lpb);

        LinearLayout d = statCard(c, S.d(new int[]{81,135,115,117,235,71,97,204,60,107,245,150,192,117,167,72,194,180,81,250,7,46,228,96,166,247,234,251}), "0 KB/s", U.STAR, R.drawable.ic_bolt);
        cSpeed = (TextView) d.getTag();
        row.addView(d, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        return row;
    }

    private LinearLayout statCard(Context c, String label, String value, int color, int icon) {
        LinearLayout card = U.col(c);
        card.setBackground(U.roundStroke(U.CARD, 18, U.STROKE, 1, c));
        U.pad(card, c, 12, 12, 12, 12);

        LinearLayout top = U.row(c);
        top.addView(U.icon(c, icon, U.alpha(color, 0xCC), 13));
        TextView l = U.tv(c, " " + label, 10, U.MUTED, false);
        top.addView(l);
        card.addView(top);

        TextView v = U.tv(c, value, 17, color, true);
        U.pad(v, c, 0, 6, 0, 0);
        card.addView(v);
        card.setTag(v);
        return card;
    }

    private View overallCard() {
        Context c = act;
        overallCard = U.col(c);
        overallCard.setBackground(U.roundStroke(U.alpha(U.ACCENT, 0x1F), 18, U.alpha(U.ACCENT, 0x66), 1, c));
        U.pad(overallCard, c, 14, 13, 14, 13);
        overallCard.setVisibility(View.GONE);

        LinearLayout top = U.row(c);
        top.addView(U.tv(c, S.d(new int[]{72,197,112,238,15,228,255,206,171,62,83,240,174,23,196,70,80,155,157,242,118,95,105,218,162,231,164,171,11,154,143,102,164,227,18,28,34,75,207}), 13, U.TEXT, true), U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        overallPct = U.tv(c, "0%", 14, U.ACCENT2, true);
        top.addView(overallPct);
        overallCard.addView(top);

        overallBar = U.progress(c, 8);
        LinearLayout.LayoutParams lbp = U.matchH(U.dp(c, 8));
        lbp.setMargins(0, U.dp(c, 10), 0, 0);
        overallCard.addView(overallBar, lbp);

        overallMeta = U.tv(c, "", 11, U.SUB, false);
        U.pad(overallMeta, c, 0, 8, 0, 0);
        overallCard.addView(overallMeta);
        return overallCard;
    }

    private View hostNote() {
        Context c = act;
        LinearLayout card = U.col(c);
        card.setBackground(U.roundStroke(U.CARD, 18, U.STROKE, 1, c));
        U.pad(card, c, 14, 12, 14, 12);

        LinearLayout r1 = U.row(c);
        r1.addView(U.icon(c, R.drawable.ic_server, U.MUTED, 15));
        r1.addView(U.tv(c, "  " + Hosts.byId(act.prefs.host()).name + " — "
                + Hosts.byId(act.prefs.host()).note, 11, U.MUTED, false));
        card.addView(r1);

        TextView t2 = U.tv(c, S.d(new int[]{156,141,219,173,248,68,172,227,52,146,112,126,1,189,138,238,220,108,109,166,159,93,142,15,33,33,149,241,212,46,185,44,154,48,62,245,97,92,245,19,75,122,180,86,176,31,45,214,122,152,30,75,124,240,35,101,47,240,67,58,104,5,78,110,187,105,31,59,64,203,86,191,184,55,197,79,21,94,44,166,101,96,239,25,164,33,135,21,134,105,141,14,80,65,117,118,4,55,233,243,255,199,57,205,175,150,100,74,172,154,52,205,195,144,133,124,109,212,207,6,21,195,139,188,158,173,62,114,44,27,227,46,21,84,95,28,178,229,73,92,220,235,171,77,172,171,19,94,178,115,241,188,203,194,138,33,170,144,254,227,175,41,178,48,177,191,248,225,99,78,228,252,42,236,25,236,213,238,238,93,180,94,11,71,109,53}),
                10.5f, U.FAINT, false);
        U.pad(t2, c, 0, 7, 0, 0);
        card.addView(t2);
        return card;
    }

    // ---------- live ----------

    public void refresh() {
        onUploaderChanged();
    }

    public void onUploaderChanged() {
        Uploader u = act.uploader;
        cPending.setText(String.valueOf(u.pendingCount()));
        cDone.setText(String.valueOf(u.doneCount()));
        long speed = u.activeSpeed();
        cSpeed.setText(speed > 0 ? U.speed(speed) : "0 KB/s");

        long done = u.activeDone(), tot = u.activeTotal();
        if (u.running && tot > 0) {
            overallCard.setVisibility(View.VISIBLE);
            int p = (int) Math.min(1000, done * 1000 / tot);
            overallBar.setProgress(p);
            overallPct.setText((p / 10) + "%");
            long eta = u.activeEta();
            overallMeta.setText(U.size(done) + S.d(new int[]{184,104,122,129,37,228,225,23,172,243,107,186,242,183,185,148,178,180,239,74,174,111}) + U.size(tot) + " · " + U.speed(speed)
                    + (eta > 0 ? S.d(new int[]{181,133,220,182,114,212,198,192,62,242,181,52,136,97,88,88,236,212,209,135,208,46,105,225,77,133,18,1,3}) + U.dur(eta) : ""));
        } else {
            overallCard.setVisibility(View.GONE);
        }

        syncRows();

        for (Uploader.Task t : u.tasks) {
            int key = System.identityHashCode(t);
            if (t.state == Uploader.DONE && t.entry != null && !notified.contains(key)) {
                notified.add(key);
                if (act.prefs.autoCopy()) act.copy(t.entry.url, S.d(new int[]{17,107,21,103,64,26,123,235,39,220,76,113,60,187,124,46,206,99,60,138,191,64,65,31,32,251,102,108,211,0,169,0,103,83,162,44,28,187,1,142,221,131,79,246,106,20,155,237,15,66,99,106,134,152,154,186,1,247,24}));
                else act.toast(S.d(new int[]{83,191,224,18,239,154,138,66,94,131,97,204,143,13,234,59,15,122,161,167,91,111,62,186,44,146,66,160,125,114,186,206,52,149,92}));
                act.haptic();
                act.refreshData();
            }
        }
    }

    private void syncRows() {
        ArrayList<Uploader.Task> tasks = act.uploader.tasks;
        while (rows.size() > tasks.size()) {
            Row r = rows.remove(rows.size() - 1);
            queueBox.removeView(r.view);
        }
        while (rows.size() < tasks.size()) {
            Row r = new Row(tasks.get(rows.size()));
            rows.add(r);
            queueBox.addView(r.view, U.match());
            LinearLayout.LayoutParams lp = U.match();
            lp.setMargins(0, 0, 0, U.dp(act, 9));
            r.view.setLayoutParams(lp);
        }
        for (int i = 0; i < rows.size(); i++) rows.get(i).bind(tasks.get(i));

        if (tasks.isEmpty()) {
            if (emptyHint == null) {
                emptyHint = U.tv(act, S.d(new int[]{76,242,220,194,202,91,9,171,0,47,177,16,47,47,141,24,145,205,4,152,176,228,46,136,99,151,87,144,161,143,120,213,84,233,124,246,8,219,174,247,75,204,169,186,69,54,15,227,219,166,74,209,120,160,122,253,209,254,159,203,147,205,233,249,208,186,148,16,248,167,104,93,252,29,229,162,127,148,146,121,189,190,52,113,165,46,36,12}), 12, U.FAINT, false);
                emptyHint.setGravity(Gravity.CENTER);
                U.pad(emptyHint, act, 0, 16, 0, 16);
                queueBox.addView(emptyHint);
            }
        } else if (emptyHint != null) {
            queueBox.removeView(emptyHint);
            emptyHint = null;
        }
    }

    private class Row {
        final View view;
        final TextView name, meta, status;
        final ProgressBar bar;
        final LinearLayout actions;
        final TextView link;
        Uploader.Task task;

        Row(final Uploader.Task t) {
            task = t;
            Context c = act;
            LinearLayout card = U.col(c);
            card.setBackground(U.roundStroke(U.CARD, 18, U.STROKE, 1, c));
            U.pad(card, c, 13, 12, 13, 12);

            LinearLayout top = U.row(c);

            LinearLayout badge = U.col(c);
            badge.setGravity(Gravity.CENTER);
            badge.setLayoutParams(U.lp(U.dp(c, 36), U.dp(c, 36)));
            badge.setBackground(U.round(U.alpha(U.ACCENT2, 0x22), 12, c));
            boolean img = t.mime != null && t.mime.startsWith("image/");
            badge.addView(U.icon(c, img ? R.drawable.ic_img : R.drawable.ic_file, U.ACCENT2, 17));
            top.addView(badge);

            LinearLayout texts = U.col(c);
            LinearLayout.LayoutParams tlp = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
            tlp.setMargins(U.dp(c, 11), 0, 0, 0);
            name = U.tv(c, t.name, 12.5f, U.TEXT, true);
            name.setSingleLine(true);
            name.setEllipsize(android.text.TextUtils.TruncateAt.MIDDLE);
            texts.addView(name);
            meta = U.tv(c, U.size(t.size), 10.5f, U.MUTED, false);
            U.pad(meta, c, 0, 3, 0, 0);
            texts.addView(meta);
            top.addView(texts, tlp);

            status = U.tv(c, S.d(new int[]{122,141,6,229,163,178,47,109,164,225,100,50,141,194,12,224,133,64,89,91,33,48,163,249,180,159,156,150,30,156}), 11, U.MUTED, true);
            top.addView(status);
            card.addView(top);

            bar = U.progress(c, 6);
            LinearLayout.LayoutParams lbp = U.matchH(U.dp(c, 6));
            lbp.setMargins(0, U.dp(c, 10), 0, 0);
            card.addView(bar, lbp);

            actions = U.row(c);
            U.pad(actions, c, 0, 9, 0, 0);
            actions.setVisibility(View.GONE);

            link = U.tv(c, "", 10.5f, U.ACCENT2, false);
            link.setSingleLine(true);
            link.setEllipsize(android.text.TextUtils.TruncateAt.MIDDLE);
            actions.addView(link, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

            final ImageView copy = U.iconButton(c, R.drawable.ic_copy, U.SUB);
            copy.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    if (task.entry != null) act.copy(task.entry.url, S.d(new int[]{25,237,65,196,5,32,52,66,126,52,76,125,99,172,114,235,221,15,228,214,64,231,75,142,18,222,255,129,247,133,188,212,162,168,213,251,182,49,5,92,159,230,182,32}));
                }
            });
            actions.addView(copy);

            final ImageView share = U.iconButton(c, R.drawable.ic_share, U.SUB);
            LinearLayout.LayoutParams s2 = U.lp(U.dp(c, 36), U.dp(c, 36));
            s2.setMargins(U.dp(c, 7), 0, 0, 0);
            share.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    if (task.entry != null) act.share(task.entry.url);
                }
            });
            actions.addView(share, s2);

            card.addView(actions);
            view = card;
        }

        void bind(final Uploader.Task t) {
            task = t;
            name.setText(t.name);
            String sizeTxt = t.total > 0 ? U.size(t.total) : U.size(t.size);
            actions.setVisibility(t.state == Uploader.DONE ? View.VISIBLE : View.GONE);
            if (t.entry != null) link.setText(t.entry.url);

            switch (t.state) {
                case Uploader.QUEUED:
                    status.setText(I18n.t(S.d(new int[]{17,190,143,5,26,121,64,132,214,131,221,42,156,83,160,216,112,191,169,126,26,190,64,102,49,110,117,232,138,28})));
                    status.setTextColor(U.MUTED);
                    bar.setProgress(0);
                    meta.setText(sizeTxt + S.d(new int[]{53,134,172,221,216,253,87,149,110,123,160,236,200,184,129,55,76,37,117,165,21,154,17,64,91,40,80,184,218,42,91,230,197,203,200,130,176,171,34}));
                    break;
                case Uploader.PREPARING:
                    status.setText(I18n.t(S.d(new int[]{199,89,217,37,159,157,67,229,89,17,148,63,35,53,8,5,183,142,31,214,4,165,109,18,210,166})));
                    status.setTextColor(U.WARN);
                    bar.setProgress(t.total > 0 ? (int) Math.min(1000, t.done * 1000 / t.total) : 200);
                    meta.setText(sizeTxt + S.d(new int[]{144,15,123,135,175,108,253,233,84,169,170,80,5,14,147,4,150,245,167,74,235,250,51,207,141,167,123,148,171,21,153,85,203,30,255,160,68,68,145,246,73}));
                    break;
                case Uploader.UPLOADING:
                    status.setText(U.pct(t.done, t.total));
                    status.setTextColor(U.ACCENT2);
                    bar.setProgress((int) Math.min(1000, t.done * 1000 / Math.max(1, t.total)));
                    meta.setText(U.size(t.done) + " / " + sizeTxt + " · " + U.speed(t.bps)
                            + (t.eta > 0 ? S.d(new int[]{70,4,70,128,139,254,109,35,108,182,106,80,9,187,42,76,70,16,98,139,247,169,186,176,130,77,125,223,41}) + U.dur(t.eta) : ""));
                    break;
                case Uploader.DONE:
                    status.setText(I18n.t(S.d(new int[]{21,19,107,10,142,82,230,113,176,205,163,179,54,236,62,38,61,226,27,127,56,128,77,67})));
                    status.setTextColor(U.SUCCESS);
                    bar.setProgress(1000);
                    meta.setText(sizeTxt + " · " + (t.entry != null ? t.entry.host : "—"));
                    break;
                case Uploader.CANCELLED:
                    status.setText(I18n.t(S.d(new int[]{51,75,47,111,60,72,127,243,41,177,186,186,171,237,253,114,56,70,68,99,150,155,220,88})));
                    status.setTextColor(U.MUTED);
                    meta.setText(sizeTxt + S.d(new int[]{128,28,233,52,228,105,93,37,194,99,207,148,209,34,63,48,238,120,168,73,98,22,204,175,208,71,102,178,8,226}));
                    bar.setProgress(0);
                    break;
                case Uploader.FAILED:
                    status.setText(I18n.t(S.d(new int[]{29,4,10,143,251,197,103,152,108,200,140,220,161,95,180,213,120,13,26,71,253,101})));
                    status.setTextColor(U.DANGER);
                    meta.setText(I18n.t(t.error));
                    bar.setProgress(0);
                    break;
            }
        }
    }
}
