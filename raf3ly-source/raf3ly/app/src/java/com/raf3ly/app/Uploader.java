package com.raf3ly.app;

import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import android.provider.OpenableColumns;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

/** Upload queue: prepare (optional compression) → upload with host fallback chain → archive. */
public class Uploader {

    public static final int QUEUED = 0, PREPARING = 1, UPLOADING = 2, DONE = 3, FAILED = 4, CANCELLED = 5;

    public static class Task {
        public Uri uri;
        public String name = S.d(new int[]{81,255,42,244,22,69,51,82,82,98,162,161,255,82,179,66,236,42,195,63,49,30});
        public String mime = "application/octet-stream";
        public long size = 0, done = 0, total = 0, bps = 0, eta = -1;
        public int state = QUEUED;
        public String error = "";
        public Entry entry;
        public volatile boolean cancel = false;
        public String hostUsed = "";
        public String stage = "";
        public long lastTick = 0, lastBytes = 0;
    }

    public interface Listener {
        void onChanged();
    }

    private final Context ctx;
    private final Store store;
    private final Prefs prefs;
    private final Listener listener;
    private final Handler main = new Handler(Looper.getMainLooper());
    private final ExecutorService pool = Executors.newFixedThreadPool(3);
    private final AtomicInteger activeWorkers = new AtomicInteger(0);

    public final ArrayList<Task> tasks = new ArrayList<>();
    public volatile boolean running = false;

    private long lastPostAt = 0;

    public Uploader(Context c, Store s, Prefs p, Listener l) {
        ctx = c;
        store = s;
        prefs = p;
        listener = l;
    }

    private void post(boolean force) {
        long now = System.currentTimeMillis();
        if (!force && now - lastPostAt < 110) return;
        lastPostAt = now;
        main.post(new Runnable() {
            @Override
            public void run() {
                if (listener != null) listener.onChanged();
            }
        });
    }

    public void enqueue(List<Uri> uris) {
        for (Uri u : uris) {
            Task t = new Task();
            t.uri = u;
            t.name = nameOf(u);
            String m = ctx.getContentResolver().getType(u);
            if (m != null && !m.isEmpty()) t.mime = m;
            t.size = sizeOf(u);
            t.total = t.size;
            tasks.add(t);
        }
        post(true);
        start();
    }

    public void cancel(Task t) {
        t.cancel = true;
        if (t.state == QUEUED) {
            t.state = CANCELLED;
            post(true);
        }
    }

    public void clearFinished() {
        for (int i = tasks.size() - 1; i >= 0; i--) {
            int st = tasks.get(i).state;
            if (st == DONE || st == FAILED || st == CANCELLED) tasks.remove(i);
        }
        post(true);
    }

    public void retry(Task t) {
        if (t.state == FAILED || t.state == CANCELLED) {
            t.state = QUEUED;
            t.done = 0;
            t.error = "";
            t.cancel = false;
            post(true);
            start();
        }
    }

    public int pendingCount() {
        int n = 0;
        for (Task t : tasks) if (t.state == QUEUED || t.state == PREPARING || t.state == UPLOADING) n++;
        return n;
    }

    public int doneCount() {
        int n = 0;
        for (Task t : tasks) if (t.state == DONE) n++;
        return n;
    }

    public long activeTotal() {
        long n = 0;
        for (Task t : tasks) if (t.state == UPLOADING) n += t.total;
        return n;
    }

    public long activeDone() {
        long n = 0;
        for (Task t : tasks) if (t.state == UPLOADING) n += t.done;
        return n;
    }

    public long activeSpeed() {
        long n = 0;
        for (Task t : tasks) if (t.state == UPLOADING) n += t.bps;
        return n;
    }

    public long activeEta() {
        long worst = -1;
        for (Task t : tasks) if (t.state == UPLOADING && t.eta > worst) worst = t.eta;
        return worst;
    }

    public long queuedBytes() {
        long n = 0;
        for (Task t : tasks) n += Math.max(t.size, t.total);
        return n;
    }

    public void start() {
        if (running) return;
        running = true;
        int n = Math.max(1, Math.min(3, prefs.parallel()));
        activeWorkers.set(n);
        for (int i = 0; i < n; i++) pool.execute(worker);
    }

    private final Runnable worker = new Runnable() {
        @Override
        public void run() {
            try {
                while (true) {
                    Task t = claim();
                    if (t == null) break;
                    process(t);
                }
            } finally {
                if (activeWorkers.decrementAndGet() <= 0) {
                    running = false;
                    post(true);
                }
            }
        }
    };

    private synchronized Task claim() {
        for (Task t : tasks) {
            if (t.state == QUEUED) {
                t.state = PREPARING; // reserve
                return t;
            }
        }
        return null;
    }

    private void process(Task t) {
        File cache = null;
        File original = null;
        File compressed = null;
        String uploadName = t.name;
        String uploadMime = t.mime;
        try {
            t.error = "";
            t.cancel = false;
            t.stage = S.d(new int[]{148,228,212,184,180,220,219,8,12,53,153,15,132,153,160,63,203,160,193,130,163,153,55,170,182,124});
            post(true);

            // 1) copy the picked content into a private cache file
            original = new File(ctx.getCacheDir(), "up_" + UUID.randomUUID().toString());
            copyToCache(t, original);
            if (original.length() <= 0) throw new Exception(S.d(new int[]{239,78,244,231,28,216,237,158,222,23,230,100,176,107,13,140,156,107,173,139,102,237,140,100,54,157,225,112,80,92,235,18,49,137,144,81,19,70,7,17,230,97,172,132,142,43,126,150,233,130,173,32,213,247,27,123,129,248,26,59,143,149,227,138,101,205,172,218,147}));
            if (t.cancel) throw new Net.Cancelled();

            // 2) optional image slimming
            cache = original;
            if (prefs.compression() > 0 && t.mime != null && t.mime.startsWith("image/")) {
                t.stage = S.d(new int[]{153,128,15,70,238,61,122,19,176,104,212,252,146,63,66,0,104,27,136,242,106,241,98,156,61,123,107,150,64,120,186,116,164,23,85});
                post(true);
                compressed = ImageCompressor.compress(original, t.mime, t.name, prefs.compression());
                if (compressed != null) {
                    cache = compressed;
                    uploadMime = t.mime.contains("png") || t.mime.contains("webp") ? "image/png" : "image/jpeg";
                    if (!uploadName.toLowerCase().endsWith(uploadMime.contains("png") ? ".png" : ".jpg")) {
                        int dot = uploadName.lastIndexOf('.');
                        uploadName = (dot > 0 ? uploadName.substring(0, dot) : uploadName)
                                + (uploadMime.contains("png") ? ".png" : ".jpg");
                    }
                }
            }

            t.size = cache.length();
            t.total = cache.length();
            t.state = UPLOADING;
            t.done = 0;
            t.bps = 0;

            // 3) upload with fallback chain
            final Task ft = t;
            Net.Prog prog = new Net.Prog() {
                @Override
                public boolean onBytes(long done, long total) {
                    if (ft.cancel) return false;
                    ft.done = done;
                    ft.total = total > 0 ? total : ft.total;
                    long now = System.currentTimeMillis();
                    if (ft.lastTick == 0) {
                        ft.lastTick = now;
                        ft.lastBytes = done;
                    } else if (now - ft.lastTick >= 250) {
                        long inst = (done - ft.lastBytes) * 1000L / Math.max(1, now - ft.lastTick);
                        ft.bps = ft.bps == 0 ? inst : (ft.bps * 2 + inst) / 3;
                        ft.lastTick = now;
                        ft.lastBytes = done;
                        ft.eta = ft.bps > 0 ? (ft.total - done) * 1000L / ft.bps : -1;
                    }
                    post(false);
                    return true;
                }
            };

            Hosts.Host chosen = Hosts.byId(prefs.host());
            ArrayList<Hosts.Host> chain = prefs.fallback()
                    ? Hosts.chain(chosen, prefs)
                    : Hosts.single(chosen);

            String url = null;
            Exception lastError = null;
            for (int i = 0; i < chain.size(); i++) {
                Hosts.Host h = chain.get(i);
                try {
                    t.stage = S.d(new int[]{47,69,114,215,51,38,18,221,128,227,224,109,234,52,32,85,136,141,210,185,143,162,225,244,170,37,60,151,9,93}) + h.name;
                    t.done = 0;
                    t.bps = 0;
                    t.lastTick = 0;
                    post(true);
                    url = Hosts.upload(h, prefs, cache, uploadName, uploadMime, prog);
                    t.hostUsed = h.domain;
                    break;
                } catch (Net.Cancelled ce) {
                    throw ce;
                } catch (Exception e) {
                    lastError = e;
                    if (t.cancel) throw new Net.Cancelled();
                    post(true);
                }
            }
            if (url == null) throw lastError != null ? lastError : new Exception(S.d(new int[]{77,52,202,99,129,239,155,159,253,226,123,116,31,245,223,249,46,150,203,36,173,254,51,235,156,117,174,169,8,84,70,88,144,11,165,209,55,145,167,2,68,117,5,8,128,16,91,211,212,172,223,148,134,12,81,246,160,104,75,148}));

            Entry e = new Entry();
            e.id = UUID.randomUUID().toString();
            e.name = uploadName;
            e.url = url;
            e.host = t.hostUsed;
            e.mime = uploadMime;
            e.size = cache.length();
            e.ts = System.currentTimeMillis();
            if (prefs.keepHistory()) store.add(e);

            t.entry = e;
            t.state = DONE;
            t.done = t.total;
            t.eta = 0;
            t.stage = "";
            post(true);
        } catch (Net.Cancelled ce) {
            t.state = CANCELLED;
            t.error = S.d(new int[]{71,194,104,202,220,119,187,246,175,95,14,155,232,35,68,242,213,14,239,217,117,142,53,141,28,128});
            post(true);
        } catch (Exception ex) {
            t.state = FAILED;
            t.error = ex.getMessage() == null ? S.d(new int[]{238,198,150,152,50,125,238,233,97,221,11,1,165,22,160,219,69,161,222,124,233,183,161,224,74,163,189,140,170,69,88,10,7,57,16,69,249,141,51,155}) : ex.getMessage();
            post(true);
        } finally {
            if (original != null && original.exists()) {
                //noinspection ResultOfMethodCallIgnored
                original.delete();
            }
            if (compressed != null && compressed.exists()) {
                //noinspection ResultOfMethodCallIgnored
                compressed.delete();
            }
        }
    }

    private void copyToCache(Task t, File dest) throws Exception {
        InputStream in = ctx.getContentResolver().openInputStream(t.uri);
        if (in == null) throw new Exception(S.d(new int[]{168,47,40,234,141,160,95,157,58,121,61,14,102,73,165,102,165,75,47,60,230,196,41,4,67,53,190,114,233,175,74,186,55,174,227,20,3,66,101,116,97,242,223,27,143,185,73,103,46}));
        FileOutputStream out = new FileOutputStream(dest);
        byte[] buf = new byte[256 * 1024];
        long done = 0;
        int r;
        long lastTick = 0;
        while ((r = in.read(buf)) > 0) {
            out.write(buf, 0, r);
            done += r;
            t.done = done;
            t.total = Math.max(t.total, done);
            long now = System.currentTimeMillis();
            if (now - lastTick > 140) {
                lastTick = now;
                post(false);
            }
        }
        in.close();
        out.flush();
        out.close();
    }

    private String nameOf(Uri uri) {
        String name = null;
        try {
            Cursor c = ctx.getContentResolver().query(uri, null, null, null, null);
            if (c != null) {
                int ni = c.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                if (c.moveToFirst() && ni >= 0) name = c.getString(ni);
                c.close();
            }
        } catch (Exception ignored) {
        }
        if (name == null) {
            String p = uri.getLastPathSegment();
            name = p == null ? "file" : p.substring(p.lastIndexOf('/') + 1);
        }
        return name;
    }

    private long sizeOf(Uri uri) {
        long size = -1;
        try {
            Cursor c = ctx.getContentResolver().query(uri, null, null, null, null);
            if (c != null) {
                int si = c.getColumnIndex(OpenableColumns.SIZE);
                if (c.moveToFirst() && si >= 0 && !c.isNull(si)) size = c.getLong(si);
                c.close();
            }
        } catch (Exception ignored) {
        }
        return size;
    }
}
