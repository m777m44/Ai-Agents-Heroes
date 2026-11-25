package com.raf3ly.app;

import org.json.JSONObject;

/** One uploaded file record. */
public class Entry {
    public String id = "";
    public String name = "";
    public String url = "";
    public String host = S.d(new int[]{206,129,20,191,59,16,26,29,229,245,3,199,11,238,150,249,127,227,131,121,57});
    public String mime = "";
    public long size = 0;
    public long ts = System.currentTimeMillis();
    public int downloads = 0;
    public boolean fav = false;
    public String tags = "";

    public boolean isImage() {
        return mime != null && mime.startsWith("image/");
    }

    public boolean isVideo() {
        return mime != null && mime.startsWith("video/");
    }

    public String kind() {
        if (isImage()) return S.d(new int[]{67,239,136,215,21,194,146,13,0,198,216,51,110,179,219,211,32,93,107,105,22,69});
        if (isVideo()) return S.d(new int[]{89,231,20,39,184,135,138,195,51,201,255,85,17,61,4,24,98,118,147,4,250,30,120,2,54,40});
        if (mime != null && (mime.contains("pdf") || mime.contains("word") || mime.contains("excel")
                || mime.contains("text") || mime.contains("sheet") || mime.contains("presentation")))
            return S.d(new int[]{69,119,140,71,160,224,244,236,129,155,190,232,180,134,89,4,94,74,81,24,163,34,121,201,101,253,105,90,78,250});
        return S.d(new int[]{195,75,253,179,59,107,103,235,44,224,158,37,227,105,193,205,30,28,196,187,59,132,194,118,86,205});
    }

    public JSONObject toJson() {
        JSONObject o = new JSONObject();
        try {
            o.put("id", id);
            o.put("name", name);
            o.put("url", url);
            o.put("host", host);
            o.put("mime", mime);
            o.put("size", size);
            o.put("ts", ts);
            o.put("downloads", downloads);
            o.put("fav", fav);
            o.put("tags", tags);
        } catch (Exception ignored) {
        }
        return o;
    }

    public static Entry from(JSONObject o) {
        Entry e = new Entry();
        e.id = o.optString("id", "");
        e.name = o.optString("name", "");
        e.url = o.optString("url", "");
        e.host = o.optString("host", S.d(new int[]{114,80,158,145,28,243,178,52,156,165,42,92,146,75,56,248,145,126,111,157,245}));
        e.mime = o.optString("mime", "");
        e.size = o.optLong("size", 0);
        e.ts = o.optLong("ts", System.currentTimeMillis());
        e.downloads = o.optInt("downloads", 0);
        e.fav = o.optBoolean("fav", false);
        e.tags = o.optString("tags", "");
        return e;
    }
}
