package com.raf3ly.app;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;

import java.io.File;
import java.io.FileOutputStream;

/** Optional image slimming before upload (level 0 = off). */
public class ImageCompressor {

    public static final String[] LEVELS = {S.d(new int[]{15,218,87,63,163,68,108,24,181,214,0,184,1,109,222,3,0,79,86,108,6,201,32,52}), S.d(new int[]{108,57,37,254,228,23,165,58,39,157,249,241,71,78,53,86,74,73,139,48,38,209,59,151,37,188,196,78,209,27,9}), S.d(new int[]{223,99,122,180,135,36,36,148,62,100,176,33,216,238,38,109,59,12,241,216,203,175,217,12,208,172,185,102,60,147,117,171,39})};

    /** Returns a compressed temp file, or null when the original should be used. */
    public static File compress(File src, String mime, String name, int level) {
        if (level <= 0) return null;
        if (mime == null || !mime.startsWith("image/")) return null;
        if (mime.contains("gif") || mime.contains("svg")) return null;

        int maxSide = level == 1 ? 2560 : 1600;
        int quality = level == 1 ? 88 : 70;

        try {
            BitmapFactory.Options bounds = new BitmapFactory.Options();
            bounds.inJustDecodeBounds = true;
            BitmapFactory.decodeFile(src.getAbsolutePath(), bounds);
            if (bounds.outWidth <= 0) return null;

            int sample = 1;
            while (Math.max(bounds.outWidth, bounds.outHeight) / (sample * 2) >= maxSide) sample *= 2;

            BitmapFactory.Options opts = new BitmapFactory.Options();
            opts.inSampleSize = sample;
            Bitmap bmp = BitmapFactory.decodeFile(src.getAbsolutePath(), opts);
            if (bmp == null) return null;

            int w = bmp.getWidth(), h = bmp.getHeight();
            float scale = Math.min(1f, maxSide / (float) Math.max(w, h));
            if (scale < 1f) {
                Bitmap scaled = Bitmap.createScaledBitmap(bmp, Math.round(w * scale), Math.round(h * scale), true);
                if (scaled != bmp) bmp.recycle();
                bmp = scaled;
            }

            boolean png = mime.contains("png") || mime.contains("webp");
            File out = new File(src.getParentFile(), "cmp_" + System.nanoTime() + (png ? ".png" : ".jpg"));
            FileOutputStream fos = new FileOutputStream(out);
            bmp.compress(png ? Bitmap.CompressFormat.PNG : Bitmap.CompressFormat.JPEG, quality, fos);
            fos.flush();
            fos.close();
            bmp.recycle();

            if (out.length() <= 0 || out.length() >= src.length()) {
                //noinspection ResultOfMethodCallIgnored
                out.delete();
                return null;
            }
            return out;
        } catch (Throwable t) {
            return null;
        }
    }
}
