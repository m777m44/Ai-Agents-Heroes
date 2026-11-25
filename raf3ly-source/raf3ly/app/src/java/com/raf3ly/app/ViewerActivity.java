package com.raf3ly.app;

import android.app.Activity;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;

/** Full screen preview / details of one archived file. */
public class ViewerActivity extends Activity {

    private Store store;
    private Entry entry;
    private TextView dlMeta;
    private ProgressBar dlBar;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        store = new Store(this);
        String id = getIntent().getStringExtra("id");
        entry = id == null ? null : store.get(id);
        if (entry == null) {
            finish();
            return;
        }

        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(U.BG);
        root.setLayoutDirection(I18n.rtl() ? View.LAYOUT_DIRECTION_RTL : View.LAYOUT_DIRECTION_LTR);

        ScrollView scroll = new ScrollView(this);
        LinearLayout box = U.col(this);
        U.pad(box, this, 16, 8, 16, 28);
        scroll.addView(box, U.match());
        root.addView(scroll, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT));

        // top bar
        LinearLayout top = U.row(this);
        ImageView back = U.iconButton(this, R.drawable.ic_close, U.SUB);
        back.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
        top.addView(back);

        LinearLayout titles = U.col(this);
        LinearLayout.LayoutParams tlp = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        tlp.setMargins(U.dp(this, 11), 0, 0, 0);
        TextView nm = U.tv(this, entry.name, 14, U.TEXT, true);
        nm.setSingleLine(true);
        nm.setEllipsize(android.text.TextUtils.TruncateAt.MIDDLE);
        titles.addView(nm);
        titles.addView(U.tv(this, U.size(entry.size) + " · " + entry.host + " · " + U.ago(entry.ts), 10.5f, U.MUTED, false));
        top.addView(titles, tlp);

        final ImageView star = U.iconButton(this, R.drawable.ic_star, entry.fav ? U.STAR : U.SUB);
        star.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                store.toggleFav(entry.id);
                entry.fav = !entry.fav;
                star.setColorFilter(entry.fav ? U.STAR : U.SUB);
            }
        });
        top.addView(star);
        box.addView(top);

        // preview
        LinearLayout preview = U.col(this);
        preview.setBackground(U.roundStroke(U.CARD, 22, U.STROKE, 1, this));
        preview.setGravity(Gravity.CENTER);
        U.pad(preview, this, 10, 10, 10, 10);
        LinearLayout.LayoutParams plp = U.matchH(U.dp(this, 320));
        plp.setMargins(0, U.dp(this, 14), 0, 0);
        box.addView(preview, plp);

        if (entry.isImage()) {
            ImageView img = new ImageView(this);
            img.setScaleType(ImageView.ScaleType.FIT_CENTER);
            img.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.MATCH_PARENT));
            preview.addView(img);
            ImageLoader.load(img, entry.url, U.dp(this, 900));
        } else {
            preview.addView(U.icon(this, entry.isVideo() ? R.drawable.ic_bolt : R.drawable.ic_file, U.FAINT, 64));
            TextView t = U.tv(this, S.d(new int[]{125,242,11,55,166,66,169,188,5,252,178,172,161,154,248,129,24,19,79,254,80,41,119,4,75,173,46,110,48,94,97,97,208,226,51,52,103,171,65,8,217,38,226,150,207,128,14,145,228,42,50,254,108,223,20,157,115,194,28,10,17,14}), 11.5f, U.FAINT, false);
            U.pad(t, this, 0, 10, 0, 0);
            preview.addView(t);
        }

        // actions
        LinearLayout actions = U.row(this);
        LinearLayout.LayoutParams alp = U.matchH(LinearLayout.LayoutParams.WRAP_CONTENT);
        alp.setMargins(0, U.dp(this, 14), 0, 0);
        box.addView(actions, alp);

        actions.addView(actionBtn(R.drawable.ic_copy, S.d(new int[]{125,84,172,145,182,101,117,249,157,141,13,110,238,16,10,161,60,231,191,241,199,225}), U.SUB, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                copy();
            }
        }), U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        LinearLayout.LayoutParams g1 = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        g1.setMargins(U.dp(this, 9), 0, 0, 0);
        actions.addView(actionBtn(R.drawable.ic_share, S.d(new int[]{21,70,53,48,112,196,100,43,128,162,49,99,204,184,185,237,236,185,5,24,120,156,48,161,5,187,139,147}), U.SUB, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                android.content.Intent s = new android.content.Intent(android.content.Intent.ACTION_SEND);
                s.setType("text/plain");
                s.putExtra(android.content.Intent.EXTRA_TEXT, entry.url);
                startActivity(android.content.Intent.createChooser(s, S.d(new int[]{3,15,86,173,117,202,248,98,155,155,78,102,139,16,240,20,59,240,230,220,253,17,1,172,60,120,117,50,16,32,125,161,251,41,9,6,246,203,241,241,149})));
            }
        }), g1);

        LinearLayout.LayoutParams g2 = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        g2.setMargins(U.dp(this, 9), 0, 0, 0);
        actions.addView(actionBtn(R.drawable.ic_dl, S.d(new int[]{196,33,127,191,157,227,75,80,106,114,51,124,118,150,45,51,55,177,88,100,55,125,246,161,116,87}), U.ACCENT2, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                download();
            }
        }), g2);

        // download progress
        LinearLayout dl = U.col(this);
        dl.setBackground(U.roundStroke(U.CARD, 16, U.STROKE, 1, this));
        U.pad(dl, this, 14, 12, 14, 12);
        LinearLayout.LayoutParams dlp = U.match();
        dlp.setMargins(0, U.dp(this, 12), 0, 0);
        box.addView(dl, dlp);
        dlBar = U.progress(this, 6);
        dl.addView(dlBar);
        dlMeta = U.tv(this, S.d(new int[]{27,24,109,85,24,196,2,15,50,118,16,96,20,82,231,170,208,10,207,97,100,228,39,70,62,198,75,174,98,178,24,164,158,151,236,162,103,24,15,59,116,197,1,55,201,215,125,116,109,84,4,180,214,39,131,111,103,27,43,119,130,106,26,148,240,114,190,51,190,229}), 10.5f, U.MUTED, false);
        U.pad(dlMeta, this, 0, 7, 0, 0);
        dl.addView(dlMeta);

        // details
        LinearLayout details = U.card(this);
        LinearLayout.LayoutParams dlp2 = U.match();
        dlp2.setMargins(0, U.dp(this, 14), 0, 0);
        box.addView(details, dlp2);

        details.addView(row(S.d(new int[]{120,78,113,75,33,48,18,3,246,253,150,66,29,121,1,228,75,101,59,111,6,224,199,83,50,44,25,93}), entry.url));
        details.addView(U.divider(this));
        details.addView(row(S.d(new int[]{195,4,36,209,83,162,186,1,230,184,1,228,192,28,17,150,125,43,185,184,224,94,150,153,106,154,54,223}), entry.host + " · " + Hosts.byId(hostId(entry.host)).life));
        details.addView(U.divider(this));
        details.addView(row(S.d(new int[]{100,212,78,190,118,3,154,212,196,21,130,9,71,97,217,33,71,84,47,208,85,16,148,204,176,212}), (entry.mime == null || entry.mime.isEmpty()) ? S.d(new int[]{85,81,11,209,0,9,82,191,179,9,226,153,19,72,59,70,135,112,34,138,198,168,179,5,224,114,151,59,38,16,192,14,27}) : entry.mime));
        details.addView(U.divider(this));
        details.addView(row(S.d(new int[]{10,1,151,225,219,88,58,186,246,211,71,121,115,118,88,222,254,123,10,241,85,81,15,90,55,214}), U.size(entry.size)));
        details.addView(U.divider(this));
        details.addView(row(S.d(new int[]{186,62,247,238,41,201,89,145,38,44,135,97,151,117,105,102,8,82,93,26,162,87,143,78,163,107,129,84,229,117,110,19,170,239,35,176,93}), U.date(entry.ts)));
        details.addView(U.divider(this));
        details.addView(row(S.d(new int[]{85,76,5,72,145,1,79,76,185,219,56,175,133,147,187,224,42,252,210,40,228,167,189,243,140,239,162,41,146,231,88,12,170,82,180,22,1,254,206,45,182}), String.valueOf(entry.downloads)));

        LinearLayout bottom = U.row(this);
        LinearLayout.LayoutParams blp = U.matchH(LinearLayout.LayoutParams.WRAP_CONTENT);
        blp.setMargins(0, U.dp(this, 14), 0, 0);
        box.addView(bottom, blp);

        TextView openBrowser = U.button(this, S.d(new int[]{134,214,182,123,135,47,248,177,176,107,81,112,8,149,213,77,7,186,8,132,76,125,91,126,42,133,168,125,25,16,1,210,208,162,145,209,41,42,31,45,103,235}), false);
        openBrowser.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    startActivity(new android.content.Intent(android.content.Intent.ACTION_VIEW,
                            android.net.Uri.parse(entry.url)));
                } catch (Exception ignored) {
                }
            }
        });
        bottom.addView(openBrowser, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        TextView del = U.button(this, S.d(new int[]{198,163,201,43,52,106,120,131,41,227,64,138,127,129,47,147,236,170,234,164,122,86,109,252,129,97,64,19,35,69,32,98,59,105,250,174,32,249}), false);
        del.setTextColor(U.DANGER);
        LinearLayout.LayoutParams d2 = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        d2.setMargins(U.dp(this, 9), 0, 0, 0);
        del.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                store.remove(entry.id);
                finish();
            }
        });
        bottom.addView(del, d2);

        setContentView(root);
    }

    private String hostId(String domain) {
        for (Hosts.Host h : Hosts.ALL) if (h.domain.equals(domain) || h.name.equals(domain)) return h.id;
        return "x0";
    }

    private View row(String label, String value) {
        LinearLayout r = U.col(this);
        r.addView(U.tv(this, label, 10, U.MUTED, true));
        TextView v = U.tv(this, value, 11.5f, U.SUB, false);
        U.pad(v, this, 0, 3, 0, 0);
        v.setTextIsSelectable(true);
        r.addView(v);
        return r;
    }

    private View actionBtn(int icon, String label, int color, View.OnClickListener cb) {
        LinearLayout b = U.col(this);
        b.setGravity(Gravity.CENTER);
        b.setBackground(U.roundStroke(U.CARD, 16, U.STROKE, 1, this));
        U.pad(b, this, 0, 11, 0, 11);
        b.addView(U.icon(this, icon, color, 19));
        TextView t = U.tv(this, label, 10.5f, U.SUB, true);
        U.pad(t, this, 0, 5, 0, 0);
        b.addView(t);
        b.setOnClickListener(cb);
        U.pressable(b);
        return b;
    }

    private void copy() {
        android.content.ClipboardManager cm = (android.content.ClipboardManager)
                getSystemService(CLIPBOARD_SERVICE);
        if (cm != null)
            cm.setPrimaryClip(android.content.ClipData.newPlainText("raf3ly", entry.url));
        android.widget.Toast.makeText(this, S.d(new int[]{81,175,19,217,242,103,139,173,55,112,69,104,115,206,100,53,20,117,182,246,27,23,105,150,85,244,87,250,97,68,35,167,136,210,73,246,147,44,5,105,86,246,63,214}), android.widget.Toast.LENGTH_SHORT).show();
    }

    private void download() {
        store.bumpDownload(entry.id);
        dlMeta.setText(I18n.t(S.d(new int[]{47,9,205,121,165,128,51,73,208,9,98,35,134,127,172,135,233,101,167,131,99,79,244,42,45,253,48,88,219,138,3,211,90,222,238,241,66,147,9,152,3,243})));
        Downloader.start(this, entry, new Downloader.Cb() {
            @Override
            public void onProgress(long done, long total, long bps, long eta) {
                dlBar.setProgress(total > 0 ? (int) Math.min(1000, done * 1000 / total) : 300);
                dlMeta.setText(U.size(done) + (total > 0 ? " / " + U.size(total) : "")
                        + " · " + U.speed(bps) + (eta > 0 ? S.d(new int[]{250,52,46,76,235,113,18,157,214,143,238,80,186,187,144,86,47,99,202,56,244,74,171,127,132,130,111,96,52}) + U.dur(eta) : ""));
            }

            @Override
            public void onDone(String message, android.net.Uri uri) {
                dlBar.setProgress(1000);
                dlMeta.setText(I18n.t(message));
            }

            @Override
            public void onError(String message) {
                dlMeta.setText(I18n.t(S.d(new int[]{143,121,236,220,76,118,199,79,230,188,210,145,34,66,232,30,6,5,2,226,57,172,146,163})) + message);
            }
        });
    }
}
