package com.raf3ly.app;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Handler;
import android.os.Looper;
import android.util.LruCache;
import android.widget.ImageView;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Tiny async thumbnail loader for remote images (no external libs). */
public class ImageLoader {
    private static final LruCache<String, Bitmap> cache = new LruCache<String, Bitmap>(6 * 1024 * 1024) {
        @Override
        protected int sizeOf(String key, Bitmap value) {
            return value.getByteCount();
        }
    };
    private static final Handler main = new Handler(Looper.getMainLooper());
    private static final ExecutorService pool = Executors.newFixedThreadPool(3);

    public static void load(final ImageView iv, final String url, final int px) {
        if (url == null || url.isEmpty()) return;
        iv.setTag(url);
        Bitmap cached = cache.get(url);
        if (cached != null) {
            iv.setImageBitmap(cached);
            return;
        }
        pool.execute(new Runnable() {
            @Override
            public void run() {
                final Bitmap bm = fetch(url, px);
                if (bm == null) return;
                cache.put(url, bm);
                main.post(new Runnable() {
                    @Override
                    public void run() {
                        if (url.equals(iv.getTag())) iv.setImageBitmap(bm);
                    }
                });
            }
        });
    }

    private static Bitmap fetch(String url, int px) {
        try {
            HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
            c.setConnectTimeout(15000);
            c.setReadTimeout(20000);
            c.setInstanceFollowRedirects(true);
            c.setRequestProperty("User-Agent", "Mozilla/5.0 (Linux; Android) Raf3ly/1.0");
            InputStream in = c.getInputStream();
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            byte[] buf = new byte[64 * 1024];
            int r;
            while ((r = in.read(buf)) > 0) {
                bos.write(buf, 0, r);
                if (bos.size() > 6 * 1024 * 1024) break;
            }
            in.close();
            byte[] data = bos.toByteArray();
            BitmapFactory.Options o = new BitmapFactory.Options();
            o.inJustDecodeBounds = true;
            BitmapFactory.decodeByteArray(data, 0, data.length, o);
            int sample = 1;
            while (o.outWidth / (sample * 2) >= px) sample *= 2;
            BitmapFactory.Options o2 = new BitmapFactory.Options();
            o2.inSampleSize = sample;
            return BitmapFactory.decodeByteArray(data, 0, data.length, o2);
        } catch (Exception e) {
            return null;
        }
    }
}
