package com.raf3ly.app;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Vibrator;
import android.provider.MediaStore;
import android.view.Gravity;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends Activity {

    public static final int REQ_FILES = 101, REQ_IMAGES = 102, REQ_CAMERA = 103;

    Store store;
    Prefs prefs;
    Uploader uploader;

    FrameLayout content;
    LinearLayout nav;
    LinearLayout root;

    HomeView homeView;
    UploadView uploadView;
    ArchiveView archiveView;
    SettingsView settingsView;

    int tab = 0;
    final int[] navIconRes = {R.drawable.ic_home, R.drawable.ic_up, R.drawable.ic_folder, R.drawable.ic_gear};
    final String[] navTitles = {S.d(new int[]{94,47,35,113,192,78,141,130,114,187,24,152,10,59,249,159,250,210,37,148,140,150,99,106,97,194,106,188,61,39,175,183}), S.d(new int[]{65,207,168,184,5,74,181,130,143,148,126,100,193,20,209,249,59,219,77,192,247,248}), S.d(new int[]{25,247,169,250,199,71,91,177,102,247,37,48,31,42,18,193,242,138,87,112,30,144,165,58,213,143,253,221,82,27,148,102}), S.d(new int[]{230,242,227,113,64,81,120,76,233,15,255,184,143,61,64,222,98,213,205,75,72,255,229,80,202,252,163,202,7,38,162,216,235,66})};
    final ImageView[] navIcons = new ImageView[4];
    final TextView[] navLabels = new TextView[4];
    final LinearLayout[] navItems = new LinearLayout[4];
    final View[] navIndicators = new View[4];

    Uri cameraTarget;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        prefs = new Prefs(this);
        U.setAccent(prefs.accent());
        store = new Store(this);

        uploader = new Uploader(this, store, prefs, new Uploader.Listener() {
            @Override
            public void onChanged() {
                if (uploadView != null) uploadView.onUploaderChanged();
                if (homeView != null && tab == 0) homeView.refresh();
            }
        });

        buildUi();
        setTab(0);
        handleIncoming(getIntent());
        if (!prefs.welcomed()) showWelcome();
    }

    public void buildUi() {
        root = U.col(this);
        root.setLayoutDirection(I18n.rtl() ? View.LAYOUT_DIRECTION_RTL : View.LAYOUT_DIRECTION_LTR);
        root.setBackgroundColor(U.BG);

        root.addView(topBar());

        content = new FrameLayout(this);
        root.addView(content, U.lpw(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));

        root.addView(bottomNav());
        setContentView(root);

        homeView = new HomeView(this);
        uploadView = new UploadView(this);
        archiveView = new ArchiveView(this);
        settingsView = new SettingsView(this);
    }

    private View topBar() {
        LinearLayout wrap = U.row(this);
        wrap.setBackgroundColor(U.BG);
        U.pad(wrap, this, 16, 12, 16, 8);

        LinearLayout logo = U.col(this);
        logo.setGravity(Gravity.CENTER);
        logo.setLayoutParams(U.lp(U.dp(this, 40), U.dp(this, 40)));
        logo.setBackground(U.accentGrad(13, this));
        logo.addView(U.icon(this, R.drawable.ic_up, 0xFFFFFFFF, 20), U.lp(U.dp(this, 20), U.dp(this, 20)));
        wrap.addView(logo);

        LinearLayout titles = U.col(this);
        titles.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        LinearLayout.LayoutParams tlp = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        tlp.setMargins(U.dp(this, 11), 0, U.dp(this, 8), 0);
        TextView title = U.tv(this, S.d(new int[]{127,57,145,133,0,212,246,239,189,79,31,1,92,14,236,193,141,125,150,170,48,73,119,146,234,200}), 17, U.TEXT, true);
        title.setTextDirection(View.TEXT_DIRECTION_RTL);
        titles.addView(title);
        TextView sub = U.tv(this, S.d(new int[]{146,3,29,222,11,47,158,39,199,165,45,238,13,60,185,51,30,231,86,87,211,206,24,139,213,248,153,91,119,198,232,128,216,141,98,190,156,29,236,74,25,240,21,142,211,51,68,101,139,135,93}), 10.5f, U.MUTED, false);
        U.pad(sub, this, 0, 3, 0, 0);
        sub.setTextDirection(View.TEXT_DIRECTION_RTL);
        titles.addView(sub);
        wrap.addView(titles, tlp);

        Hosts.Host host = Hosts.byId(prefs.host());
        LinearLayout live = U.row(this);
        live.setBackground(U.roundStroke(U.CARD, 20, U.STROKE, 1, this));
        U.pad(live, this, 9, 6, 9, 6);
        View dot = new View(this);
        dot.setBackground(U.round(U.SUCCESS, 10, this));
        live.addView(dot, U.lp(U.dp(this, 6), U.dp(this, 6)));
        TextView on = U.tv(this, " " + host.name, 10, U.SUB, true);
        live.addView(on);
        wrap.addView(live);

        return wrap;
    }

    private View bottomNav() {
        LinearLayout wrap = U.col(this);
        View line = new View(this);
        line.setBackgroundColor(U.DIVIDER);
        wrap.addView(line, U.matchH(1));

        nav = U.row(this);
        nav.setBackgroundColor(0xFF0D1220);
        nav.setGravity(Gravity.CENTER_VERTICAL);
        U.pad(nav, this, 6, 7, 6, 9);

        for (int i = 0; i < 4; i++) {
            final int idx = i;
            LinearLayout item = U.col(this);
            item.setGravity(Gravity.CENTER);
            U.pad(item, this, 0, 0, 0, 2);

            View ind = new View(this);
            LinearLayout.LayoutParams ilp = U.lp(U.dp(this, 20), U.dp(this, 3));
            ilp.setMargins(0, 0, 0, U.dp(this, 6));
            ind.setLayoutParams(ilp);
            ind.setBackground(U.accentGrad(3, this));

            ImageView ic = U.icon(this, navIconRes[i], U.MUTED, 23);
            ic.setLayoutParams(U.lp(U.dp(this, 23), U.dp(this, 23)));

            TextView lb = U.tv(this, navTitles[i], 10.5f, U.MUTED, true);
            LinearLayout.LayoutParams llp = U.wrap();
            llp.setMargins(0, U.dp(this, 4), 0, 0);
            lb.setTextDirection(View.TEXT_DIRECTION_RTL);

            item.addView(ind);
            item.addView(ic);
            item.addView(lb, llp);
            item.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    setTab(idx);
                }
            });
            nav.addView(item, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
            navItems[i] = item;
            navIcons[i] = ic;
            navLabels[i] = lb;
            navIndicators[i] = ind;
        }
        wrap.addView(nav);
        return wrap;
    }

    public void setTab(int i) {
        tab = i;
        content.removeAllViews();
        View v;
        if (i == 0) {
            homeView.refresh();
            v = homeView.root;
        } else if (i == 1) {
            uploadView.refresh();
            v = uploadView.root;
        } else if (i == 2) {
            archiveView.refresh();
            v = archiveView.root;
        } else {
            settingsView.refresh();
            v = settingsView.root;
        }
        content.addView(v, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT));

        for (int k = 0; k < 4; k++) {
            boolean active = k == i;
            navIcons[k].setColorFilter(active ? U.ACCENT2 : U.MUTED);
            navLabels[k].setTextColor(active ? 0xFFFFFFFF : U.MUTED);
            navLabels[k].setTextSize(active ? 10.5f : 10.5f);
            navIndicators[k].setVisibility(active ? View.VISIBLE : View.INVISIBLE);
            navItems[k].setBackground(null);
        }
    }

    /** Rebuild everything (after a theme change). */
    public void rebuildAll() {
        buildUi();
        setTab(Math.min(tab, 3));
    }

    public void refreshData() {
        if (archiveView != null) archiveView.refresh();
        if (homeView != null && tab == 0) homeView.refresh();
    }

    // ---------------- actions ----------------

    public void pickFiles() {
        Intent in = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        in.addCategory(Intent.CATEGORY_OPENABLE);
        in.setType("*/*");
        in.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
        try {
            startActivityForResult(in, REQ_FILES);
        } catch (Exception e) {
            toast(S.d(new int[]{219,251,74,247,240,97,28,64,48,132,43,117,42,162,6,154,23,9,4,47,75,38,35,213,131,184,249,53,182,108,109,17,107,7,85,30,176,145,68,236,0,3,245,15,127,147,164,10,136,77,138,161,149,49,57}));
        }
    }

    public void pickImages() {
        Intent in = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        in.addCategory(Intent.CATEGORY_OPENABLE);
        in.setType("image/*");
        in.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
        try {
            startActivityForResult(in, REQ_IMAGES);
        } catch (Exception e) {
            toast(S.d(new int[]{97,30,224,107,34,92,210,121,94,237,49,28,197,225,163,215,237,199,178,114,79,227,57,58,119,53,22,212,68,1,180,139,80,71,38,251,116,160,118,114,11,29,137,149,41,116,72,49,107,191,164}));
        }
    }

    public void takePhoto() {
        if (Build.VERSION.SDK_INT < 29) {
            toast(S.d(new int[]{127,27,228,45,248,207,245,20,239,189,232,3,254,221,232,168,130,240,92,144,33,178,190,51,139,180,153,246,144,25,56,92,63,130,159,103,52,37,85,74,175,29,4,236,238,224,155,222,99,171,203,44,195,228,49,227,255,127,27,56,3,99,85,109,112,54,148,30,17,99,219,77,222,179,193,88,139,245,112,76,71,86,25,29,158,60,58,161,106,232,117,149,231,108,53,212,44,106,11,203,229,252,177,207,177,168,225,144,66,47,82,201,198,4,105,23,144,121,243,194}));
            return;
        }
        try {
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.MediaColumns.DISPLAY_NAME, "raf3ly_" + System.currentTimeMillis() + ".jpg");
            cv.put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg");
            cv.put(MediaStore.MediaColumns.RELATIVE_PATH, "Pictures/Raf3ly");
            cameraTarget = getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, cv);
            Intent in = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
            in.putExtra(MediaStore.EXTRA_OUTPUT, cameraTarget);
            in.setClipData(ClipData.newRawUri("", cameraTarget));
            in.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION);
            startActivityForResult(in, REQ_CAMERA);
        } catch (Exception e) {
            toast(S.d(new int[]{81,98,208,161,174,146,47,191,36,157,81,208,171,169,155,252,182,40,196,209,49,171,26,253,48,64,124,243,195,106,26,16,54,18,161,51,182,48,79,79,38,69,155,194,230,209,196,244,196,114,16,179,187,227,20,124,141}));
        }
    }

    private void handleIncoming(Intent intent) {
        if (intent == null) return;
        String action = intent.getAction();
        if (Intent.ACTION_SEND.equals(action)) {
            Uri u = intent.getParcelableExtra(Intent.EXTRA_STREAM);
            if (u != null) {
                List<Uri> l = new ArrayList<>();
                l.add(u);
                setTab(1);
                uploader.enqueue(l);
            }
        } else if (Intent.ACTION_SEND_MULTIPLE.equals(action)) {
            ArrayList<Uri> uris = intent.getParcelableArrayListExtra(Intent.EXTRA_STREAM);
            if (uris != null && !uris.isEmpty()) {
                setTab(1);
                uploader.enqueue(uris);
            }
        }
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleIncoming(intent);
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        super.onActivityResult(req, res, data);
        if (req == REQ_CAMERA) {
            if (res == RESULT_OK && cameraTarget != null) {
                List<Uri> l = new ArrayList<>();
                l.add(cameraTarget);
                setTab(1);
                uploader.enqueue(l);
            }
            cameraTarget = null;
            return;
        }
        if (res != RESULT_OK || data == null) return;
        List<Uri> uris = new ArrayList<>();
        ClipData cd = data.getClipData();
        if (cd != null) {
            for (int i = 0; i < cd.getItemCount(); i++) {
                Uri u = cd.getItemAt(i).getUri();
                if (u != null) uris.add(u);
            }
        } else if (data.getData() != null) {
            uris.add(data.getData());
        }
        if (uris.isEmpty()) return;
        setTab(1);
        uploader.enqueue(uris);
    }

    public void copy(String text, String label) {
        ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        if (cm != null) cm.setPrimaryClip(ClipData.newPlainText("raf3ly", text));
        toast(label == null ? S.d(new int[]{152,196,118,243,93,92,25,197,85,198,43,170,39,72,203,90,14,116,46,209,157,117,40,36,101,146,170,42,188,108,123,142,116,25,124}) : label);
        haptic();
    }

    public String paste() {
        ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        if (cm == null || cm.getPrimaryClip() == null || cm.getPrimaryClip().getItemCount() == 0) return "";
        CharSequence s = cm.getPrimaryClip().getItemAt(0).coerceToText(this);
        return s == null ? "" : s.toString();
    }

    public void share(String url) {
        Intent s = new Intent(Intent.ACTION_SEND);
        s.setType("text/plain");
        s.putExtra(Intent.EXTRA_TEXT, url);
        try {
            startActivity(Intent.createChooser(s, S.d(new int[]{229,195,217,77,174,135,215,115,192,225,114,117,113,19,230,247,7,85,47,245,37,90,220,17,65,3,91,225,226,234,118,165,114,163,37,133,188,8,216,91,178})));
        } catch (Exception e) {
            toast(S.d(new int[]{58,78,95,29,254,24,213,192,50,152,138,8,24,232,218,72,70,169,199,10,189,229,126,102,41,83,104,211,175,93,135,195,117,191,246,59,71,234,113,74,197,77,85,95,251,104,165,26}));
        }
    }

    public void openUrl(String url) {
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
        } catch (Exception e) {
            toast(S.d(new int[]{55,80,233,62,145,131,175,57,153,48,171,158,169,87,245,118,88,205,4,54,60,76,133,211,71,228,242,15,54,128,30,161,244,110,101,189,7,18,125,76,255,184,46,217}));
        }
    }

    public void openViewer(Entry e) {
        Intent i = new Intent(this, ViewerActivity.class);
        i.putExtra("id", e.id);
        startActivity(i);
    }

    public void toast(String s) {
        Toast.makeText(this, I18n.t(s), Toast.LENGTH_SHORT).show();
    }

    public void haptic() {
        if (!prefs.haptics()) return;
        try {
            Vibrator v = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
            if (v != null) v.vibrate(12);
        } catch (Exception ignored) {
        }
    }

    public void openTelegram() {
        openUrl(Brand.TELEGRAM);
    }

    public void openYoutube() {
        openUrl(Brand.YOUTUBE);
    }

    private android.app.Dialog welcome;

    private void showWelcome() {
        prefs.setWelcomed(true);
        Hosts.Host def = Hosts.byId(prefs.host());

        // ---- card shell ----------------------------------------------------
        LinearLayout card = U.col(this);
        card.setLayoutDirection(I18n.rtl() ? View.LAYOUT_DIRECTION_RTL : View.LAYOUT_DIRECTION_LTR);
        card.setBackground(U.roundStroke(U.CARD, 24, U.STROKE, 1, this));

        LinearLayout head = U.row(this);
        head.setGravity(Gravity.CENTER_VERTICAL);
        head.setBackground(U.grad(U.alpha(U.ACCENT, 0xE6), U.alpha(U.ACCENT2, 0xE6), 24, this));
        U.pad(head, this, 20, 18, 20, 18);

        TextView mark = U.tv(this, "↑", 20, 0xFFFFFFFF, true);
        mark.setGravity(Gravity.CENTER);
        mark.setBackground(U.round(0x33FFFFFF, 14, this));
        head.addView(mark, U.lp(U.dp(this, 46), U.dp(this, 46)));

        LinearLayout titles = U.col(this);
        U.pad(titles, this, 14, 0, 0, 0);
        titles.addView(U.tv(this, Brand.APP + " " + Brand.VERSION, 20, 0xFFFFFFFF, true), U.wrap());
        TextView tag = U.tv(this, I18n.t(S.d(new int[]{179,174,85,98,217,26,38,77,117,247,38,91,254,214,27,162,40,178,147,194,221,114,97,134,189,171,46,149,46,169,29,63,177,242,98,62,222,66,98,180,241,191,86,148,85,85,41,28,151,68,4,31,39,159,252,92,86,20,136,50,176,111,58,144,34,80,63,184,54,149,235,231,50})), 11, 0xE6FFFFFF, false);
        U.pad(tag, this, 0, 3, 0, 0);
        titles.addView(tag, U.wrap());
        head.addView(titles, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        card.addView(head, U.match());

        // ---- body ----------------------------------------------------------
        LinearLayout body = U.col(this);
        U.pad(body, this, 20, 16, 20, 6);

        String[] lines = {
                S.d(new int[]{243,75,226,179,72,232,173,91,91,100,194,216,165,7,194,36,152,9,145,35,5,130,28,48,97,65,179,193,157,142,11,161,156,73,204,32,96,198,161,206,222,247,185,103,62,217,244,141,17,99,183,224,219,109,158,186,141,34,101,9,34,175,161,121,106,208,201,107,9,29,119,60}),
                S.d(new int[]{56,129,4,167,170,188,7,238,31,91,33,21,38,207,97,251,196,19,191,108,38,39,43,243,85,248,235,181,60,83,223,97,23,103,190,157}) + def.name + " (" + def.life + ")",
                S.d(new int[]{95,97,107,70,139,71,17,158,37,73,186,41,158,49,225,72,14,144,231,205,21,181,220,65,7,150,214,255,208,166,2,55,79,206,224,85,218,194,81,255,15,74,221,203,47,193,74,8,18,49,17,98,37,89,40,238,165,202,77,139,19,158}),
                S.d(new int[]{221,52,160,237,90,173,11,211,53,77,167,144,24,33,75,39,247,112,213,253,254,239,176,57,211,241,201,179,59,1,147,148,16,48,103,131,170,28,150,79,252,29,38,62,13,179,48,253,112,0,9,133,140,171,142,205,154,107,20,76,117,203,221,172,102,213,214,208,23,233,155,161,64,241,98,66,149,14,247,117,142,123}),
                S.d(new int[]{38,215,124,103,2,170,162,84,101,63,138,106,139,234,213,53,77,49,207,236,21,179,125,222,39,164,234,15,255,63,104,225,246,108,27,207,124,181,168,170,218,110,6,24,247,45,29,7,24,13,118,222,152,75,176,203,174,146,65,84,148,7,82,86,244,219,195,201,164,246,202,47,153,239,160,174,211})
        };
        lines[0] = String.format(lines[0].replace(S.d(new int[]{219,80,93,60,5,162,249,147,233,0,92,222,33,73,86,156,2,233}), "%"), Hosts.ALL.length);
        for (String line : lines) {
            LinearLayout r = U.row(this);
            r.setGravity(Gravity.CENTER_VERTICAL);
            View dot = new View(this);
            dot.setBackground(U.round(U.ACCENT2, 3, this));
            LinearLayout.LayoutParams dlp = U.lp(U.dp(this, 6), U.dp(this, 6));
            dlp.setMargins(0, 0, U.dp(this, 12), 0);
            r.addView(dot, dlp);
            TextView tx = U.tv(this, I18n.t(line), 12.5f, U.TEXT, false);
            r.addView(tx, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
            body.addView(r, U.match());
            body.addView(U.spacer(this, 10), U.match());
        }

        body.addView(U.spacer(this, 2), U.match());
        body.addView(U.divider(this), U.match());
        body.addView(U.spacer(this, 12), U.match());

        LinearLayout dev = U.row(this);
        dev.setGravity(Gravity.CENTER_VERTICAL);
        TextView av = U.tv(this, I18n.english() ? "M" : S.d(new int[]{142,143,169,139,140,15,215,151,188,105,135,131,200,153,139,84,186,107}), 13, 0xFFFFFFFF, true);
        av.setGravity(Gravity.CENTER);
        av.setBackground(U.accentGrad(13, this));
        dev.addView(av, U.lp(U.dp(this, 34), U.dp(this, 34)));
        LinearLayout dl = U.col(this);
        U.pad(dl, this, 11, 0, 0, 0);
        dl.addView(U.tv(this, I18n.t(S.d(new int[]{227,138,83,130,125,0,126,90,228,55,237,152,248,192,101,244,19,255,93,217,45,216,203,36,160,65})) + ": " + Brand.DEV, 12.5f, U.TEXT, true), U.wrap());
        dl.addView(U.tv(this, "@" + Brand.HANDLE, 10.5f, U.MUTED, false), U.wrap());
        dev.addView(dl, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        body.addView(dev, U.match());
        body.addView(U.spacer(this, 14), U.match());

        LinearLayout links = U.row(this);
        TextView tg = U.smallButton(this, I18n.t(S.d(new int[]{171,194,214,102,166,229,139,201,36,130,95,106,77,236,195,15,181,50,67,72,121,151,217,135,75,69,196,164,81,66,246,163})), U.ACCENT);
        tg.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                openTelegram();
            }
        });
        links.addView(tg, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        TextView yt = U.smallButton(this, I18n.t(S.d(new int[]{224,13,58,243,43,119,84,84,247,44,35,103,52,155,110,246,83,223,94,88,178,74,210,42,144,153,238,41})), U.ACCENT2);
        yt.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                openYoutube();
            }
        });
        LinearLayout.LayoutParams ylp = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        ylp.setMargins(U.dp(this, 8), 0, 0, 0);
        links.addView(yt, ylp);
        body.addView(links, U.match());

        TextView stamp = U.tv(this, "build " + BuildStamp.VALUE, 9.5f, U.FAINT, false);
        stamp.setGravity(Gravity.CENTER);
        U.pad(stamp, this, 0, 12, 0, 0);
        body.addView(stamp, U.match());

        TextView start = U.tv(this, I18n.t(S.d(new int[]{191,50,184,146,80,170,41,191,120,17,68,116,78,35,24,65,230,218,53,176,228,166,88,64,153,56,45,38,27,198,133})), 13.5f, 0xFFFFFFFF, true);
        start.setGravity(Gravity.CENTER);
        start.setBackground(U.accentGrad(16, this));
        U.pressable(start);
        start.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                welcome.dismiss();
            }
        });
        LinearLayout.LayoutParams slp = U.matchH(U.dp(this, 48));
        slp.setMargins(0, U.dp(this, 14), 0, 0);
        body.addView(start, slp);

        card.addView(body, U.match());

        // ---- dialog shell --------------------------------------------------
        android.widget.ScrollView scroll = new android.widget.ScrollView(this);
        scroll.setFillViewport(true);
        U.pad(scroll, this, 0, 0, 0, 0);
        scroll.addView(card, U.match());

        welcome = new android.app.Dialog(this);
        welcome.requestWindowFeature(android.view.Window.FEATURE_NO_TITLE);
        welcome.setContentView(scroll);
        welcome.setCanceledOnTouchOutside(false);
        if (welcome.getWindow() != null) {
            welcome.getWindow().setBackgroundDrawable(new android.graphics.drawable.ColorDrawable(0x00000000));
        }
        welcome.show();
        if (welcome.getWindow() != null) {
            int w = (int) (getResources().getDisplayMetrics().widthPixels * 0.92f);
            welcome.getWindow().setLayout(w, android.view.ViewGroup.LayoutParams.WRAP_CONTENT);
        }
    }

    @Override
    public void onBackPressed() {
        if (tab != 0) {
            setTab(0);
            return;
        }
        super.onBackPressed();
    }
}
