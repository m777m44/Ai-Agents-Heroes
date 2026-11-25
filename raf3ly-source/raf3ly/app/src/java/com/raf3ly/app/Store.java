package com.raf3ly.app;

import android.content.Context;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;

/** Local archive (JSON on private storage). */
public class Store {
    private final File file;
    private final ArrayList<Entry> list = new ArrayList<>();
    private static final int MAX = 500;

    public Store(Context c) {
        file = new File(c.getFilesDir(), "history.json");
        load();
    }

    private synchronized void load() {
        list.clear();
        if (!file.exists()) return;
        try {
            FileInputStream in = new FileInputStream(file);
            BufferedReader r = new BufferedReader(new InputStreamReader(in, "UTF-8"));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = r.readLine()) != null) sb.append(line);
            r.close();
            JSONArray arr = new JSONArray(sb.toString());
            for (int i = 0; i < arr.length(); i++) {
                JSONObject o = arr.optJSONObject(i);
                if (o != null) list.add(Entry.from(o));
            }
        } catch (Exception ignored) {
        }
    }

    private synchronized void save() {
        try {
            JSONArray arr = new JSONArray();
            for (Entry e : list) arr.put(e.toJson());
            FileOutputStream out = new FileOutputStream(file);
            out.write(arr.toString().getBytes("UTF-8"));
            out.close();
        } catch (Exception ignored) {
        }
    }

    public synchronized void add(Entry e) {
        list.add(0, e);
        while (list.size() > MAX) list.remove(list.size() - 1);
        save();
    }

    public synchronized void remove(String id) {
        for (int i = 0; i < list.size(); i++) {
            if (list.get(i).id.equals(id)) {
                list.remove(i);
                break;
            }
        }
        save();
    }

    public synchronized void removeAll(ArrayList<String> ids) {
        for (String id : ids) {
            for (int i = list.size() - 1; i >= 0; i--) {
                if (list.get(i).id.equals(id)) list.remove(i);
            }
        }
        save();
    }

    public synchronized void bumpDownload(String id) {
        for (Entry e : list) {
            if (e.id.equals(id)) {
                e.downloads++;
                break;
            }
        }
        save();
    }

    public synchronized void toggleFav(String id) {
        for (Entry e : list) {
            if (e.id.equals(id)) {
                e.fav = !e.fav;
                break;
            }
        }
        save();
    }

    public synchronized void setFav(String id, boolean v) {
        for (Entry e : list) {
            if (e.id.equals(id)) {
                e.fav = v;
                break;
            }
        }
        save();
    }

    public synchronized Entry get(String id) {
        for (Entry e : list) if (e.id.equals(id)) return e;
        return null;
    }

    public synchronized ArrayList<Entry> all() {
        return new ArrayList<>(list);
    }

    /** sort: new | old | big | small | dl | fav */
    public synchronized ArrayList<Entry> sorted(String sort) {
        ArrayList<Entry> out = new ArrayList<>(list);
        if ("old".equals(sort)) {
            Collections.sort(out, new Comparator<Entry>() {
                public int compare(Entry a, Entry b) {
                    return Long.compare(a.ts, b.ts);
                }
            });
        } else if ("big".equals(sort)) {
            Collections.sort(out, new Comparator<Entry>() {
                public int compare(Entry a, Entry b) {
                    return Long.compare(b.size, a.size);
                }
            });
        } else if ("dl".equals(sort)) {
            Collections.sort(out, new Comparator<Entry>() {
                public int compare(Entry a, Entry b) {
                    return Integer.compare(b.downloads, a.downloads);
                }
            });
        } else if ("fav".equals(sort)) {
            Collections.sort(out, new Comparator<Entry>() {
                public int compare(Entry a, Entry b) {
                    if (a.fav != b.fav) return a.fav ? -1 : 1;
                    return Long.compare(b.ts, a.ts);
                }
            });
        } else {
            Collections.sort(out, new Comparator<Entry>() {
                public int compare(Entry a, Entry b) {
                    return Long.compare(b.ts, a.ts);
                }
            });
        }
        return out;
    }

    public synchronized int count() {
        return list.size();
    }

    public synchronized int favCount() {
        int n = 0;
        for (Entry e : list) if (e.fav) n++;
        return n;
    }

    public synchronized long bytes() {
        long t = 0;
        for (Entry e : list) t += e.size;
        return t;
    }

    public synchronized int downloads() {
        int t = 0;
        for (Entry e : list) t += e.downloads;
        return t;
    }

    public synchronized long biggest() {
        long t = 0;
        for (Entry e : list) t = Math.max(t, e.size);
        return t;
    }

    /** host domain -> count */
    public synchronized Map<String, Integer> hostsBreakdown() {
        HashMap<String, Integer> m = new HashMap<>();
        for (Entry e : list) {
            Integer v = m.get(e.host);
            m.put(e.host, v == null ? 1 : v + 1);
        }
        return m;
    }

    public synchronized int perDay(int daysAgo) {
        Calendar cal = Calendar.getInstance();
        cal.set(Calendar.HOUR_OF_DAY, 0);
        cal.set(Calendar.MINUTE, 0);
        cal.set(Calendar.SECOND, 0);
        cal.set(Calendar.MILLISECOND, 0);
        long end = cal.getTimeInMillis() - (daysAgo * 86400000L);
        long start = end - 86400000L;
        int n = 0;
        for (Entry e : list) if (e.ts >= start && e.ts < end) n++;
        return n;
    }

    public synchronized int[] last7() {
        int[] out = new int[7];
        for (int i = 0; i < 7; i++) out[i] = perDay(6 - i);
        return out;
    }

    public synchronized long bytesToday() {
        Calendar cal = Calendar.getInstance();
        cal.set(Calendar.HOUR_OF_DAY, 0);
        cal.set(Calendar.MINUTE, 0);
        cal.set(Calendar.SECOND, 0);
        cal.set(Calendar.MILLISECOND, 0);
        long start = cal.getTimeInMillis();
        long t = 0;
        for (Entry e : list) if (e.ts >= start) t += e.size;
        return t;
    }

    public synchronized void clear() {
        list.clear();
        save();
    }

    public synchronized String exportJson() {
        JSONArray arr = new JSONArray();
        for (Entry e : list) arr.put(e.toJson());
        return arr.toString();
    }

    /** returns imported count */
    public synchronized int importJson(String json) {
        int n = 0;
        try {
            JSONArray arr = new JSONArray(json);
            for (int i = 0; i < arr.length(); i++) {
                JSONObject o = arr.optJSONObject(i);
                if (o == null) continue;
                Entry e = Entry.from(o);
                if (e.url.isEmpty()) continue;
                boolean dup = false;
                for (Entry x : list) if (x.url.equals(e.url)) dup = true;
                if (!dup) {
                    list.add(e);
                    n++;
                }
            }
            save();
        } catch (Exception ignored) {
        }
        return n;
    }
}
