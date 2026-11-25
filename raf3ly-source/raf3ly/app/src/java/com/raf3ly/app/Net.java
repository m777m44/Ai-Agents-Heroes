package com.raf3ly.app;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.LinkedHashMap;
import java.util.Map;

/** Low level HTTP: multipart upload (with cancel), text GET, streaming download. */
public class Net {

    /** Progress callback. Return false to cancel the transfer. */
    public interface Prog {
        boolean onBytes(long done, long total);
    }

    private static final String CRLF = "\r\n";
    public static final String UA = "Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 "
            + "(KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36";

    public static class Cancelled extends IOException {
        public Cancelled() {
            super(S.d(new int[]{66,85,3,22,56,225,69,206,77,177,115,230,30,156,213,147,19,139,185,94,92,188,113,175,237,148,133,254,171,179,32,21,134,92,142,188,202,116,234,212,218,212}));
        }
    }

    /** Generic multipart POST. extra fields are sent before the file part. */
    public static String postMultipart(String endpoint, LinkedHashMap<String, String> extra, String fileField,
                                       File file, String name, String mime, Prog prog) throws IOException {
        String boundary = "----Raf3lyBoundary" + System.currentTimeMillis();
        String safeName = (name == null ? "file" : name).replace("\"", "").replace("\n", " ").replace("\r", " ");
        String type = (mime == null || mime.isEmpty()) ? "application/octet-stream" : mime;

        ByteArrayOutputStream headBuf = new ByteArrayOutputStream();
        if (extra != null) {
            for (Map.Entry<String, String> e : extra.entrySet()) {
                String part = "--" + boundary + CRLF
                        + "Content-Disposition: form-data; name=\"" + e.getKey() + "\"" + CRLF + CRLF
                        + e.getValue() + CRLF;
                headBuf.write(part.getBytes("UTF-8"));
            }
        }
        String fileHead = "--" + boundary + CRLF
                + "Content-Disposition: form-data; name=\"" + fileField + "\"; filename=\"" + safeName + "\"" + CRLF
                + "Content-Type: " + type + CRLF + CRLF;
        headBuf.write(fileHead.getBytes("UTF-8"));

        byte[] head = headBuf.toByteArray();
        byte[] tail = (CRLF + "--" + boundary + "--" + CRLF).getBytes("UTF-8");
        long total = head.length + file.length() + tail.length;

        HttpURLConnection c = (HttpURLConnection) new URL(endpoint).openConnection();
        c.setRequestMethod("POST");
        c.setDoOutput(true);
        c.setConnectTimeout(25000);
        c.setReadTimeout(300000);
        c.setInstanceFollowRedirects(true);
        c.setRequestProperty("Content-Type", "multipart/form-data; boundary=" + boundary);
        c.setRequestProperty("User-Agent", UA);
        c.setRequestProperty("Accept", "*/*");
        c.setRequestProperty("Connection", "close");
        c.setFixedLengthStreamingMode(total);

        OutputStream os = c.getOutputStream();
        long sent = 0;
        os.write(head);
        sent += head.length;

        FileInputStream in = new FileInputStream(file);
        byte[] buf = new byte[128 * 1024];
        int r;
        long lastTick = 0;
        try {
            while ((r = in.read(buf)) > 0) {
                os.write(buf, 0, r);
                sent += r;
                long now = System.currentTimeMillis();
                if (prog != null && now - lastTick > 130) {
                    lastTick = now;
                    if (!prog.onBytes(sent, total)) {
                        try {
                            c.disconnect();
                        } catch (Exception ignored) {
                        }
                        throw new Cancelled();
                    }
                }
            }
        } finally {
            try {
                in.close();
            } catch (Exception ignored) {
            }
        }
        os.write(tail);
        sent += tail.length;
        os.flush();
        os.close();
        if (prog != null) prog.onBytes(total, total);

        int code = c.getResponseCode();
        InputStream is = (code >= 400) ? c.getErrorStream() : c.getInputStream();
        String body = readAll(is).trim();
        c.disconnect();
        if (code >= 400) throw new IOException("HTTP " + code + " — " + trim(body, 80));
        if (body.isEmpty()) throw new IOException(S.d(new int[]{64,25,146,4,98,51,171,203,85,126,12,70,195,142,195,39,5,8,8,148,150,142,204,38,179,99,137,33,50,47,92,87,249,130,108,172,132,36,45,68,146,161,161,47,110,87,85,199,132}));
        return body;
    }

    /** Raw PUT upload (used by bins like filebin). */
    public static String putFile(String url, File f, String name, String mime, Prog prog) throws IOException {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setRequestMethod("PUT");
        c.setDoOutput(true);
        c.setConnectTimeout(25000);
        c.setReadTimeout(300000);
        c.setRequestProperty("Content-Type", (mime == null || mime.isEmpty()) ? "application/octet-stream" : mime);
        c.setRequestProperty("User-Agent", UA);
        c.setRequestProperty("Connection", "close");
        c.setFixedLengthStreamingMode(f.length());

        OutputStream os = c.getOutputStream();
        FileInputStream in = new FileInputStream(f);
        byte[] buf = new byte[128 * 1024];
        int r;
        long sent = 0, lastTick = 0;
        try {
            while ((r = in.read(buf)) > 0) {
                os.write(buf, 0, r);
                sent += r;
                long now = System.currentTimeMillis();
                if (prog != null && now - lastTick > 130) {
                    lastTick = now;
                    if (!prog.onBytes(sent, f.length())) {
                        c.disconnect();
                        throw new Cancelled();
                    }
                }
            }
        } finally {
            try {
                in.close();
            } catch (Exception ignored) {
            }
        }
        os.flush();
        os.close();
        if (prog != null) prog.onBytes(f.length(), f.length());

        int code = c.getResponseCode();
        InputStream is = code >= 400 ? c.getErrorStream() : c.getInputStream();
        String body = readAll(is);
        c.disconnect();
        if (code >= 400) throw new IOException("HTTP " + code + " — " + trim(body, 70));
        return body;
    }

    public static String getText(String url) throws IOException {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setConnectTimeout(20000);
        c.setReadTimeout(30000);
        c.setInstanceFollowRedirects(true);
        c.setRequestProperty("User-Agent", UA);
        int code = c.getResponseCode();
        InputStream is = code >= 400 ? c.getErrorStream() : c.getInputStream();
        String body = readAll(is);
        c.disconnect();
        if (code >= 400) throw new IOException("HTTP " + code);
        return body;
    }

    /** Streams a remote file into out. Returns bytes written. */
    public static long download(String url, OutputStream out, Prog prog) throws IOException {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setConnectTimeout(25000);
        c.setReadTimeout(60000);
        c.setInstanceFollowRedirects(true);
        c.setRequestProperty("User-Agent", UA);
        c.setRequestProperty("Accept", "*/*");
        int code = c.getResponseCode();
        if (code >= 400) throw new IOException(S.d(new int[]{126,140,121,46,156,220,67,126,124,240,95,167,203,40,33,223,108,252,115,77,66,152,117,20,197,173,98,48,152,22,96,116,51,68,11,244,55,17,61,116,98,79,138,224}) + code + ")");
        long total = c.getContentLengthLong();
        InputStream in = c.getInputStream();
        byte[] buf = new byte[128 * 1024];
        long done = 0;
        int r;
        long lastTick = 0;
        while ((r = in.read(buf)) > 0) {
            out.write(buf, 0, r);
            done += r;
            long now = System.currentTimeMillis();
            if (prog != null && now - lastTick > 130) {
                lastTick = now;
                if (!prog.onBytes(done, total)) {
                    try {
                        c.disconnect();
                    } catch (Exception ignored) {
                    }
                    throw new Cancelled();
                }
            }
        }
        in.close();
        out.flush();
        if (prog != null) prog.onBytes(done, total);
        c.disconnect();
        return done;
    }

    public static String readAll(InputStream in) throws IOException {
        if (in == null) return "";
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int r;
        while ((r = in.read(buf)) > 0) bos.write(buf, 0, r);
        in.close();
        return bos.toString("UTF-8");
    }

    public static String firstUrl(String body) {
        if (body == null) return null;
        for (String line : body.split("\n")) {
            line = line.trim();
            if (line.startsWith("http")) {
                int sp = line.indexOf(' ');
                return sp > 0 ? line.substring(0, sp) : line;
            }
        }
        return null;
    }

    public static String trim(String s, int n) {
        if (s == null) return "";
        s = s.replace("\n", " ").trim();
        return s.length() <= n ? s : s.substring(0, n) + "…";
    }
}
