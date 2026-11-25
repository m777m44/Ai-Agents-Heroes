package com.raf3ly.app;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Catalog of anonymous upload platforms + upload implementations. */
public class Hosts {

    public static class Host {
        public final String id;
        public final String name;
        public final String domain;
        public final String life;      // retention label
        public final String note;
        public final boolean recommended;
        public final boolean verified; // tested & worked
        public final boolean permanent; // S.d(new int[]{86,88,196,56,209,16,72,11,244,62,222,110,177,174,241,39,214,61,52,32,106,238,10,84})
        public final boolean direct;    // url serves the file itself
        public final boolean imageOnly;

        Host(String id, String name, String domain, String life, String note,
             boolean recommended, boolean verified, boolean permanent, boolean direct, boolean imageOnly) {
            this.id = id;
            this.name = name;
            this.domain = domain;
            this.life = life;
            this.note = note;
            this.recommended = recommended;
            this.verified = verified;
            this.permanent = permanent;
            this.direct = direct;
            this.imageOnly = imageOnly;
        }

        public String kindLabel() {
            return direct ? S.d(new int[]{200,108,92,21,48,221,225,218,43,230,33,201,202,176,67,10,210,122,244,165,49,66,68,167,223,234,67,185,46,249,201,24,101,89,123}) : S.d(new int[]{215,28,96,219,191,117,59,204,123,5,239,249,58,113,137,172,40,62,251,52,115,141,108,190,74,192,55,31,56,118,85,170,228,243,24});
        }

        /** دائم / طويل / متوسط / مؤقت / صور */
        public String category() {
            if (imageOnly) return S.d(new int[]{34,232,72,34,245,250,48,201,34,49,19,105,173,37,181,75,161,158,213,72,234,119});
            if (permanent) return S.d(new int[]{190,250,41,26,11,243,13,242,81,239,243,26,94,6,225,177,207,225,67,68,143,69,190,110});
            if (life.contains("30") || life.contains("60")) return S.d(new int[]{149,173,183,138,204,206,15,117,106,202,135,97,17,110,119,243,181,254,24,24,22,141,0,53});
            if (life.contains("10") || life.contains("7") || life.contains("6") || life.contains(S.d(new int[]{251,5,43,213,74,164,139,244,19,28,64,90,5,150,71,104,220,202,158,20,167,242,8,229,188,147}))) return S.d(new int[]{154,136,0,98,147,13,156,205,224,253,131,171,193,158,103,125,255,83,176,91,185,161,71,29,249,77});
            return S.d(new int[]{61,184,45,249,189,253,75,172,76,234,42,51,7,105,133,18,186,65,135,60,58,197,78,218});
        }
    }

    // ---- catalog (tested 2026-11) ----
    public static final Host CATBOX = new Host(S.d(new int[]{216,182,92,153,188,77,42,220,161,14,145,218,95,212,53,238,38,122,144,8,77,198}), S.d(new int[]{236,245,38,221,229,136,212,112,52,69,252,25,36,163,121,246,124,49,60,10,250,147,63,14,135,22}), S.d(new int[]{195,111,174,123,143,15,39,40,161,171,108,93,52,116,71,100,135,247,214,57,7,79,92,128,159,50}), S.d(new int[]{41,189,80,9,171,152,137,84,222,53,140,171,7,255,162,229,109,198,13,210,44,203,108,141}),
            S.d(new int[]{99,83,26,51,46,49,113,32,169,181,251,89,158,201,2,66,255,120,252,230,208,22,151,221,5,201,245,52,11,202,250,30,38,99,245,100,156,235,100,37,13,167,244,98,131,71,27,191,56,120,241,60,38,196,72,175,184,11,129,143,20,135,141,124,183,173,254,206,154,113,51,172,73,86,66,138,212,71,180,170,219,171,250,243,103,135,157,122,80,144,192,83,104,45,159,229,15,169,85,173,206}), true, false, true, true, false);
    public static final Host X0 = new Host(S.d(new int[]{243,40,214,177,48,164,94,213,141,134,187,111,46,242,1,104,26,15}), S.d(new int[]{67,85,141,45,105,29,30,84,37,151,190,117,75,155,171,144,52,98,168,97,162}), S.d(new int[]{76,95,93,72,31,4,228,165,119,39,80,165,171,93,1,85,81,52,62,98,127}), S.d(new int[]{61,66,31,86,12,242,24,78,29,136,104,200,93,89,145,173,204,11,109,27,142,78,132,80,79,244}),
            S.d(new int[]{232,232,111,37,216,75,134,239,175,113,229,160,105,15,100,169,196,228,149,209,70,56,119,242,221,229,166,232,47,223,155,144,18,36,97,9,254,157,0,44,218,230,45,1,219,209,54,189,146,245,51,90,195,10,11,210,183,145,28,38,30,64,214,16,57,182,188,254,214,48,227,84,183,254,109,147,2,87,66,86,8,81,179,96,151,124,134,231,135,136,114,67,96,155,146,108,78,103,183,124,236,139}), true, true, false, true, false);
    public static final Host POMF = new Host(S.d(new int[]{167,0,127,248,73,59,17,199,223,250,249,236,183,16,61,103,24,182,19,30}), S.d(new int[]{0,91,122,100,141,246,146,50,3,31,2,126,190,148,40,38,206,177,153,63,123,0,135,67,142,166,141,52}), S.d(new int[]{26,220,94,93,7,219,142,131,61,83,68,170,131,33,47,178,43,124,106,65,88,137,168,254,164,40,62,233,242}), S.d(new int[]{137,81,235,206,235,195,110,16,98,8,46,239,216,100,179,135,195,208,141,249,133,30,242,67,25}),
            S.d(new int[]{135,43,29,212,154,223,70,181,122,72,36,32,104,128,47,32,242,199,149,114,255,21,65,87,172,94,253,168,145,134,27,235,83,126,153,92,60,245,180,254,98,161,239,133,8,231,182,195,252,32,47,130,243,210,102,69,160,11,123,30,50,0,89,167,234,94,14,240}), false, true, false, true, false);
    public static final Host KAPPA = new Host(S.d(new int[]{80,247,168,229,41,223,177,43,226,7,218,85,186,32,35,167,180,70,244,72,253}), S.d(new int[]{168,132,72,64,26,188,33,63,10,156,12,61,135,100,26,84,237,158,183,169,251,36,174,108,189}), S.d(new int[]{185,138,167,145,11,207,211,108,149,158,232,191,131,108,38,183,102,162,147,203,80,233,192,188,215}), S.d(new int[]{64,215,47,23,221,46,80,117,102,44,62,139,50,192,10,132,21,245,205,162,192,128,126,220,58}),
            S.d(new int[]{87,138,44,63,203,43,24,78,125,38,223,71,33,195,198,146,173,250,216,96,179,176,198,161,70,139,195,42,138,218,77,117,169,255,54,205,42,207,206,48,42,233,220,8,189,0,17,37,230,80,205,111,99,122,175,95,230,45,77,11,147,75,101,5,201,255,223,232,168,196,145,85}), false, true, false, true, false);
    public static final Host ZERO = new Host(S.d(new int[]{50,40,21,251,20,158,174,251,22,255,203,93,147,218,243,128,246,17,60}), S.d(new int[]{76,162,214,149,220,197,210,136,152,119,94,186,124,246,39,97,228,131,209,162,241,119}), S.d(new int[]{136,83,254,143,10,89,190,245,197,218,164,236,223,48,49,53,32,196,107,33,67,254}), S.d(new int[]{52,119,230,25,247,56,10,7,216,247,228,142,63,135,99,229,202,11,29,125,42,141,83,147,225,107}),
            S.d(new int[]{9,184,253,113,140,160,174,133,29,93,174,4,66,53,119,191,83,24,209,40,17,1,120,51,43,191,21,142,0,199,166,71,178,81,71,17,111,235,19,58,95,82,172,183,237,140,100,17,94,115,231,146,130,203,40,217,33,220,236,31,39,131,85,68,64,245,82,182,196,106,157,121,19,84,78,153,206,35,25,134,206,94,27,229,200,33,204,128,246,235,1,245,176}), false, false, false, true, false);
    public static final Host FARS = new Host(S.d(new int[]{137,223,219,189,248,1,174,1,91,177,173,90,94,36,154,113,164,160,106,173}), S.d(new int[]{188,53,182,244,184,155,90,62,80,105,13,211,121,43,247,243,64,10,189,53,168,225,92}), S.d(new int[]{76,85,114,227,101,34,200,0,4,225,147,59,207,121,166,136,19,26,102,225,132,17,67}), S.d(new int[]{61,66,7,76,146,59,205,40,129,242,23,107,225,57,105,149,139,193,92,75,201,122,206,67,17}),
            S.d(new int[]{249,219,65,39,208,201,48,156,186,217,91,167,75,36,127,210,36,191,141,224,253,186,219,34,82,19,2,99,13,204,75,154,44,154,63,173,92,78,155,222,149,77,245,244,214,18,99,211,247,56,204,204,129,146,154,166,251,88,134,134,197,195,154,154,204,148,167,172,127,218,239,14,181,54,38,248,179,249,31,166,184,141,95,76,39,201,95,59,144,234,227,236,246}), false, false, false, true, false);
    public static final Host GOFILE = new Host(S.d(new int[]{68,210,145,133,192,121,213,203,196,246,25,115,178,157,127,229,195,177,223,29,3,107}), S.d(new int[]{114,184,7,61,31,224,65,25,179,191,77,6,205,67,220,44,216,20,3,149,213,211,70,224,15}), S.d(new int[]{54,222,226,61,254,11,198,239,201,132,101,11,91,124,215,189,210,252,254,71,35,247,59,69,248}), S.d(new int[]{4,146,196,226,29,182,174,213,235,249,195,131,227,236,102,181,137,230,172,246,66,5,120,134,65,184,40}),
            S.d(new int[]{142,52,243,249,9,14,251,3,121,97,217,247,133,76,113,199,194,223,34,13,172,229,233,72,227,203,172,244,195,227,164,233,79,234,231,160,39,250,6,31,21,121,155,101,49,212,6,170,205,174,7,216,65,204,32,172,246,64,34,146,236,227,236,188,14,166,0,125,242,66,35,197,82,21,93,107,208,227,80,169,22,234,57}), false, true, false, false, false);
    public static final Host QUAX = new Host(S.d(new int[]{252,128,43,122,13,147,118,150,50,108,188,224,244,184,190,249,2,123,212,18}), S.d(new int[]{241,195,221,192,142,104,252,219,5,5,62,73,121,197,44,115,35,99,83,209,193}), S.d(new int[]{153,190,243,52,255,210,81,28,148,216,61,137,198,40,69,152,96,140,187,244,61}), S.d(new int[]{134,131,28,24,147,54,252,232,155,32,216,240,129,131,136,226,130,243,230,29,254,42,123,151,118,91}),
            S.d(new int[]{147,35,45,30,88,128,69,253,236,255,159,133,226,99,102,124,154,102,180,123,62,129,157,230,38,148,47,12,167,229,252,43,71,191,236,169,117,152,176,48,61,166,166,163,1,248,89,67,231,95,245,21,147,88,28,104,238,182,187,196,141,152,40,139,224}), false, true, false, false, false);
    public static final Host FILEBIN = new Host(S.d(new int[]{25,230,158,108,96,254,24,46,10,76,212,139,42,143,247,210,33,255,64,144,10,71,110}), S.d(new int[]{127,138,26,178,21,225,17,24,202,46,91,174,227,164,55,168,156,176,44,145,107,88,36,214,130,29,128}), S.d(new int[]{238,129,63,104,74,37,83,81,205,156,102,59,80,174,160,38,243,65,15,188,32,254,216,99,105,20,48}), S.d(new int[]{212,204,241,124,18,28,58,17,85,0,186,72,140,33,120,36,8,144,21,45,155,194,208,228,112,112}),
            S.d(new int[]{51,150,180,99,80,86,241,176,189,6,76,33,157,95,214,142,54,136,170,108,96,193,162,13,243,195,160,46,57,119,154,209,146,46,22,241,250,143,94,56,129,32,115,230,187,77,100,99,111,105,225,201,75,25,213,14,198,146,251,134,252,201,20,199,169,14,12,250,90,36,74,209,89,177,253,9,197,56,19,20,230,84,184,112,195,253,108,205,25,127,77,173,17,69,165,105,174,241,164,65,139,41,20,163,127,204,94,74,251,138,2,135,56,131,233,192,214}), false, true, false, false, false);
    public static final Host LITTER = new Host(S.d(new int[]{181,55,246,243,138,217,173,171,190,33,181,232,100,9,91,252,94,23,201,211,157,139}), S.d(new int[]{0,16,58,152,71,225,233,96,174,81,255,59,197,77,43,56,84,164,183,90,220,100,246,108,101,65,159,168,117,21,236,108,85,194,45,118}), S.d(new int[]{167,16,213,67,121,203,254,214,117,1,33,39,27,156,103,201,158,3,221,252,216,64,200,6,128,141,67,63,61,13,199,15,6,192,25,86}), S.d(new int[]{248,124,80,216,47,238,157,78,21,112,35,38,236,34,141,210,43,97,38,243,148,210,46,145,144,214}),
            S.d(new int[]{207,22,130,36,250,167,228,76,102,40,49,255,31,132,38,170,81,219,33,130,160,28,100,21,19,129,50,236,218,95,243,61,250,119,49,28,108,249,204,117,214,17,76,249,164,122,219,134,245,33,165,137,153,103,250,4,26,209,131,240,163,4,244,26}), false, false, false, true, false);
    public static final Host PIXHOST = new Host(S.d(new int[]{123,239,240,73,63,208,230,48,107,217,60,71,8,99,13,34,124,150,255,166,83,225,70}), S.d(new int[]{130,226,210,22,186,94,15,74,133,37,145,242,66,189,83,71,6,52,19,37,110,203,226,131,53,14}), S.d(new int[]{41,248,80,207,153,44,243,76,41,40,35,30,93,249,177,247,51,63,205,150,30,142,84,162,3,56}), S.d(new int[]{176,153,88,161,222,253,143,54,87,18,130,7,77,235,9,242,180,85,239,104,63,173,238,108}),
            S.d(new int[]{116,202,232,58,197,56,26,156,44,15,48,247,164,254,171,147,2,54,22,194,154,128,79,102,3,12,70,94,191,137,157,234,135,10,30,193,160,248,30,171,108,227,1,38,92,152,211,4,5,190,81,29,76,46,37,1,117,224,28,177,234,175,120,207,155,123,70,112,251,18,22,111,164,73,87,140,63,120,219,44,228,83,227,12,14,143,126,137,168,138,63,120,139,81}), false, false, true, true, true);
    public static final Host PIXELDRAIN = new Host(S.d(new int[]{193,213,210,157,136,74,79,22,137,173,154,46,60,222,10,72,164,218,231,45,103,249,189,218,127,179}), S.d(new int[]{157,219,129,30,73,204,167,5,12,221,95,13,27,31,48,155,158,237,205,167,174,175,233,182,117,14,94,160,157,125}), S.d(new int[]{82,194,28,116,115,200,234,231,215,102,45,23,213,51,165,155,33,159,10,165,127,227,224,196,211,84,0,69,82,191}), S.d(new int[]{122,239,72,172,241,163,215,63,131,69,227,50,5,82,249,155,5,116,142,100,90,140,96,133,104}),
            S.d(new int[]{5,94,148,139,62,121,209,22,10,88,223,154,193,141,161,13,156,35,35,162,214,240,211,165,46,75,90,231,223,1,65,212,54,91,165,208,174,237,170,109,194,207,160,36,56,30,153,157,199,45,128,204,149,72,121,210,202,27,134,180,10,142,237,238,247,162,90,54,63,98,140,73,176,7,44,218,116,222,200,61,35,219,211,142,190,92,111,170}), false, false, false, false, false);
    public static final Host UGUU = new Host(S.d(new int[]{117,147,54,167,111,225,85,23,53,181,101,114,150,252,230,80,141,161,34,24}), S.d(new int[]{148,206,151,17,133,6,163,37,103,168,49,96,150,130,226,234,240,122,100,147,145,40,165}), S.d(new int[]{62,123,183,81,233,243,116,51,222,180,3,176,8,239,143,92,152,122,95,169,19,227,187}), S.d(new int[]{231,227,185,6,96,190,176,163,25,52,134,178,177,104,129,59,123,236,108,99,20,86,16,64,55,112,239,126}),
            S.d(new int[]{113,238,163,7,209,95,129,205,33,31,242,250,217,35,193,57,235,217,195,116,224,144,197,9,65,133,185,197,22,136,102,198,223,113,1,235,89,241,54,39,136,165,76,220,22,86,127,195,253,109,168,39,118,57,67,139,110,109,113,183,53}), false, true, false, true, false);
    public static final Host TMPFILES = new Host(S.d(new int[]{191,71,60,226,161,186,75,43,210,234,154,175,176,193,241,195,87,96,156,162,136,169,246,61}), S.d(new int[]{145,47,63,241,211,176,130,251,48,246,90,109,64,136,211,200,214,181,45,63,188,190,216,187,125,135,57,133}), S.d(new int[]{49,236,27,79,175,36,236,129,91,148,188,164,225,72,93,249,191,12,180,122,228,70,250,212,246,118,158,214}), S.d(new int[]{70,131,118,78,204,37,236,240,14,118,45,172,239,98,60,226,207,212,81,204,76,166,179,219}),
            S.d(new int[]{168,146,38,163,20,39,137,8,57,93,168,8,237,92,240,115,89,182,252,23,178,115,45,212,81,144,45,70,0,136,93,213,145,17,17,197,70,186,11,255,241,106,52,135,254,43,128,249,45,19,105,199,37,27,107,22,186,54,20,209,3,44,45,228,227,144,191,21,38,161,98,165,129,45,15,161,38,84,214,100,46,212,127,108,54,107,208,230,212,90,155,185,182,170,25,12,183,58,71,36,130,236,191,137,71,28}), false, true, false, true, false);

    public static final Host[] ALL = {
            CATBOX, X0, POMF, KAPPA, ZERO, FARS, GOFILE, QUAX,
            FILEBIN, LITTER, PIXHOST, PIXELDRAIN, UGUU, TMPFILES
    };

    public static final String[] CATEGORIES = {S.d(new int[]{191,42,137,129,176,164,238,1,110,7,132,136,76,44,111,253,80,243,16,218,96,14,118,33}), S.d(new int[]{128,175,58,185,193,179,222,71,176,56,35,140,200,236,13,72,81,203,57,190,160,124,244,163}), S.d(new int[]{114,33,143,30,199,121,96,178,181,99,225,134,7,138,232,99,83,26,45,152,36,139,175,189}), S.d(new int[]{245,170,23,180,223,202,214,56,63,124,12,8,196,125,147,18,132,69,146,27,119,205,117,215,205,176}), S.d(new int[]{52,55,73,243,28,70,177,62,114,227,33,252,158,233,219,62,208,233,109,122,168,210,8,136}), S.d(new int[]{39,131,128,77,230,147,168,225,122,108,96,187,168,115,172,60,165,123,124,224,180,235}), S.d(new int[]{3,190,174,127,146,83,76,94,33,99,106,40,156,215,107,24,178,94,184,40,160,8,243,121,21,144,246,159,159,122,0,112})};

    public static Host byId(String id) {
        if (id != null && id.startsWith("custom:")) return customHostFromId(id);
        for (Host h : ALL) if (h.id.equals(id)) return h;
        return CATBOX;
    }

    // ---------------- custom platform ----------------

    public static Host customHost(Prefs p) {
        String name = p.customName();
        if (name == null || name.trim().isEmpty()) return null;
        return new Host("custom:x", name, name, S.d(new int[]{171,201,19,206,149,27,33,157,206,124,149,249,200,121,168,122,52,166,183,204,46,124,59,74,141,2,176,87,71,235,154,46,115}),
                S.d(new int[]{23,58,178,53,55,112,71,130,176,44,35,168,251,65,99,108,70,26,121,135,180,172,188,249,39,111,81,5,80,169,80,59,153,224,103,185,30,194,153,95,247,44,76,33,255,57,0,14,218,224,121,239,92,30,121,144,175,226,165,150,150,238,153,160,240,208}), false, true, false, true, false);
    }

    private static Host customHostFromId(String id) {
        // custom is resolved through Prefs at upload time; placeholder keeps the API simple
        return new Host(id, S.d(new int[]{197,185,130,36,52,165,28,16,161,117,226,78,73,143,55,135,223,250,145,249,12,20,70,129,223,10,79,20,227,186,176,167,20,118,242}), "custom", S.d(new int[]{189,116,76,197,70,114,198,200,103,221,25,102,144,41,197,140,219,136,103,77,125,51,209,5,89,27,92,104,111,221,188,127,8}), "", false, true, false, true, false);
    }

    // ---------------- upload ----------------

    public static String upload(Host h, Prefs prefs, File f, String name, String mime, Net.Prog p) throws IOException {
        if (h.id != null && h.id.startsWith("custom:")) {
            return uploadCustom(prefs, f, name, mime, p);
        }

        if ("filebin".equals(h.id)) return filebin(f, name, mime, p);

        String endpoint;
        String field;
        LinkedHashMap<String, String> extra = new LinkedHashMap<>();

        switch (h.id.hashCode()) {
            case 3588274:
                endpoint = S.d(new int[]{187,53,194,247,205,233,55,114,140,15,26,163,220,21,168,86,154,80,104,65,168,129,125,224,199,129,95,172,24,200,141,24,89,7,77,217,201,212,69,164,57,112,148,86,50,82,255,126,208,27});
                field = "files[]";
                break;
            case 1560088512:
                endpoint = S.d(new int[]{208,175,205,12,108,174,57,140,255,202,228,240,239,37,112,78,107,46,158,196,249,12,244,145,201,91,114,33,94,206,249,5,198,227,19,231,145,86,87,201,87,191,212,39,50,169,29,201,37,180});
                field = "file";
                break;
            case 3481947:
                endpoint = S.d(new int[]{239,226,105,19,6,161,217,147,67,127,198,115,170,77,43,93,230,115,234,177,209,54,178,187,145,77,42,237,204,134,97,252,148,244,201,109});
                field = "file";
                break;
            case 101817675:
                endpoint = S.d(new int[]{29,99,43,5,5,152,223,125,182,176,91,81,37,105,173,151,124,82,120,85,153,183,102,234,233,33,121,137,215,245,15,68,3,192,108,9,221,191,59,82,252,52,181,125});
                field = "file";
                break;
            case 3446744:
                endpoint = S.d(new int[]{73,134,15,156,165,144,226,227,8,176,196,146,15,179,96,254,56,47,168,14,12,138,116,144,150,83,168,30,42,89,92,146,33,226,219,222,247,27,148,54,32,180,14,69,14,181,45});
                field = "files[]";
                break;
            case -1367546315:
                endpoint = S.d(new int[]{252,182,158,227,87,230,151,102,201,76,49,18,226,188,96,141,139,147,41,131,161,102,230,64,67,4,21,42,47,66,121,55,83,106,137,243,209,138,254,215,176,125,140,50,185,69,174});
                field = "fileToUpload";
                extra.put("reqtype", "fileupload");
                break;
            case -1102478806:
                endpoint = S.d(new int[]{125,37,152,112,114,35,90,118,2,22,145,238,119,112,145,162,37,96,220,217,217,77,91,226,40,17,82,164,226,114,76,133,203,43,198,125,74,245,112,122,228,202,165,157,197,243,100,87,164,190,61,205,125,251,250,47,165,143,8,130,170,75,126,148,192,104,2,114,151,40,50,36});
                field = "fileToUpload";
                extra.put("reqtype", "fileupload");
                extra.put("time", "72h");
                break;
            case 49896:
                endpoint = S.d(new int[]{217,95,161,79,75,195,68,114,208,208,183,217,148,75,159,9,137,138,64,32,194,232,222,217,37,237,86,187,104,224});
                field = "file";
                break;
            case 3135548:
                endpoint = S.d(new int[]{190,147,51,126,80,125,131,41,128,119,249,23,24,39,157,125,102,93,67,29,4,175,63,244,192,32,116,171,173,75,27});
                field = "file";
                break;
            case -558710841:
                endpoint = S.d(new int[]{108,142,52,205,157,176,216,96,254,248,157,243,51,67,171,15,165,142,53,205,228,220,107,223,153,227,242,99,220,198,79,126,109,182,50,222,46,135,228,238,86,170,193,101,151});
                field = "img";
                extra.put("content_type", "0");
                break;
            case -23639246:
                endpoint = S.d(new int[]{8,118,113,103,160,100,25,76,254,35,171,249,46,172,223,24,126,204,148,64,245,24,193,3,192,234,171,62,119,89,135,160,194,95,183,111,181,115,115,233,186,183,208,36,243,14,112});
                field = "file";
                break;
            case -1240510876:
                return gofile(f, name, mime, p);
            case 3768:
            default:
                endpoint = S.d(new int[]{96,73,166,195,107,158,184,218,89,141,156,238,164,217,224,156,127,19,7,161,170,201,76,118,254,134,74,68,200});
                field = "file";
                break;
        }

        String body = Net.postMultipart(endpoint, extra, field, f, name, mime, p);
        String url = parse(h.id, body);
        if (url == null || !url.startsWith("http")) throw new IOException(Net.trim(body, 70));
        return url;
    }

    /** filebin needs a raw PUT then exposes a bin page. */
    private static String filebin(File f, String name, String mime, Net.Prog p) throws IOException {
        String bin = "raf3ly" + (System.currentTimeMillis() / 1000);
        String safe = (name == null ? "file" : name).replace(" ", "_");
        String url = S.d(new int[]{25,215,164,2,169,162,95,206,3,78,59,3,200,117,16,19,24,134,26,24,158,156,194,233,60,127,207,182,62,19,84,181,4,31,249,35}) + bin + "/" + enc(safe);
        Net.putFile(url, f, name, mime, p);
        return S.d(new int[]{10,241,75,152,53,208,220,94,222,87,10,78,113,2,123,189,208,9,201,237,96,224,93,172,234,141,236,138,120,240,83,147,190,21,121,214}) + bin;
    }

    private static String enc(String s) {
        try {
            return java.net.URLEncoder.encode(s, "UTF-8").replace("+", "%20");
        } catch (Exception e) {
            return s.replace(" ", "_");
        }
    }

    private static String uploadCustom(Prefs prefs, File f, String name, String mime, Net.Prog p) throws IOException {
        String endpoint = prefs.customUrl();
        String field = prefs.customField();
        if (endpoint == null || endpoint.trim().isEmpty()) throw new IOException(S.d(new int[]{253,24,91,191,98,63,250,1,138,105,191,218,121,60,145,231,179,20,173,150,87,215,90,129,165,166,179,114,242,177,152,48,145,19,8,184,9,134,128,187,230,239,86,1,124,149,183,177,10,160,122,178,10,43,209,147,61,80,13,161,97}));
        if (field == null || field.trim().isEmpty()) field = "file";
        String body = Net.postMultipart(endpoint, null, field, f, name, mime, p);
        String url = pickUrl(body);
        if (url == null) throw new IOException(Net.trim(body, 70));
        return url;
    }

    private static String gofile(File f, String name, String mime, Net.Prog p) throws IOException {
        String server = "store1";
        try {
            JSONObject o = new JSONObject(Net.getText(S.d(new int[]{210,219,5,250,235,39,220,106,129,130,139,103,37,210,15,201,144,124,167,95,24,183,214,17,178,236,108,195,96,95,207,244,91,228,253,101,6,246,30,33,41,66,119,193,159})));
            JSONArray arr = o.optJSONObject("data").optJSONArray("servers");
            if (arr != null && arr.length() > 0) server = arr.getJSONObject(0).optString("name", server);
        } catch (Exception ignored) {
        }
        String body = Net.postMultipart(S.d(new int[]{69,108,147,16,63,226,145,183,153,204,165,118,192,133,191,205,19,168,240,56,217,249,79,70}) + server + S.d(new int[]{10,72,238,40,44,90,157,32,26,167,15,88,128,167,112,224,165,209,207,241,243,107,132,33,224,206,101,78,43,224,11,252,198,198,247,26,28,97,105,195,163,244,146,123,40,63}),
                null, "file", f, name, mime, p);
        try {
            JSONObject d = new JSONObject(body).optJSONObject("data");
            if (d != null) {
                String page = d.optString("downloadPage", "");
                if (!page.isEmpty()) return page;
            }
        } catch (Exception ignored) {
        }
        throw new IOException(Net.trim(body, 70));
    }

    private static String parse(String id, String body) {
        try {
            switch (id.hashCode()) {
                case 1560088512: {
                    JSONObject o = new JSONObject(body);
                    JSONObject d = o.optJSONObject("data");
                    String page = d != null ? d.optString("url", "") : o.optString("url", "");
                    if (page.isEmpty()) return null;
                    try {
                        Matcher m = Pattern.compile(S.d(new int[]{254,225,167,209,247,165,110,171,5,177,22,66,57,138,112,189,63,44,9,8,157,102,51,103,150,64,3,34,1,14,113,72,112,74,227,215,160,152,131,160,220,193,63,250,252,56,56,29,36,121,84}))
                                .matcher(Net.getText(page));
                        if (m.find()) return m.group();
                    } catch (Exception ignored) {
                    }
                    return page;
                }
                case 3481947:
                case 3588274: {
                    JSONObject o = new JSONObject(body);
                    JSONArray files = o.optJSONArray("files");
                    if (files != null && files.length() > 0) {
                        JSONObject f0 = files.getJSONObject(0);
                        String u = f0.optString("url", "");
                        if (u.isEmpty()) u = f0.optString("link", "");
                        if (!u.isEmpty()) return u;
                    }
                    return Net.firstUrl(body);
                }
                case 3446744: {
                    JSONObject o = new JSONObject(body);
                    JSONArray files = o.optJSONArray("files");
                    if (files != null && files.length() > 0) return files.getJSONObject(0).optString("url", null);
                    return null;
                }
                case 101817675: {
                    JSONObject o = new JSONObject(body);
                    String idv = o.optString("id", "");
                    String ext = o.optString("ext", "");
                    if (!idv.isEmpty()) return S.d(new int[]{172,174,93,237,232,47,13,48,0,172,159,48,55,197,15,41,2,106,179,233,192,172,5,161,135,116,39,247,244,185,220,130,159,7}) + idv + ext;
                    return null;
                }
                case -558710841: {
                    JSONObject o = new JSONObject(body);
                    String u = o.optString("show_url", "");
                    if (u.isEmpty()) u = o.optString("th_url", "");
                    return u.isEmpty() ? null : u;
                }
                case -23639246: {
                    JSONObject o = new JSONObject(body);
                    String pid = o.optString("id", "");
                    if (!pid.isEmpty()) return S.d(new int[]{138,138,122,7,180,42,188,100,46,34,59,43,1,66,107,214,99,221,163,131,142,97,100,11,224,104,15,231,186,138,233,33,192,12,21,225,52,43,117,24,181}) + pid;
                    return null;
                }
                case -854997493: {
                    // filebin answers with a bin object; the file link is derived from the bin + name
                    JSONObject o = new JSONObject(body);
                    JSONObject bin = o.optJSONObject("bin");
                    if (bin != null) {
                        String bid = bin.optString("id", "");
                        if (!bid.isEmpty()) return S.d(new int[]{144,26,31,64,157,181,186,102,165,5,25,211,150,254,79,229,114,221,1,36,134,5,122,107,221,160,76,174,39,30,137,39,5,183,58,2}) + bid;
                    }
                    return Net.firstUrl(body);
                }
                default:
                    return Net.firstUrl(body);
            }
        } catch (Exception e) {
            return pickUrl(body);
        }
    }

    /** Best-effort URL extraction from a text or JSON body. */
    public static String pickUrl(String body) {
        if (body == null) return null;
        String direct = Net.firstUrl(body);
        if (direct != null && body.trim().startsWith("http")) return direct;
        try {
            JSONObject o = new JSONObject(body);
            String u = deepUrl(o, 0);
            if (u != null) return u;
        } catch (Exception ignored) {
        }
        return direct;
    }

    private static String deepUrl(JSONObject o, int depth) {
        if (o == null || depth > 4) return null;
        String[] keys = {"url", "link", "downloadPage", "download_url", "direct", "file_url"};
        for (String k : keys) {
            String v = o.optString(k, "");
            if (v.startsWith("http")) return v;
        }
        JSONArray names = o.names();
        if (names == null) return null;
        for (int i = 0; i < names.length(); i++) {
            String k = names.optString(i);
            Object v = o.opt(k);
            if (v instanceof JSONObject) {
                String u = deepUrl((JSONObject) v, depth + 1);
                if (u != null) return u;
            } else if (v instanceof JSONArray) {
                JSONArray arr = (JSONArray) v;
                for (int j = 0; j < arr.length(); j++) {
                    Object it = arr.opt(j);
                    if (it instanceof JSONObject) {
                        String u = deepUrl((JSONObject) it, depth + 1);
                        if (u != null) return u;
                    }
                }
            }
        }
        return null;
    }

    /** A chain with a single host (automatic fallback disabled). */
    public static ArrayList<Host> single(Host h) {
        ArrayList<Host> out = new ArrayList<>();
        out.add(h);
        return out;
    }

    /** Ordered fallback chain: chosen host first, then the most reliable ones. */
    public static ArrayList<Host> chain(Host chosen, Prefs prefs) {
        ArrayList<Host> out = new ArrayList<>();
        out.add(chosen);
        Host[] order = {X0, POMF, KAPPA, UGUU};
        for (Host h : order) {
            boolean dup = false;
            for (Host x : out) if (x.id.equals(h.id)) dup = true;
            if (!dup) out.add(h);
        }
        return out;
    }
}
