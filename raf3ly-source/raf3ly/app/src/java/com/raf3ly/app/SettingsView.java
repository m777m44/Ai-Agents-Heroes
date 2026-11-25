package com.raf3ly.app;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;

/** Tab 3: platforms catalog, developer credits, options, backup. */
public class SettingsView {

    public final ScrollView root;
    private final MainActivity act;
    private final LinearLayout box;

    private String hostQuery = "";
    private String hostFilter = S.d(new int[]{195,187,208,244,147,171,154,215,129,195,5,119,109,114,77,158,219,147,61,119,8,158,232,91});

    public SettingsView(MainActivity a) {
        act = a;
        Context c = a;
        root = new ScrollView(c);
        root.setBackgroundColor(U.BG);
        root.setFillViewport(true);
        box = U.col(c);
        U.pad(box, c, 16, 4, 16, 30);
        root.addView(box, U.match());
        refresh();
    }

    public void refresh() {
        box.removeAllViews();
        Context c = act;

        box.addView(devCard(c));
        box.addView(U.spacer(c, 16));

        box.addView(U.sectionHead(c, S.d(new int[]{80,17,171,37,57,128,35,242,130,179,22,36,104,128,247,1,141,244,214,133,208,126,7,144,12,71,215,174,240,131,60,76,69,58,214,205,85,195,232}) + Hosts.ALL.length + ")", null, null));
        box.addView(platformsSection(c));
        box.addView(U.spacer(c, 16));

        box.addView(U.sectionHead(c, S.d(new int[]{160,39,162,128,71,116,111,35,249,82,219,226,27,86,190,60,171,42,98,50,82,156,242,187,197,102,199,141,40,194,128,103,149,200,99}), null, null));
        box.addView(customCard(c));
        box.addView(U.spacer(c, 16));

        box.addView(U.sectionHead(c, S.d(new int[]{71,235,116,190,68,80,72,121,168,138,168,152,182,162,108,129,31,112,17,24,65,93,181,231,140,156,98,225,106,154,206,175,221,7,61,141,184,174,213}), null, null));
        box.addView(uploadOptions(c));
        box.addView(U.spacer(c, 16));

        box.addView(U.sectionHead(c, S.d(new int[]{9,185,56,109,127,130,69,170,159,215,179,111,122,232,17,131,186,29,234,17,125,14,82,119,79,28,231,229,107,105,194,120,31,103,103,232,59,217,199,206,169,148,185,220,90}), null, null));
        box.addView(backupCard(c));
        box.addView(U.spacer(c, 16));

        box.addView(U.sectionHead(c, S.d(new int[]{24,237,213,62,246,200,9,174,161,114,233,6,185,81,52,137,43,198,255,81,146,152,218,40,107,69,185,234,65,197,85,193,153,139,195,34,90}), null, null));
        box.addView(dangerCard(c));
        box.addView(U.spacer(c, 18));
        box.addView(about(c));
    }

    // ---------------- developer ----------------

    private View devCard(Context c) {
        LinearLayout card = U.col(c);
        card.setBackground(U.heroBg(c));
        U.pad(card, c, 16, 16, 16, 15);

        LinearLayout top = U.row(c);
        LinearLayout avatar = U.col(c);
        avatar.setGravity(Gravity.CENTER);
        avatar.setLayoutParams(U.lp(U.dp(c, 44), U.dp(c, 44)));
        avatar.setBackground(U.round(0x3DFFFFFF, 22, c));
        avatar.addView(U.tv(c, I18n.english() ? "M" : S.d(new int[]{116,190,192,176,32,196,62,154,128,44,70,59,166,93,229,156,92,103}), 18, 0xFFFFFFFF, true));
        top.addView(avatar);

        LinearLayout names = U.col(c);
        LinearLayout.LayoutParams nlp = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        nlp.setMargins(U.dp(c, 11), 0, 0, 0);
        names.addView(U.tv(c, S.d(new int[]{254,211,115,68,36,172,167,165,193,109,83,104,185,212,146,61,27,250,224,53,167,136,220,27,88,63,35,22,218,250,241,245}) + Brand.DEV, 14, 0xFFFFFFFF, true));
        TextView sub = U.tv(c, "@" + Brand.HANDLE + " · " + Brand.VERSION, 10.5f, 0xCCFFFFFF, false);
        U.pad(sub, c, 0, 3, 0, 0);
        names.addView(sub);
        top.addView(names, nlp);
        card.addView(top);

        LinearLayout links = U.row(c);
        U.pad(links, c, 0, 13, 0, 0);

        TextView tg = U.tv(c, S.d(new int[]{45,34,229,204,234,19,152,16,231,75,123,196,251,111,207,174,82,56,20,138,131,202,110,139,165,229,21,110,239,97,212,136}), 11.5f, 0xFF0B0E14, true);
        tg.setGravity(Gravity.CENTER);
        tg.setBackground(U.round(0xFFFFFFFF, 14, c));
        U.pad(tg, c, 0, 9, 0, 9);
        tg.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.openTelegram();
            }
        });
        links.addView(tg, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        TextView yt = U.tv(c, S.d(new int[]{113,147,87,202,55,161,58,78,222,119,46,28,128,18,34,167,130,208,228,170,12,95,220,133,147,129,16,17}), 11.5f, 0xFFFFFFFF, true);
        yt.setGravity(Gravity.CENTER);
        yt.setBackground(U.round(0x33FFFFFF, 14, c));
        U.pad(yt, c, 0, 9, 0, 9);
        LinearLayout.LayoutParams ylp = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        ylp.setMargins(U.dp(c, 8), 0, 0, 0);
        yt.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.openYoutube();
            }
        });
        links.addView(yt, ylp);
        card.addView(links);
        return card;
    }

    // ---------------- platforms ----------------

    private View platformsSection(Context c) {
        LinearLayout wrap = U.col(c);

        EditText search = new EditText(c);
        search.setHint(I18n.t(S.d(new int[]{245,101,134,46,172,41,57,93,28,181,56,120,32,8,162,80,240,223,70,149,45,113,138,186,173,77,123,64,11,193,218,223,152,67,214,6,251,199,205,38,254})));
        search.setTextSize(12.5f);
        search.setTextColor(U.TEXT);
        search.setHintTextColor(U.FAINT);
        search.setSingleLine(true);
        search.setText(hostQuery);
        search.setBackground(U.roundStroke(U.CARD, 14, U.STROKE, 1, c));
        U.pad(search, c, 13, 9, 13, 9);
        wrap.addView(search, U.match());
        search.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int a, int b, int cc) {
            }

            @Override
            public void onTextChanged(CharSequence s, int a, int b, int cc) {
                hostQuery = s.toString().trim();
                renderHostList();
            }

            @Override
            public void afterTextChanged(Editable s) {
            }
        });

        LinearLayout chips = U.row(c);
        for (final String f : Hosts.CATEGORIES) {
            TextView chip = U.chip(c, f, f.equals(hostFilter));
            LinearLayout.LayoutParams lp = U.wrap();
            lp.setMargins(0, 0, U.dp(c, 6), 0);
            chip.setLayoutParams(lp);
            chip.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    hostFilter = f;
                    refresh();
                }
            });
            chips.addView(chip);
        }
        LinearLayout.LayoutParams clp = U.matchH(LinearLayout.LayoutParams.WRAP_CONTENT);
        clp.setMargins(0, U.dp(c, 9), 0, 0);
        wrap.addView(U.hscroll(c, chips), clp);

        hostListBox = U.col(c);
        LinearLayout.LayoutParams hlp = U.match();
        hlp.setMargins(0, U.dp(c, 10), 0, 0);
        wrap.addView(hostListBox, hlp);
        renderHostList();
        return wrap;
    }

    private LinearLayout hostListBox;

    private void renderHostList() {
        if (hostListBox == null) return;
        Context c = act;
        hostListBox.removeAllViews();
        int shown = 0;
        for (Hosts.Host h : Hosts.ALL) {
            if (!S.d(new int[]{94,140,197,202,66,114,249,155,201,203,49,210,32,225,86,175,155,100,200,91,205,139,8,34}).equals(hostFilter)) {
                if (S.d(new int[]{244,46,250,77,249,226,243,222,173,187,107,77,234,243,0,133,218,152,197,74,50,138,97,140,215,74,16,252,165,194,13,148}).equals(hostFilter)) {
                    if (!h.verified) continue;
                } else if (!hostFilter.equals(h.category())) {
                    continue;
                }
            }
            if (!hostQuery.isEmpty()) {
                String q = hostQuery.toLowerCase();
                if (!h.name.toLowerCase().contains(q) && !h.domain.toLowerCase().contains(q)) continue;
            }
            shown++;
            hostListBox.addView(hostRow(c, h), U.match());
            LinearLayout.LayoutParams lp = U.match();
            lp.setMargins(0, 0, 0, U.dp(c, 8));
            hostListBox.getChildAt(hostListBox.getChildCount() - 1).setLayoutParams(lp);
        }
        if (shown == 0) {
            TextView none = U.tv(c, S.d(new int[]{20,53,66,1,178,79,232,5,184,145,224,22,170,219,243,53,183,253,41,115,23,99,220,170,203,46,78,229,34,63,246,150,206,16,80,228,159,111,137,243,57,143,252,166,162,58,65,8,241,208,85,213,222}), 12, U.FAINT, false);
            none.setGravity(Gravity.CENTER);
            U.pad(none, c, 0, 18, 0, 18);
            hostListBox.addView(none);
        }
    }

    private View hostRow(final Context c, final Hosts.Host h) {
        boolean active = act.prefs.host().equals(h.id);
        LinearLayout card = U.col(c);
        card.setBackground(active ? U.roundStroke(U.alpha(U.ACCENT, 0x22), 18, U.ACCENT, 1.4f, c)
                : U.roundStroke(U.CARD, 18, U.STROKE, 1, c));
        U.pad(card, c, 13, 12, 13, 12);

        LinearLayout top = U.row(c);

        LinearLayout badge = U.col(c);
        badge.setGravity(Gravity.CENTER);
        badge.setLayoutParams(U.lp(U.dp(c, 34), U.dp(c, 34)));
        badge.setBackground(U.round(active ? U.alpha(U.ACCENT, 0x33) : U.CARD2, 11, c));
        badge.addView(U.icon(c, h.permanent ? R.drawable.ic_star : R.drawable.ic_server,
                active ? U.ACCENT2 : U.MUTED, 16));
        top.addView(badge);

        LinearLayout texts = U.col(c);
        LinearLayout.LayoutParams tlp = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        tlp.setMargins(U.dp(c, 11), 0, 0, 0);

        LinearLayout nameRow = U.row(c);
        nameRow.addView(U.tv(c, h.name, 13, U.TEXT, true));
        if (h.verified) {
            TextView v = U.tv(c, S.d(new int[]{182,237,21,191,118,233,90,145,116,144,179,66,196,190,132,10,75,35,167,146,216,145,146,218,181,169,143,187,246,147,146,107}), 8.5f, U.SUCCESS, true);
            nameRow.addView(v);
        }
        texts.addView(nameRow);

        TextView note = U.tv(c, h.note, 10, U.MUTED, false);
        U.pad(note, c, 0, 3, 0, 0);
        texts.addView(note);
        top.addView(texts, tlp);

        LinearLayout right = U.col(c);
        right.setGravity(Gravity.CENTER);
        TextView life = U.tv(c, h.life, 9.5f, active ? U.ACCENT2 : U.SUB, true);
        life.setBackground(U.round(active ? U.alpha(U.ACCENT, 0x33) : U.CARD2, 20, c));
        U.pad(life, c, 7, 3, 7, 3);
        right.addView(life);

        TextView kind = U.tv(c, h.kindLabel(), 8.5f, h.direct ? U.SUCCESS : U.WARN, true);
        U.pad(kind, c, 0, 3, 0, 0);
        right.addView(kind);
        top.addView(right);

        card.addView(top);

        card.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.prefs.setHost(h.id);
                act.haptic();
                act.rebuildAll();
                act.toast(S.d(new int[]{123,193,144,228,173,4,229,100,164,206,117,29,16,138,151,179,58,3,51,86,216,58,18,151,250,249,75,139,29,40}) + h.name);
            }
        });
        U.pressable(card);
        return card;
    }

    // ---------------- custom host ----------------

    private View customCard(Context c) {
        LinearLayout card = U.card(c);
        card.addView(U.tv(c, S.d(new int[]{6,143,237,117,145,170,7,61,92,43,81,10,169,44,205,60,80,150,27,16,60,198,134,27,90,230,221,66,235,254,113,35,167,255,21,27,90,110,42,73,159,123,21,237,210,255,204,234,88,150,247,143,209,122,138,252,99,188,86,91,163,60,15,201,244,157,112,75,247,51,66,241,187,100,82,8,217,85,64,82,166,78,85,133,22,133,202,222,108,255,149,224,16,77,193,174,17,188,105,125,232,173,169,169,192,51,206,244,130,112,54,110,133,213,104,28,2,26,111}),
                10.5f, U.MUTED, false));

        LinearLayout row = U.row(c);
        LinearLayout.LayoutParams rlp = U.matchH(LinearLayout.LayoutParams.WRAP_CONTENT);
        rlp.setMargins(0, U.dp(c, 11), 0, 0);
        card.addView(row, rlp);

        final EditText name = input(c, S.d(new int[]{158,247,217,250,18,250,223,229,54,81,185,36,69,23,35,233,225,62,123,197,255,9,38,210,178,200,195,62,151,41,53,55,115,146,249}), act.prefs.customName());
        row.addView(name, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        LinearLayout.LayoutParams n2 = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        n2.setMargins(U.dp(c, 7), 0, 0, 0);
        final EditText field = input(c, S.d(new int[]{196,29,107,116,133,235,242,144,241,96,23,120,151,194,15,70,45,208,135,120,126,208,99,216,234,196,216,195,90,63,207,112,196,73,32,6,123,61,173,177}), act.prefs.customField());
        row.addView(field, n2);

        LinearLayout.LayoutParams u2 = U.matchH(LinearLayout.LayoutParams.WRAP_CONTENT);
        u2.setMargins(0, U.dp(c, 7), 0, 0);
        final EditText url = input(c, S.d(new int[]{28,186,17,117,41,187,51,58,250,36,156,65,96,95,74,142,143,126,202,25,234,78,76,142,188,149,214,212,194,70,34,113,239,37,206,235,83,3,221,162,132,224,46,19,107,204}), act.prefs.customUrl());
        card.addView(url, u2);

        LinearLayout btns = U.row(c);
        LinearLayout.LayoutParams blp = U.matchH(LinearLayout.LayoutParams.WRAP_CONTENT);
        blp.setMargins(0, U.dp(c, 10), 0, 0);
        card.addView(btns, blp);

        TextView save = U.button(c, S.d(new int[]{205,72,210,236,63,81,179,105,17,127,255,63,33,74,236,115,192,227,186,154,196,229,27,26,53,254,191,2,86,227,82,214,45,40,172,118,193,83,212}), true);
        save.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String nm = name.getText().toString().trim();
                String u = url.getText().toString().trim();
                String f = field.getText().toString().trim();
                if (nm.isEmpty() || !u.startsWith("http")) {
                    act.toast(S.d(new int[]{78,65,84,221,27,36,195,67,144,150,62,90,63,186,54,97,57,103,204,22,51,162,100,141,123,12,192,97,14,83,216,16,154,233,15,201,67,229,177,50,60,173,5,175,155,247,122,161,49,132,203,237,20,38,63,26,184,26,9}));
                    return;
                }
                act.prefs.setCustom(nm, u, f.isEmpty() ? "file" : f);
                act.prefs.setHost("custom:x");
                act.toast(S.d(new int[]{224,228,163,32,204,80,217,174,212,128,103,147,6,97,129,170,188,90,188,241,149,153,193,111,5,164,55,112,30,112,87,39,106,10,22,50,190,247,64,205,192,129,217,101,117}));
                act.rebuildAll();
            }
        });
        btns.addView(save, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        TextView del = U.button(c, S.d(new int[]{124,0,13,176,4,14,188,238,209,180,226,48,161,216,17,208,34,39,83,20,17,96}), false);
        del.setTextColor(U.DANGER);
        LinearLayout.LayoutParams dlp = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        dlp.setMargins(U.dp(c, 8), 0, 0, 0);
        del.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.prefs.clearCustom();
                if (act.prefs.host().startsWith("custom")) act.prefs.setHost(Hosts.CATBOX.id);
                act.toast(S.d(new int[]{14,57,139,121,41,37,117,228,123,38,206,247,142,12,252,210,152,145,46,215,175,22,94,96,85,63,184,73}));
                act.rebuildAll();
            }
        });
        btns.addView(del, dlp);

        if (act.prefs.customName() != null && !act.prefs.customName().isEmpty()) {
            TextView cur = U.tv(c, S.d(new int[]{117,154,70,8,234,79,59,50,33,55,14,84,240,234,98,117,3,234,34,24,181,250,55,23,237,145,21,236,146,7,179,219,92,22,238,127,109,187,186,115,20,214,58}) + act.prefs.customName(), 10, U.SUCCESS, true);
            U.pad(cur, c, 0, 9, 0, 0);
            card.addView(cur);
        }
        return card;
    }

    private EditText input(Context c, String hint, String value) {
        EditText e = new EditText(c);
        e.setHint(I18n.t(hint));
        e.setText(value == null ? "" : value);
        e.setTextSize(11.5f);
        e.setSingleLine(true);
        e.setTextColor(U.TEXT);
        e.setHintTextColor(U.FAINT);
        e.setBackground(U.roundStroke(U.CARD2, 12, U.STROKE, 1, c));
        U.pad(e, c, 11, 8, 11, 8);
        return e;
    }

    // ---------------- options ----------------

    private View uploadOptions(Context c) {
        LinearLayout card = U.card(c);

        card.addView(U.tv(c, S.d(new int[]{80,248,51,196,236,65,161,9,88,10,2,182,120,189,184,153,51,168,230,55,104,105,211,100,152,52,228,44,189,0,255,16,135,67,125,9,164,36,44,113,64,188,253,15,222,239,221,60,121,143,230}), 12.5f, U.TEXT, true));
        TextView sub = U.tv(c, S.d(new int[]{122,60,126,158,152,70,40,123,190,157,221,254,215,11,60,175,127,138,48,87,201,49,175,149,59,128,23,195,207,244,232,191,201,51,143,255,124,134,165,13,192,111,209,172,214,94,239,104,50,208,182,135,249,253,74,10,62,45,56,248,85,221,91,144,246,45,186,195,176,232,229,165,85,198,74,189,125,193,255,128,40,94,9,161,61,148,147,84,109,87,17,140,99,30,145,115,207}), 10, U.MUTED, false);
        U.pad(sub, c, 0, 3, 0, 0);
        card.addView(sub);

        LinearLayout levels = U.row(c);
        U.pad(levels, c, 0, 9, 0, 0);
        for (int i = 0; i < 3; i++) {
            final int lv = i;
            TextView chip = U.chip(c, ImageCompressor.LEVELS[i], act.prefs.compression() == i);
            LinearLayout.LayoutParams lp = U.wrap();
            lp.setMargins(0, 0, U.dp(c, 6), 0);
            chip.setLayoutParams(lp);
            chip.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    act.prefs.setCompression(lv);
                    refresh();
                }
            });
            levels.addView(chip);
        }
        card.addView(levels);

        card.addView(U.divider(c));

        card.addView(U.tv(c, S.d(new int[]{240,224,207,152,91,223,116,109,89,213,79,210,161,53,32,211,181,60,113,187,38,188,97,94,62,230,204,245,150,122,214,121,111,179,44,209,164,221,124,232,81,150,70,128,33,38,214,206,97,135,155,250,236,155,221,119}), 12.5f, U.TEXT, true));
        LinearLayout par = U.row(c);
        U.pad(par, c, 0, 9, 0, 0);
        for (int i = 1; i <= 3; i++) {
            final int n = i;
            TextView chip = U.chip(c, n == 1 ? S.d(new int[]{9,215,77,167,177,7,36,212,136,125,164,246,184,208,228,120,93,213,62,74,80,5,149,242,86,53,145,153,159,136,146}) : n + S.d(new int[]{236,255,152,40,240,236,117,226,9,161,86,247,63,218,59,8,255,132,49,186,75,223,218,225,255,163,242}), act.prefs.parallel() == n);
            LinearLayout.LayoutParams lp = U.wrap();
            lp.setMargins(0, 0, U.dp(c, 6), 0);
            chip.setLayoutParams(lp);
            chip.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    act.prefs.setParallel(n);
                    refresh();
                }
            });
            par.addView(chip);
        }
        card.addView(par);

        card.addView(U.divider(c));
        card.addView(toggleRow(c, S.d(new int[]{113,147,143,141,189,2,213,107,30,5,89,194,56,122,149,105,35,253,197,38,43,33,233,116,0,24,163,218,169,195,252,241,45,73,230,81,254,215,105,200,240,27,63,245,177,228,89,137,245,66,181,25}), S.d(new int[]{64,235,130,241,0,237,51,54,192,126,73,252,4,40,65,8,88,34,192,118,66,171,244,72,161,134,132,122,101,98,249,169,233,252,28,45,184,8,203,227,242,30,210,74,232,169,137,9,30,183,254,136,81,220,47,191,142,29,202,95,8,42,168,132,183,236,8,222,44,8,156}),
                act.prefs.autoCopy(), new Setter() {
                    @Override
                    public void set(boolean v) {
                        act.prefs.setAutoCopy(v);
                    }
                }));
        card.addView(U.divider(c));
        card.addView(toggleRow(c, S.d(new int[]{82,167,220,231,156,122,253,232,138,171,14,63,108,42,168,112,84,181,201,153,16,16,172,225,131,247,114,56,142,9,81,197,158,2,151,32,190,45,182,156,96,24,203,101,38,152,182,109,186,252,104,164,130,95,85,123,235,99,243,175,190}), S.d(new int[]{18,203,76,105,253,114,196,238,134,117,100,93,248,150,92,185,65,192,29,12,182,55,162,103,155,115,68,107,25,106,54,54,245,167,222,213,101,157,120,68,138,29,115,57,56,37,250,99,43,183,174,104,174,248,145,212,222,92,1,61,221,11,255,4,128,132,101,50,46,66,9,91,188,204,209}),
                act.prefs.fallback(), new Setter() {
                    @Override
                    public void set(boolean v) {
                        act.prefs.setFallback(v);
                    }
                }));
        card.addView(U.divider(c));
        card.addView(toggleRow(c, S.d(new int[]{128,5,163,183,114,64,24,198,239,119,97,195,50,255,251,134,80,213,222,39,119,100,21,182,211,38,18,85,42,186,56,194,139,198,1,89,117,8,11,254,146,89,168,220,69,43,36,84}), S.d(new int[]{42,235,45,29,208,162,251,206,34,98,216,108,16,102,120,71,179,235,48,155,101,133,235,110,132,199,152,18,181,149,119,216,15,221,213,195,167,208,46,93,35,72,151,247,180}),
                act.prefs.haptics(), new Setter() {
                    @Override
                    public void set(boolean v) {
                        act.prefs.setHaptics(v);
                    }
                }));
        card.addView(U.divider(c));
        card.addView(toggleRow(c, S.d(new int[]{244,177,200,189,29,77,123,90,67,156,59,222,245,150,114,11,99,187,172,231,38,195,42,124,214,223,217,134,196,164,112,191,48}), S.d(new int[]{253,5,138,132,221,163,165,129,86,251,44,8,97,38,54,238,33,113,12,21,178,53,63,123,231,221,27,246,142,170,122,196,99,139,133,174,81,250,148,162,22,185,116,151,67,114,212,236,121,7,81,62,136,192,152,99,220,50,158,177,198}),
                act.prefs.keepHistory(), new Setter() {
                    @Override
                    public void set(boolean v) {
                        act.prefs.setKeepHistory(v);
                    }
                }));
        return card;
    }

    private interface Setter {
        void set(boolean v);
    }

    // ---------------- backup / danger / about ----------------

    private View backupCard(Context c) {
        LinearLayout card = U.card(c);
        card.addView(U.tv(c, S.d(new int[]{88,156,186,27,211,176,4,97,20,243,235,249,232,173,83,70,189,195,94,27,199,7,60,176,224,13,171,116,134,118,102,173,123,169,220,216,155,116,117,120,90,193,179,134,190,3,201,130,237,98,107,229,220,114,9,42,16,214,139,208,96,178,157,231,4,171,4,194,31,208,184,78,115,218,141,172,48,177,131,78,100,186,171,208,53,217,59,27,76,139,5,96,128,203,95,156,247,179,5,163,206,36,40}), 10.5f, U.MUTED, false));

        LinearLayout row = U.row(c);
        LinearLayout.LayoutParams rlp = U.matchH(LinearLayout.LayoutParams.WRAP_CONTENT);
        rlp.setMargins(0, U.dp(c, 11), 0, 0);
        card.addView(row, rlp);

        TextView export = U.button(c, S.d(new int[]{57,167,27,167,133,203,86,168,14,246,57,63,50,5,1,22,152,111,31,117,34,61,181,60,103,178}), true);
        export.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.copy(act.store.exportJson(), S.d(new int[]{92,170,124,96,83,233,113,20,93,193,221,209,53,255,191,156,14,72,238,106,36,100,178,161,165,227,217,244,209,95,136,216,186,254,129,46,180,201,102,73,176,15,115,135,87,124,127,87,39,146,65,186,234,63,42,251,47,204,213,84,123,23,98,230}));
            }
        });
        row.addView(export, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        TextView importBtn = U.button(c, S.d(new int[]{127,157,160,153,202,213,13,49,73,227,21,207,115,71,157,147,116,248,71,241,206,30,138,240,76,222,253,53,172,23}), false);
        LinearLayout.LayoutParams ilp = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        ilp.setMargins(U.dp(c, 8), 0, 0, 0);
        importBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String clip = act.paste();
                if (clip == null || !clip.trim().startsWith("[")) {
                    act.toast(S.d(new int[]{20,9,173,81,124,207,29,224,255,125,211,100,1,229,184,138,188,83,227,53,35,190,136,234,4,30,61,39,229,96,253,4,229,78,159,156,42,78,218,8,211,66,70,191,87,219,78,45,133,181,81,207,251,64,100,90,44,125,149,69,190,78,21,156,26,108,79,0,20,253,90,115,42,140}));
                    return;
                }
                int n = act.store.importJson(clip);
                act.toast(S.d(new int[]{168,108,113,148,106,206,105,209,110,121,19,247,174,78,88,190,239,52,50,210,65,5,17,90,53,143,192}) + n + S.d(new int[]{65,93,162,250,228,45,35,182,93,216,221,111,63,79,170,82,189,233,44,86,245,193,201,137,110,227,166}));
                act.refreshData();
            }
        });
        row.addView(importBtn, ilp);
        return card;
    }

    private View dangerCard(Context c) {
        LinearLayout card = U.card(c);
        TextView clear = U.button(c, S.d(new int[]{34,110,69,246,155,95,54,51,152,53,79,232,146,108,196,100,88,43,110,201,164,50,166,127,79,166,211,50,163,23,221,179,239,81,120,203,75,94,101,174,250,142,127,70}), false);
        clear.setTextColor(U.DANGER);
        clear.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                new AlertDialog.Builder(act)
                        .setTitle(I18n.t(S.d(new int[]{231,45,158,123,207,200,203,91,218,221,216,225,127,137,42,113,84,236,130,202,111,62,157,222,27,108,85,168,147,198,43,112,99})))
                        .setMessage(I18n.t(S.d(new int[]{82,75,92,27,57,86,236,233,98,62,26,208,43,206,132,169,148,103,33,239,172,120,169,149,20,123,49,175,103,233,199,199,22,180,243,205,149,95,234,137,184,196,159,180,35,7,74,176,112,253,80,175,103,97,74,101,71,13,122,112,210,115,73,132,152,8,154,183,47,114,239,252,239,202,171,2,96,42,233,237,252,24,100,81,211,202,182,57,46,252,198,84,103,185,49,197,35,129,148,182,206,0,220,29,97,58,67,205,219,119,75,67,78,123,220,65,204,213})))
                        .setNegativeButton(I18n.t(S.d(new int[]{92,25,133,35,210,84,90,47,49,29,56,127,91,49,94,78,116,111,255,56,174,189,116,31,4,244})), null)
                        .setPositiveButton(I18n.t(S.d(new int[]{255,248,138,83,219,162,30,81,83,247,47,245,101,248,228,161,87,238,87,42,83,204,129,3})), new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface d, int w) {
                                act.store.clear();
                                act.toast(S.d(new int[]{146,248,104,95,218,239,180,117,146,195,102,43,44,242,217,86,45,224,92,61,45,195,199,177,71,26,51,157,184,41}));
                                act.refreshData();
                            }
                        }).show();
            }
        });
        card.addView(clear, U.match());
        return card;
    }

    private View about(Context c) {
        LinearLayout card = U.col(c);
        card.setGravity(Gravity.CENTER_HORIZONTAL);
        card.setBackground(U.roundStroke(U.CARD, 20, U.STROKE, 1, c));
        U.pad(card, c, 16, 18, 16, 16);

        LinearLayout logo = U.col(c);
        logo.setGravity(Gravity.CENTER);
        logo.setLayoutParams(U.lp(U.dp(c, 48), U.dp(c, 48)));
        logo.setBackground(U.accentGrad(14, c));
        logo.addView(U.icon(c, R.drawable.ic_up, 0xFFFFFFFF, 23));
        card.addView(logo);

        TextView name = U.tv(c, Brand.APP, 16, U.TEXT, true);
        U.pad(name, c, 0, 10, 0, 0);
        card.addView(name);

        card.addView(U.tv(c, S.d(new int[]{201,168,38,196,141,124,48,121,80,30,169,59,221,10,176,121,98,106,140,232,242,11,4,212,193,79,237,35,164,150,79}) + Brand.VERSION + "  ·  build " + BuildStamp.VALUE + "  ·  " + Hosts.ALL.length
                + S.d(new int[]{233,163,10,107,170,140,91,236,131,184,46,184,179,28,177,48,175,203,205,118,74,248,82,44,5,98,249,38,68,231,163,196,83,197,171,108,147,109,164,123,92,64,118,131,203,198,73}) + Brand.DEV, 10.5f, U.MUTED, false));

        TextView links = U.tv(c, S.d(new int[]{41,2,242,179,178,14,18,191,238,123,163,4,143,52,159,144,115,22,240,149,234,167,168,203,59,93,164,31,91,115,203,21,34,99,60,91,8,31,134}) + Brand.HANDLE + S.d(new int[]{243,4,19,201,239,152,175,95,235,192,225,149,121,203,109,50,47,103,0,112,180,127,23,254,244,219,203,5,234,156,169,248,232,73,88,172,221,12,166,74,34,48,190,90})
                + Brand.HANDLE, 10.5f, U.ACCENT2, true);
        links.setGravity(Gravity.CENTER);
        links.setTextDirection(View.TEXT_DIRECTION_RTL);
        U.pad(links, c, 0, 10, 0, 0);
        links.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.openTelegram();
            }
        });
        card.addView(links);

        TextView note = U.tv(c, S.d(new int[]{51,166,189,192,122,23,190,103,58,172,230,3,160,88,84,4,50,163,95,205,99,35,133,215,39,91,219,49,155,101,4,4,167,168,11,0,113,226,116,70,238,216,30,134,160,211,228,91,245,28,174,168,8,167,82,182,182,222,17,64,165,27,233,58,139,1,117,99,240,235,65,97,1,232,157,22,170,34,210,188,188,182,103,105,214,152,127,124,28,137,8,213,7,189,219,237,243,65,120,202,161,44,12,98,103,13,142,105,179,94,103,226,91,20,150,165,225,185,58,193,49,7,46,47,74,115,232,122,216,249,9,139,183,72,90,9,190,235,118,7,217,124,206,80,73,51,93,75,53,229,94,145,91,185,88,139,169,226,61,222,88}),
                10, U.FAINT, false);
        note.setGravity(Gravity.CENTER);
        U.pad(note, c, 0, 10, 0, 0);
        card.addView(note);

        LinearLayout stats = U.row(c);
        U.pad(stats, c, 0, 12, 0, 0);
        stats.addView(pill(c, act.store.count() + S.d(new int[]{222,142,204,196,146,140,159,4,213,220,183,29,143,145,231,78,14,35,30,183,226,135,139})));
        stats.addView(pill(c, U.size(act.store.bytes())));
        stats.addView(pill(c, act.store.downloads() + S.d(new int[]{215,157,50,98,234,177,211,179,181,238,247,176,45,18,231,173,177,47,247,4,93,201,115,168,190,66,173})));
        card.addView(stats);
        return card;
    }

    private View pill(Context c, String text) {
        TextView t = U.tv(c, text, 10, U.SUB, true);
        t.setBackground(U.round(U.CARD2, 20, c));
        U.pad(t, c, 9, 4, 9, 4);
        LinearLayout.LayoutParams lp = U.wrap();
        lp.setMargins(0, 0, U.dp(c, 6), 0);
        t.setLayoutParams(lp);
        return t;
    }

    private View toggleRow(Context c, String title, String sub, boolean checked, final Setter setter) {
        LinearLayout row = U.row(c);
        LinearLayout texts = U.col(c);
        texts.addView(U.tv(c, title, 12.5f, U.TEXT, true));
        TextView s = U.tv(c, sub, 10, U.MUTED, false);
        U.pad(s, c, 0, 3, 0, 0);
        texts.addView(s);
        row.addView(texts, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        final Switch sw = new Switch(c);
        sw.setChecked(checked);
        sw.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setter.set(sw.isChecked());
            }
        });
        row.addView(sw);
        return row;
    }
}
