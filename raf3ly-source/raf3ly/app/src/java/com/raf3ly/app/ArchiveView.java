package com.raf3ly.app;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;

/** Tab 2: archive with search, filters, sorting, favorites, multi-select and downloads. */
public class ArchiveView {

    public final FrameLayout root;
    private final MainActivity act;
    private final ScrollView scroll;
    private final LinearLayout box;
    private final LinearLayout listBox;
    private final LinearLayout chipsRow;
    private final TextView countLabel;
    private final EditText search;

    private String filter = S.d(new int[]{52,118,253,175,121,12,210,105,134,22,170,22,173,164,218,6,53,67,188,56,99,79,58,166});
    private String query = "";
    private boolean selectMode = false;
    private final LinkedHashSet<String> selected = new LinkedHashSet<>();

    private final String[] filters = {S.d(new int[]{76,133,88,95,171,188,162,221,252,124,127,142,176,149,229,255,113,229,63,174,155,106,124,169}), S.d(new int[]{172,49,126,2,170,239,88,27,74,160,163,136,59,115,35,90,97,13,243,64,147,142,47,15,119,71,101,53,207,40}), S.d(new int[]{109,240,161,199,81,1,56,108,23,157,185,135,25,56,27,153,223,153,66,122,247,1}), S.d(new int[]{191,216,64,98,73,105,133,163,230,173,209,253,70,195,47,173,250,229,223,126,19,127,44,98,145,140,107,183,31,69}), S.d(new int[]{174,55,57,251,97,40,200,243,170,224,137,223,247,202,148,74,196,148,97,149,35,7,12,200,164,222}), S.d(new int[]{33,81,8,155,240,79,228,37,210,226,97,228,48,93,164,183,108,106,142,168,115,165,195,79,250,195})};

    private LinearLayout dlCard;
    private TextView dlName, dlMeta;
    private ProgressBar dlBar;

    public ArchiveView(MainActivity a) {
        act = a;
        Context c = a;
        root = new FrameLayout(c);
        root.setBackgroundColor(U.BG);

        scroll = new ScrollView(c);
        scroll.setFillViewport(true);
        box = U.col(c);
        U.pad(box, c, 16, 4, 16, 30);
        scroll.addView(box, U.match());
        root.addView(scroll, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT));

        LinearLayout head = U.row(c);
        head.addView(U.tv(c, S.d(new int[]{203,11,155,215,236,46,235,242,33,18,130,97,80,30,241,109,11,9,91,214,22,230,56,240,155,56,106,85,46,147,113,27}), 17, U.TEXT, true), U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        countLabel = U.tv(c, "", 11, U.MUTED, false);
        head.addView(countLabel);
        box.addView(head);

        // search + sort
        LinearLayout searchRow = U.row(c);
        LinearLayout.LayoutParams srp = U.matchH(LinearLayout.LayoutParams.WRAP_CONTENT);
        srp.setMargins(0, U.dp(c, 11), 0, 0);
        box.addView(searchRow, srp);

        search = new EditText(c);
        search.setHint(I18n.t(S.d(new int[]{62,189,57,218,74,150,255,139,197,144,76,117,205,199,25,100,253,130,105,129,29,82,91,79,238,164,85,82,56,242,185,13,87,192,38,213,111,18,14,252,220,110,3,248,137,63,140,189,239,67,142,239,3,55,87,224,144,251})));
        search.setTextSize(12.5f);
        search.setTextColor(U.TEXT);
        search.setHintTextColor(U.FAINT);
        search.setSingleLine(true);
        search.setBackground(U.roundStroke(U.CARD, 14, U.STROKE, 1, c));
        U.pad(search, c, 14, 10, 14, 10);
        searchRow.addView(search, U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        search.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int a1, int b, int c1) {
            }

            @Override
            public void onTextChanged(CharSequence s, int a1, int b, int c1) {
                query = s.toString().trim();
                renderList();
            }

            @Override
            public void afterTextChanged(Editable s) {
            }
        });

        ImageView sortBtn = U.iconButton(c, R.drawable.ic_sort, U.SUB);
        LinearLayout.LayoutParams sbp = U.lp(U.dp(c, 40), U.dp(c, 40));
        sbp.setMargins(U.dp(c, 9), 0, 0, 0);
        sortBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showSort();
            }
        });
        searchRow.addView(sortBtn, sbp);

        chipsRow = U.row(c);
        LinearLayout.LayoutParams clp = U.matchH(LinearLayout.LayoutParams.WRAP_CONTENT);
        clp.setMargins(0, U.dp(c, 11), 0, 0);
        box.addView(U.hscroll(c, chipsRow), clp);

        listBox = U.col(c);
        LinearLayout.LayoutParams llp = U.match();
        llp.setMargins(0, U.dp(c, 12), 0, 0);
        box.addView(listBox, llp);

        // download progress
        dlCard = U.card(c);
        dlCard.setVisibility(View.GONE);
        dlCard.setBackground(U.roundStroke(0xF2121826, 18, U.ACCENT, 1, c));
        dlName = U.tv(c, "", 12.5f, U.TEXT, true);
        dlName.setSingleLine(true);
        dlName.setEllipsize(android.text.TextUtils.TruncateAt.MIDDLE);
        dlCard.addView(dlName);
        dlBar = U.progress(c, 6);
        LinearLayout.LayoutParams blp = U.matchH(U.dp(c, 6));
        blp.setMargins(0, U.dp(c, 8), 0, 0);
        dlCard.addView(dlBar, blp);
        dlMeta = U.tv(c, "", 10.5f, U.ACCENT2, false);
        U.pad(dlMeta, c, 0, 6, 0, 0);
        dlCard.addView(dlMeta);

        FrameLayout.LayoutParams flp = new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.WRAP_CONTENT);
        flp.setMargins(U.dp(c, 16), 0, U.dp(c, 16), U.dp(c, 16));
        flp.gravity = Gravity.BOTTOM;
        root.addView(dlCard, flp);

        refresh();
    }

    public void refresh() {
        renderChips();
        renderList();
    }

    // ---------- header bits ----------

    private void renderChips() {
        chipsRow.removeAllViews();
        for (final String f : filters) {
            TextView chip = U.chip(act, f, f.equals(filter));
            LinearLayout.LayoutParams lp = U.wrap();
            lp.setMargins(0, 0, U.dp(act, 7), 0);
            chip.setLayoutParams(lp);
            chip.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    filter = f;
                    renderChips();
                    renderList();
                }
            });
            chipsRow.addView(chip);
        }
    }

    private void showSort() {
        final String[] keys = {"new", "old", "big", "dl", "fav"};
        final String[] names = {S.d(new int[]{200,78,37,194,133,79,234,39,115,124,39,51,231,26,13,0,72,115,230,186,245,111,249,182,253,55,8,81,18,24,254,156,29,150,80,209,238,251,8}), S.d(new int[]{237,131,180,95,232,102,241,56,71,169,148,92,73,128,205,171,179,141,66,128,219,168,184,100,169,102,231,70,139,163,181,66,228,118,156,58,59,77,153}), S.d(new int[]{189,232,10,92,178,80,241,156,125,216,39,0,15,213,46,124,2,83,239,5,230,29,102,113,6,46,124,38,220,22,232,87,166,82,20,55,148,45,10}), S.d(new int[]{157,193,22,160,227,51,153,165,197,211,69,92,206,35,116,53,96,195,253,143,164,139,227,192,194,105,213,67,140,228,209,173,235,110,158,196,127,178,238,107,197,229,37}), S.d(new int[]{4,248,253,38,175,210,150,66,170,153,104,90,246,149,121,40,32,245,200,210,180,81,128,246,232,139,151,89,217,64,6,223,130,17,219,6,120,207,62,17,159})};
        int cur = 0;
        for (int i = 0; i < keys.length; i++) if (keys[i].equals(act.prefs.sort())) cur = i;
        new AlertDialog.Builder(act)
                .setTitle(I18n.t(S.d(new int[]{86,111,89,150,162,106,80,108,150,72,5,33,86,66,182,186,148,88,248,114,98,22,252,63,254,87,61,103,155,28,85,35,190,215,40,217,210,99,178,45,95,21,102,240,136})))
                .setSingleChoiceItems(names, cur, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface d, int which) {
                        act.prefs.setSort(keys[which]);
                        d.dismiss();
                        renderList();
                    }
                }).show();
    }

    private List<Entry> filtered() {
        List<Entry> all = act.store.sorted(act.prefs.sort());
        ArrayList<Entry> out = new ArrayList<>();
        for (Entry e : all) {
            if (S.d(new int[]{229,200,235,246,147,109,120,206,234,22,149,46,42,68,112,254,35,193,80,157,230,29,227,197,44,33,37,84,173,47}).equals(filter)) {
                if (!e.fav) continue;
            } else if (!S.d(new int[]{96,21,97,193,105,154,142,119,95,133,27,127,170,138,134,95,7,183,6,109,124,139,183,204}).equals(filter) && !filter.equals(e.kind())) {
                continue;
            }
            if (!query.isEmpty()) {
                String q = query.toLowerCase();
                if (!e.name.toLowerCase().contains(q) && !e.url.toLowerCase().contains(q)) continue;
            }
            out.add(e);
        }
        return out;
    }

    private void renderList() {
        listBox.removeAllViews();
        List<Entry> shown = filtered();
        long bytes = 0;
        for (Entry e : shown) bytes += e.size;
        countLabel.setText(U.num(shown.size()) + S.d(new int[]{45,14,115,194,230,96,79,74,187,224,189,97,229,166,250,131,17,216,7,93,181,53,189,106,224,123,168}) + U.size(bytes));

        if (selectMode) listBox.addView(selectionBar());

        if (shown.isEmpty()) {
            LinearLayout empty = U.col(act);
            empty.setGravity(Gravity.CENTER);
            U.pad(empty, act, 0, 44, 0, 44);
            empty.addView(U.icon(act, query.isEmpty() ? R.drawable.ic_folder : R.drawable.ic_search, U.FAINT, 44));
            TextView t = U.tv(act, query.isEmpty() ? S.d(new int[]{122,231,38,216,223,242,193,199,57,211,208,47,252,205,34,19,90,217,221,113,64,52,206,97,71,245,230,197,218,1,158,255,178,199,149,243,12,40,215,57,213,106,229,253,114,113,42,35,41}) : S.d(new int[]{163,32,4,202,72,101,14,191,173,124,8,107,184,189,122,134,22,216,105,104,85,15,4,214,189,215,191,215,119,73,232,239,253,214,206}), 13, U.FAINT, false);
            t.setGravity(Gravity.CENTER);
            U.pad(t, act, 0, 10, 0, 0);
            empty.addView(t);
            listBox.addView(empty);
            return;
        }

        if (shown.size() > 1 && !selectMode) {
            TextView copyAll = U.button(act, S.d(new int[]{91,234,175,2,147,40,113,150,70,53,178,139,139,27,69,153,156,6,125,7,192,152,68,163,92,13,33,19,95,135,46,56,5,98,41,215,82,233,80,202,59,188,43,200,91,205}) + shown.size() + ")", false);
            copyAll.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    StringBuilder sb = new StringBuilder();
                    for (Entry e : filtered()) sb.append(e.url).append("\n");
                    act.copy(sb.toString().trim(), S.d(new int[]{73,36,233,227,85,167,18,94,231,229,224,127,47,192,253,40,114,49,157,63,34,167,108,89,63,54,138}) + filtered().size() + S.d(new int[]{77,128,196,47,4,95,68,222,50,123,43,108,211,250,226,26,216,195,213,127,105,167,88,160,112,119,25,243,169}));
                }
            });
            LinearLayout.LayoutParams lp = U.matchH(LinearLayout.LayoutParams.WRAP_CONTENT);
            lp.setMargins(0, 0, 0, U.dp(act, 11));
            listBox.addView(copyAll, lp);
        }

        for (final Entry e : shown) {
            listBox.addView(item(e), U.match());
            LinearLayout.LayoutParams lp = U.match();
            lp.setMargins(0, 0, 0, U.dp(act, 9));
            listBox.getChildAt(listBox.getChildCount() - 1).setLayoutParams(lp);
        }
    }

    private View selectionBar() {
        Context c = act;
        LinearLayout bar = U.row(c);
        bar.setBackground(U.roundStroke(U.alpha(U.ACCENT, 0x26), 16, U.alpha(U.ACCENT, 0x88), 1, c));
        U.pad(bar, c, 12, 10, 12, 10);

        bar.addView(U.tv(c, selected.size() + S.d(new int[]{130,82,194,221,153,71,92,40,118,82,42,228,131,32,108,224,162,89,133,214,209,63,121,253,30}), 12, U.TEXT, true),
                U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        TextView copy = U.smallButton(c, S.d(new int[]{41,226,4,47,228,5,42,148,41,186,136,123,51,62,43,140,73,22,140,143,17,142}), U.ACCENT2);
        copy.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                StringBuilder sb = new StringBuilder();
                for (String id : selected) {
                    Entry e = act.store.get(id);
                    if (e != null) sb.append(e.url).append("\n");
                }
                act.copy(sb.toString().trim(), S.d(new int[]{208,93,163,210,183,5,246,176,132,38,239,14,162,203,88,75,242,84,13,77,129,125,172,184,71,92,223,104,17,33}));
                exitSelect();
            }
        });
        bar.addView(copy);

        TextView fav = U.smallButton(c, "★", U.STAR);
        LinearLayout.LayoutParams f2 = U.wrap();
        f2.setMargins(U.dp(c, 6), 0, 0, 0);
        fav.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                for (String id : selected) act.store.setFav(id, true);
                exitSelect();
                renderList();
            }
        });
        bar.addView(fav, f2);

        TextView del = U.smallButton(c, S.d(new int[]{214,254,112,59,178,71,59,91,47,194,238,81,121,185,34,88,117,72,234,218,67,196}), U.DANGER);
        LinearLayout.LayoutParams d2 = U.wrap();
        d2.setMargins(U.dp(c, 6), 0, 0, 0);
        del.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                new AlertDialog.Builder(act)
                        .setTitle(I18n.t(S.d(new int[]{147,112,115,184,238,82,133,242,209,74,126,97,12,210,221,169,115,196,61,242,65,234,99})) + selected.size() + S.d(new int[]{126,93,90,55,95,207,104,105,103,211,208,204,173,253,227,171,178,94,111,76,93,56,100}))
                        .setMessage(I18n.t(S.d(new int[]{149,115,12,164,146,66,91,235,92,167,7,22,222,53,160,184,120,46,231,69,234,149,78,213,31,144,182,127,222,107,80,142,242,116,178,201,20,135,62,239,179,137,187,37,68,156,151,129,89,26,94,163,168,196,142,210,84,21,111,66,121,82,6,220,159,160,203,209,73,158,80,143,107,188,207,243,200,57,209,6,253,142,41,225,94,157,81,26,128,54,4,138,98,59,181,195,85,87,224,232,27,62,235,143,209,165,143,26,131,67,145,119,230,157,152,226,189,186,141,83,167,75,67,73,129,198,52,11})))
                        .setNegativeButton(I18n.t(S.d(new int[]{32,241,81,44,174,151,9,50,24,90,213,210,152,224,44,165,57,151,151,5,242,91,44,125,234,57})), null)
                        .setPositiveButton(I18n.t(S.d(new int[]{160,202,49,236,23,98,168,242,251,54,149,7,27,67,138,231,17,58,105,109,20,117})), new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface d, int w) {
                                act.store.removeAll(new ArrayList<>(selected));
                                act.toast(S.d(new int[]{243,132,139,75,118,237,228,6,47,77,163,187,89,11,142,157,154,120,40,244,110,37,38,117,164,37,91,95,215,171,193,119,192,60}));
                                exitSelect();
                                act.refreshData();
                            }
                        }).show();
            }
        });
        bar.addView(del, d2);

        ImageView close = U.iconButton(c, R.drawable.ic_close, U.SUB);
        LinearLayout.LayoutParams c2 = U.lp(U.dp(c, 32), U.dp(c, 32));
        c2.setMargins(U.dp(c, 6), 0, 0, 0);
        close.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                exitSelect();
            }
        });
        bar.addView(close, c2);

        LinearLayout wrap = U.col(c);
        wrap.addView(bar, U.match());
        wrap.addView(U.spacer(c, 10));
        return wrap;
    }

    private void exitSelect() {
        selectMode = false;
        selected.clear();
        renderList();
    }

    private View item(final Entry e) {
        final Context c = act;
        boolean picked = selected.contains(e.id);

        LinearLayout card = U.col(c);
        card.setBackground(picked ? U.roundStroke(U.alpha(U.ACCENT, 0x1F), 18, U.ACCENT, 1.4f, c)
                : U.roundStroke(U.CARD, 18, U.STROKE, 1, c));
        U.pad(card, c, 13, 13, 13, 11);

        LinearLayout top = U.row(c);

        FrameLayout thumbWrap = new FrameLayout(c);
        thumbWrap.setBackground(U.roundStroke(U.CARD2, 14, U.STROKE, 1, c));
        thumbWrap.setClipToOutline(true);
        thumbWrap.setLayoutParams(U.lp(U.dp(c, 52), U.dp(c, 52)));
        ImageView thumb = new ImageView(c);
        thumb.setScaleType(ImageView.ScaleType.CENTER_CROP);
        thumb.setLayoutParams(new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT));
        thumbWrap.addView(thumb);
        if (e.isImage()) {
            ImageLoader.load(thumb, e.url, U.dp(c, 52));
        } else {
            ImageView ph = U.icon(c, e.isVideo() ? R.drawable.ic_bolt : R.drawable.ic_file, U.ACCENT2, 21);
            FrameLayout.LayoutParams plp = new FrameLayout.LayoutParams(U.dp(c, 21), U.dp(c, 21));
            plp.gravity = Gravity.CENTER;
            thumbWrap.addView(ph, plp);
        }
        top.addView(thumbWrap);

        LinearLayout texts = U.col(c);
        LinearLayout.LayoutParams tlp = U.lpw(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        tlp.setMargins(U.dp(c, 11), 0, 0, 0);
        TextView nm = U.tv(c, e.name, 12.5f, U.TEXT, true);
        nm.setSingleLine(true);
        nm.setEllipsize(android.text.TextUtils.TruncateAt.MIDDLE);
        texts.addView(nm);

        LinearLayout metaRow = U.row(c);
        U.pad(metaRow, c, 0, 5, 0, 0);
        TextView sizeChip = U.tv(c, U.size(e.size), 9.5f, U.SUB, true);
        sizeChip.setBackground(U.round(U.CARD3, 20, c));
        U.pad(sizeChip, c, 7, 2, 7, 2);
        metaRow.addView(sizeChip);

        TextView hostChip = U.tv(c, " " + e.host, 9.5f, U.ACCENT2, true);
        U.pad(hostChip, c, 5, 2, 0, 2);
        metaRow.addView(hostChip);

        TextView dls = U.tv(c, " ⬇" + e.downloads, 9.5f, U.MUTED, true);
        metaRow.addView(dls);
        texts.addView(metaRow);

        texts.addView(U.tv(c, e.kind() + " · " + U.ago(e.ts), 9.5f, U.FAINT, false));
        top.addView(texts, tlp);

        final ImageView star = U.icon(c, R.drawable.ic_star, e.fav ? U.STAR : U.FAINT, 19);
        star.setLayoutParams(U.lp(U.dp(c, 34), U.dp(c, 34)));
        star.setPadding(U.dp(c, 7), U.dp(c, 7), U.dp(c, 7), U.dp(c, 7));
        star.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                act.store.toggleFav(e.id);
                act.haptic();
                renderList();
            }
        });
        top.addView(star);
        card.addView(top);

        TextView linkTv = U.tv(c, e.url, 10, 0xFF4E7FA8, false);
        linkTv.setSingleLine(true);
        linkTv.setEllipsize(android.text.TextUtils.TruncateAt.MIDDLE);
        U.pad(linkTv, c, 0, 9, 0, 0);
        card.addView(linkTv);

        if (!selectMode) {
            LinearLayout actions = U.row(c);
            LinearLayout.LayoutParams alp = U.matchH(LinearLayout.LayoutParams.WRAP_CONTENT);
            alp.setMargins(0, U.dp(c, 9), 0, 0);
            card.addView(actions, alp);

            final ImageView copy = U.iconButton(c, R.drawable.ic_copy, U.SUB);
            copy.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    act.copy(e.url, S.d(new int[]{201,214,137,232,85,179,232,211,223,248,45,154,214,200,143,241,103,216,69,32,102,138,253,250,251,140,16,30,127,148,140,109,116,131,3,36,112,12,107,161,106,10,230,231}));
                }
            });
            actions.addView(copy);

            final ImageView dl = U.iconButton(c, R.drawable.ic_dl, U.ACCENT2);
            dl.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    startDownload(e);
                }
            });
            addWithGap(actions, dl);

            ImageView share = U.iconButton(c, R.drawable.ic_share, U.SUB);
            share.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    act.share(e.url);
                }
            });
            addWithGap(actions, share);

            ImageView open = U.iconButton(c, R.drawable.ic_eye, U.SUB);
            open.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    act.openViewer(e);
                }
            });
            addWithGap(actions, open);

            ImageView del = U.iconButton(c, R.drawable.ic_trash, U.DANGER);
            del.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    confirmDelete(e);
                }
            });
            addWithGap(actions, del);
        } else {
            card.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    if (selected.contains(e.id)) selected.remove(e.id);
                    else selected.add(e.id);
                    if (selected.isEmpty()) selectMode = false;
                    renderList();
                }
            });
        }

        card.setOnLongClickListener(new View.OnLongClickListener() {
            @Override
            public boolean onLongClick(View v) {
                selectMode = true;
                selected.add(e.id);
                act.haptic();
                renderList();
                return true;
            }
        });
        return card;
    }

    private void addWithGap(LinearLayout parent, View child) {
        Context c = act;
        LinearLayout.LayoutParams lp = U.lp(U.dp(c, 36), U.dp(c, 36));
        lp.setMargins(U.dp(c, 7), 0, 0, 0);
        parent.addView(child, lp);
    }

    private void confirmDelete(final Entry e) {
        new AlertDialog.Builder(act)
                .setTitle(I18n.t(S.d(new int[]{64,85,116,176,247,12,14,150,233,205,151,154,146,91,186,122,60,101,7,15,34,193,243,42,83,151,102,214,32,20,243,170,0,195,5,87,120,214,183,229,39,177,187,151})))
                .setMessage(I18n.t(S.d(new int[]{86,156,43,9,74,119,58,113,77,136,193,16,137,178,188,155,81,245,117,63,199,1,192,251,230,129,50,244,140,41,247,199,173,114,218,246,80,51,106,147,51,241,22,254,112,19,75,124,197,153,196,23,208,110,53,3,138,111,207,225,93,255,66,89,34,122,139,30,82,251,44,98,76,182,98,132,216,141,33,175,116,63,86,132,18,194,185,13,172,162,69,175,136,2,239,216,28,244,29,192,24,74,237,152,197,180,140,187,215,177,32,250,187,85,44,41,248,9,132,83,117,165,81,133,22,246,155,229,143,192,226,23,26,5,49,217,29,10,150,198,102,165})) + e.name)
                .setNegativeButton(I18n.t(S.d(new int[]{93,235,3,224,225,185,230,98,137,26,116,253,243,90,166,5,185,248,186,55,43,168,152,50,22,73})), null)
                .setPositiveButton(I18n.t(S.d(new int[]{107,120,67,233,148,173,60,227,88,240,126,210,207,6,212,207,156,9,52,97,118,252})), new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface d, int w) {
                        act.store.remove(e.id);
                        act.refreshData();
                    }
                }).show();
    }

    private void startDownload(final Entry e) {
        dlCard.setVisibility(View.VISIBLE);
        dlName.setText(e.name);
        dlBar.setProgress(0);
        dlMeta.setText(I18n.t(S.d(new int[]{118,16,35,139,238,253,128,189,166,38,119,188,51,122,252,221,60,19,227,179,50,174,163,133,251,61,86,224,76,144,62,79,61,77,209,45,128,168,79,179,192,183})));
        act.store.bumpDownload(e.id);

        Downloader.start(act, e, new Downloader.Cb() {
            @Override
            public void onProgress(long done, long total, long bps, long eta) {
                dlBar.setProgress(total > 0 ? (int) Math.min(1000, done * 1000 / total) : 300);
                dlMeta.setText(U.size(done) + (total > 0 ? " / " + U.size(total) : "")
                        + " · " + U.speed(bps) + (eta > 0 ? S.d(new int[]{241,177,212,178,219,175,197,171,179,121,199,140,225,252,48,8,213,10,80,54,253,8,99,201,149,169,75,121,62}) + U.dur(eta) : ""));
            }

            @Override
            public void onDone(String message, android.net.Uri uri) {
                dlBar.setProgress(1000);
                dlMeta.setText(I18n.t(message));
                act.toast(S.d(new int[]{210,227,20,24,207,60,200,59,201,214,190,46,211,129,11,193,137,0,214,171,179,34,25,112,228,215,12,214,122,19,70,1,175,95,226,11,42,65,156}));
                act.haptic();
                renderList();
                hideLater();
            }

            @Override
            public void onError(String message) {
                dlMeta.setText(I18n.t(S.d(new int[]{62,190,65,219,149,217,204,98,193,222,44,254,202,75,181,213,167,206,104,92,248,239,204,197})) + message);
                act.toast(S.d(new int[]{255,148,59,217,198,25,28,55,160,40,51,116,121,70,144,105,86,250,140,115,124,193,138,58,245,10,59,181,117,216,23,220,149,82,59,47,208}));
                hideLater();
            }
        });
    }

    private void hideLater() {
        root.postDelayed(new Runnable() {
            @Override
            public void run() {
                dlCard.setVisibility(View.GONE);
            }
        }, 3500);
    }
}
