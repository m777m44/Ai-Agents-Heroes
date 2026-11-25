package com.raf3ly.app;

import android.content.ContentValues;
import android.content.Context;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.MediaStore;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

/** Downloads a saved file back to the device with live progress. */
public class Downloader {

    public interface Cb {
        void onProgress(long done, long total, long bps, long eta);

        void onDone(String message, Uri uri);

        void onError(String message);
    }

    private static final Handler main = new Handler(Looper.getMainLooper());

    public static void start(final Context ctx, final Entry e, final Cb cb) {
        final long[] mark = new long[]{System.currentTimeMillis(), 0};
        final long[] bps = new long[]{0};
        final long[] total = new long[]{0};
        final long[] lastPost = new long[]{0};

        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    String name = safeName(e.name);
                    if (Build.VERSION.SDK_INT >= 29) {
                        ContentValues cv = new ContentValues();
                        cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
                        cv.put(MediaStore.MediaColumns.MIME_TYPE,
                                (e.mime == null || e.mime.isEmpty()) ? "application/octet-stream" : e.mime);
                        cv.put(MediaStore.MediaColumns.RELATIVE_PATH,
                                Environment.DIRECTORY_DOWNLOADS + "/Raf3ly");
                        cv.put(MediaStore.MediaColumns.IS_PENDING, 1);

                        final Uri uri = ctx.getContentResolver()
                                .insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
                        if (uri == null) throw new Exception(S.d(new int[]{217,208,253,120,103,92,45,236,54,19,68,67,172,219,99,74,107,171,198,174,223,118,41,26,37,80,131,234,240,110,219,61,155,124,146,60,149,228,43,168,26,140,239,167,80,224,196,58,94,6,53,184,154,206,133,120,96,18,223,165,228,212,149,235,135,179,70,118,32,209,50}));

                        OutputStream os = ctx.getContentResolver().openOutputStream(uri);
                        final long n = Net.download(e.url, os, prog(cb, mark, bps, total, lastPost));
                        if (os != null) os.close();

                        ContentValues done = new ContentValues();
                        done.put(MediaStore.MediaColumns.IS_PENDING, 0);
                        ctx.getContentResolver().update(uri, done, null, null);

                        main.post(new Runnable() {
                            @Override
                            public void run() {
                                cb.onDone(S.d(new int[]{197,0,134,36,43,163,133,161,74,153,198,250,210,137,181,98,121,207,237,184,84,122,64,192,177,94,195,126,233,240,134,102,30,123,13,60,8,147,55,226,142,251,240,98,216,219,193,163,185,24,234,146,126,41,167,233,12,80,92,217,138}) + U.size(n), uri);
                            }
                        });
                    } else {
                        File dir = new File(Environment.getExternalStoragePublicDirectory(
                                Environment.DIRECTORY_DOWNLOADS), "Raf3ly");
                        if (!dir.exists()) {
                            //noinspection ResultOfMethodCallIgnored
                            dir.mkdirs();
                        }
                        final File out = new File(dir, name);
                        FileOutputStream fos = new FileOutputStream(out);
                        final long n = Net.download(e.url, fos, prog(cb, mark, bps, total, lastPost));
                        fos.close();
                        main.post(new Runnable() {
                            @Override
                            public void run() {
                                cb.onDone(S.d(new int[]{179,89,2,231,65,215,39,85,22,26,109,157,49,36,130,187,143,234,184,71,111,111,244,120,137,190,33,95,32,15,28,198,78,33,114,134,129}) + out.getAbsolutePath() + " · " + U.size(n), null);
                            }
                        });
                    }
                } catch (final Exception ex) {
                    main.post(new Runnable() {
                        @Override
                        public void run() {
                            cb.onError(ex.getMessage() == null ? S.d(new int[]{88,64,65,193,99,249,140,189,223,94,237,210,63,234,208,140,89,11,100,166,134,136,213,234,220,216,116,88,8,163,186,173,238,20,36,93,124}) : ex.getMessage());
                        }
                    });
                }
            }
        }, "raf3ly-dl").start();
    }

    private static Net.Prog prog(final Cb cb, final long[] mark, final long[] bps,
                                 final long[] total, final long[] lastPost) {
        return new Net.Prog() {
            @Override
            public boolean onBytes(long done, long t) {
                if (t > 0) total[0] = t;
                long now = System.currentTimeMillis();
                long dt = now - mark[0];
                if (dt >= 250) {
                    long inst = (done - mark[1]) * 1000L / Math.max(1, dt);
                    bps[0] = bps[0] == 0 ? inst : (bps[0] * 2 + inst) / 3;
                    mark[0] = now;
                    mark[1] = done;
                }
                if (now - lastPost[0] < 120) return true;
                lastPost[0] = now;
                final long eta = bps[0] > 0 && total[0] > 0 ? (total[0] - done) * 1000L / bps[0] : -1;
                final long fd = done, ft = total[0], fb = bps[0];
                main.post(new Runnable() {
                    @Override
                    public void run() {
                        cb.onProgress(fd, ft, fb, eta);
                    }
                });
                return true;
            }
        };
    }

    private static String safeName(String n) {
        if (n == null || n.trim().isEmpty()) return "file_" + System.currentTimeMillis();
        return n.replace('/', '_').replace('\\', '_').replace(":", "_");
    }
}
