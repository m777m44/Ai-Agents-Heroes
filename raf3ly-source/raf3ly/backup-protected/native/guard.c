/*
 * Raf3ly native guard  (v5)
 *
 * Everything that decides "is this binary still mine?" lives in machine code and
 * reads the *installed APK file* directly:
 *   - install directory is derived from this library's own mapping (dladdr) -> kernel truth
 *   - the signing certificate is parsed out of the APK Signature Scheme v2 block
 *     in C, so spoofing PackageManager / getPackageCodePath() in memory is useless
 *   - this library hashes its own bytes (self-hash) and its own classes.dex
 *   - a private pthread watchdog re-runs every check and kills the process with
 *     SIGKILL on its own, without going through Java (patching Java cannot stop it)
 */
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <jni.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <pthread.h>
#include <dlfcn.h>

#include "strings_enc.h"

#if defined(__aarch64__)
#define SELF_SLOT 0
#elif defined(__arm__)
#define SELF_SLOT 1
#elif defined(__x86_64__)
#define SELF_SLOT 2
#elif defined(__i386__)
#define SELF_SLOT 3
#else
#define SELF_SLOT 0
#endif

/* volatile key: stops the optimiser from folding the decrypted string back into .rodata */
#define DECL(n, buf) unsigned char buf[sizeof(n##_A) + 1]; \
    volatile unsigned char n##_k = (unsigned char) n##_KEY; \
    for (unsigned i = 0; i < sizeof(n##_A); i++) buf[i] = (unsigned char) (n##_A[i] ^ n##_k); \
    buf[sizeof(n##_A)] = 0;

/* ---------------- SHA-256 ---------------- */
static const uint32_t K256[64] = {
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};

#define ROR(x,n) (((x) >> (n)) | ((x) << (32 - (n))))

static void sha256_block(uint32_t *h, const unsigned char *p) {
    uint32_t w[64], a, b, c, d, e, f, g, k, t1, t2;
    for (int i = 0; i < 16; i++)
        w[i] = (uint32_t) p[i*4] << 24 | (uint32_t) p[i*4+1] << 16 | (uint32_t) p[i*4+2] << 8 | (uint32_t) p[i*4+3];
    for (int i = 16; i < 64; i++) {
        uint32_t s0 = ROR(w[i-15], 7) ^ ROR(w[i-15], 18) ^ (w[i-15] >> 3);
        uint32_t s1 = ROR(w[i-2], 17) ^ ROR(w[i-2], 19) ^ (w[i-2] >> 10);
        w[i] = w[i-16] + s0 + w[i-7] + s1;
    }
    a=h[0]; b=h[1]; c=h[2]; d=h[3]; e=h[4]; f=h[5]; g=h[6]; k=h[7];
    for (int i = 0; i < 64; i++) {
        uint32_t S1 = ROR(e,6) ^ ROR(e,11) ^ ROR(e,25);
        uint32_t ch = (e & f) ^ (~e & g);
        t1 = k + S1 + ch + K256[i] + w[i];
        uint32_t S0 = ROR(a,2) ^ ROR(a,13) ^ ROR(a,22);
        uint32_t mj = (a & b) ^ (a & c) ^ (b & c);
        t2 = S0 + mj;
        k=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
    }
    h[0]+=a; h[1]+=b; h[2]+=c; h[3]+=d; h[4]+=e; h[5]+=f; h[6]+=g; h[7]+=k;
}

static void sha_init(uint32_t *h) {
    h[0]=0x6a09e667; h[1]=0xbb67ae85; h[2]=0x3c6ef372; h[3]=0xa54ff53a;
    h[4]=0x510e527f; h[5]=0x9b05688c; h[6]=0x1f83d9ab; h[7]=0x5be0cd19;
}

static void sha_final(uint32_t *h, const unsigned char *tail, int taillen, uint64_t total,
                      unsigned char *out) {
    unsigned char blk[128];
    uint64_t bits = total * 8;
    int n = taillen;
    memset(blk, 0, sizeof(blk));
    memcpy(blk, tail, (size_t) n);
    blk[n++] = 0x80;
    if (n > 56) { sha256_block(h, blk); memset(blk, 0, sizeof(blk)); n = 0; }
    for (int i = 0; i < 8; i++) blk[56 + i] = (unsigned char) (bits >> (56 - i*8));
    sha256_block(h, blk);
    for (int i = 0; i < 8; i++) {
        out[i*4]   = (unsigned char) (h[i] >> 24);
        out[i*4+1] = (unsigned char) (h[i] >> 16);
        out[i*4+2] = (unsigned char) (h[i] >> 8);
        out[i*4+3] = (unsigned char) h[i];
    }
}

/* hashes `len` bytes read from f starting at `off` (streaming) */
static int sha_file_range(FILE *f, long off, uint32_t len, unsigned char *out) {
    if (fseek(f, off, SEEK_SET) != 0) return 0;
    uint32_t H[8];
    sha_init(H);
    unsigned char buf[65536], rest[128];
    int restlen = 0;
    uint64_t total = 0;
    uint32_t left = len;
    while (left > 0) {
        size_t want = left < sizeof(buf) ? left : sizeof(buf);
        size_t got = fread(buf, 1, want, f);
        if (!got) return 0;
        total += got;
        left -= (uint32_t) got;
        size_t o = 0;
        if (restlen) {
            size_t need = (size_t) (64 - restlen);
            if (need > got) need = got;
            memcpy(rest + restlen, buf, need);
            restlen += (int) need;
            o = need;
            if (restlen == 64) { sha256_block(H, rest); restlen = 0; }
        }
        while (o + 64 <= got) { sha256_block(H, buf + o); o += 64; }
        if (got > o) { restlen = (int) (got - o); memcpy(rest, buf + o, (size_t) restlen); }
    }
    sha_final(H, rest, restlen, total, out);
    return 1;
}

static int sha_file(const char *path, unsigned char *out) {
    FILE *f = fopen(path, "rb");
    if (!f) return 0;
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return 0; }
    long size = ftell(f);
    if (size <= 0) { fclose(f); return 0; }
    int ok = sha_file_range(f, 0, (uint32_t) size, out);
    fclose(f);
    return ok;
}

/* ---------------- tiny ZIP reader ---------------- */
static uint32_t rd32(const unsigned char *p) {
    return (uint32_t) p[0] | (uint32_t) p[1] << 8 | (uint32_t) p[2] << 16 | (uint32_t) p[3] << 24;
}
static uint16_t rd16(const unsigned char *p) {
    return (uint16_t) ((uint16_t) p[0] | (uint16_t) p[1] << 8);
}
static uint64_t rd64(const unsigned char *p) {
    uint64_t v = 0;
    for (int i = 7; i >= 0; i--) v = (v << 8) | p[i];
    return v;
}

typedef struct { long cdOffset; uint32_t cdCount; uint32_t cdSize; long fileSize; } ZipInfo;

static int zip_info(FILE *f, ZipInfo *zi) {
    if (fseek(f, 0, SEEK_END) != 0) return 0;
    long size = ftell(f);
    if (size < 22) return 0;
    long tailLen = size < 65557 ? size : 65557;
    unsigned char *tail = (unsigned char *) malloc((size_t) tailLen);
    if (!tail) return 0;
    if (fseek(f, size - tailLen, SEEK_SET) != 0) { free(tail); return 0; }
    if (fread(tail, 1, (size_t) tailLen, f) != (size_t) tailLen) { free(tail); return 0; }
    long eocd = -1;
    for (long i = tailLen - 22; i >= 0; i--) {
        if (tail[i] == 0x50 && tail[i+1] == 0x4b && tail[i+2] == 0x05 && tail[i+3] == 0x06) { eocd = i; break; }
    }
    if (eocd < 0) { free(tail); return 0; }
    zi->cdCount = rd16(tail + eocd + 10);
    zi->cdSize = rd32(tail + eocd + 12);
    zi->cdOffset = (long) rd32(tail + eocd + 16);
    zi->fileSize = size;
    free(tail);
    return 1;
}

/* SHA-256 of a STORED entry; *notStored set when the entry is compressed */
static int hash_zip_entry(FILE *f, const char *want, unsigned char *out, int *notStored) {
    ZipInfo zi;
    if (!zip_info(f, &zi)) return 0;
    uint32_t pos = (uint32_t) zi.cdOffset;
    for (uint32_t i = 0; i < zi.cdCount; i++) {
        unsigned char hdr[46];
        if (fseek(f, pos, SEEK_SET) != 0) return 0;
        if (fread(hdr, 1, 46, f) != 46) return 0;
        if (!(hdr[0] == 0x50 && hdr[1] == 0x4b && hdr[2] == 0x01 && hdr[3] == 0x02)) return 0;
        uint16_t method = rd16(hdr + 10);
        uint32_t csize = rd32(hdr + 20);
        uint16_t nlen = rd16(hdr + 28), elen = rd16(hdr + 30), clen = rd16(hdr + 32);
        uint32_t lho = rd32(hdr + 42);
        char name[256];
        if (nlen < sizeof(name)) {
            if (fread(name, 1, nlen, f) != nlen) return 0;
            name[nlen] = 0;
            if (strcmp(name, want) == 0) {
                if (method != 0) { *notStored = 1; return 0; }
                unsigned char lh[30];
                if (fseek(f, lho, SEEK_SET) != 0) return 0;
                if (fread(lh, 1, 30, f) != 30) return 0;
                long data = (long) lho + 30 + rd16(lh + 26) + rd16(lh + 28);
                return sha_file_range(f, data, csize, out);
            }
        }
        pos += 46u + nlen + elen + clen;
    }
    return 0;
}

/* ---------------- APK Signature Scheme v2: extract signer certificate ---------------- */
/* Fills out[32] with the SHA-256 of the first signer certificate. */
static int v2_cert_digest(FILE *f, unsigned char *out) {
    ZipInfo zi;
    if (!zip_info(f, &zi)) return 0;
    if (zi.cdOffset < 32) return 0;

    unsigned char tailhdr[24];
    if (fseek(f, zi.cdOffset - 24, SEEK_SET) != 0) return 0;
    if (fread(tailhdr, 1, 24, f) != 24) return 0;
    static const char magic[16] = {'A','P','K',' ','S','i','g',' ','B','l','o','c','k',' ','4','2'};
    if (memcmp(tailhdr + 8, magic, 16) != 0) return 0;

    uint64_t blockSize = rd64(tailhdr);
    long blockStart = zi.cdOffset - 8 - (long) blockSize;
    if (blockStart < 0 || blockSize < 32 || blockSize > (uint64_t) zi.fileSize) return 0;

    unsigned char *blk = (unsigned char *) malloc((size_t) blockSize);
    if (!blk) return 0;
    if (fseek(f, blockStart, SEEK_SET) != 0) { free(blk); return 0; }
    if (fread(blk, 1, (size_t) blockSize, f) != (size_t) blockSize) { free(blk); return 0; }

    int rc = 0;
    size_t off = 8;                                     /* skip size */
    size_t end = (size_t) blockSize - 24;               /* skip footer */
    while (off + 12 <= end) {
        uint64_t pairLen = rd64(blk + off);
        if (pairLen < 4 || off + 8 + pairLen > end) break;
        uint32_t id = rd32(blk + off + 8);
        const unsigned char *val = blk + off + 12;
        uint32_t vlen = (uint32_t) (pairLen - 4);
        if (id == 0x7109871a) {                         /* v2 block */
            if (vlen < 8) break;
            uint32_t p = 0;
            uint32_t signersLen = rd32(val + p); p += 4;
            if (p + signersLen > vlen || signersLen < 8) break;
            uint32_t signerLen = rd32(val + p); p += 4;
            if (p + signerLen > vlen || signerLen < 8) break;
            uint32_t sdLen = rd32(val + p); p += 4;
            if (p + sdLen > vlen) break;
            uint32_t q = p;
            uint32_t digLen = rd32(val + q); q += 4;    /* digests */
            if (q + digLen > p + sdLen) break;
            q += digLen;
            uint32_t certsLen = rd32(val + q); q += 4;  /* certificates */
            if (q + certsLen > p + sdLen || certsLen < 4) break;
            uint32_t certLen = rd32(val + q); q += 4;
            if (q + certLen > p + sdLen || certLen < 32) break;
            if (certLen <= 65536) {
                uint32_t H[8];
                sha_init(H);
                uint32_t i = 0;
                while (certLen - i >= 64) { sha256_block(H, val + q + i); i += 64; }
                sha_final(H, val + q + i, (int) (certLen - i), certLen, out);
                rc = 1;
                break;
            }
        }
        off += 8 + (size_t) pairLen;
    }
    free(blk);
    return rc;
}

/* ---------------- install path from the kernel ---------------- */
static int self_path(char *out, size_t n) {
    Dl_info info;
    if (!dladdr((void *) self_path, &info) || !info.dli_fname) return 0;
    strncpy(out, info.dli_fname, n - 1);
    out[n - 1] = 0;
    return out[0] != 0;
}

static int app_dir(char *out, size_t n) {
    char p[512];
    if (!self_path(p, sizeof(p))) return 0;
    for (int i = 0; i < 3; i++) {                     /* file, abi, lib */
        char *s = strrchr(p, '/');
        if (!s) return 0;
        *s = 0;
    }
    if (!p[0]) return 0;
    strncpy(out, p, n - 1);
    out[n - 1] = 0;
    return 1;
}

/* ---------------- state shared with the watchdog ---------------- */
static unsigned char g_dexWant[32], g_selfWant[32], g_certWant[32];
static char g_apk[600];
static volatile int g_armed = 0;
static volatile int g_failed = 0;

static int eq32(const unsigned char *a, const unsigned char *b) {
    unsigned char d = 0;
    for (int i = 0; i < 32; i++) d |= (unsigned char) (a[i] ^ b[i]);
    return d == 0;
}

static int take(JNIEnv *env, jbyteArray arr, unsigned char *out) {
    if (!arr) return 0;
    if ((*env)->GetArrayLength(env, arr) < 32) return 0;
    (*env)->GetByteArrayRegion(env, arr, 0, 32, (jbyte *) out);
    return 1;
}

/* full re-check; returns 0 when everything still matches */
static int recheck(void) {
    unsigned char got[32];
    if (!g_armed || !g_apk[0]) return 1;

    FILE *f = fopen(g_apk, "rb");
    if (!f) return 1;
    DECL(S_CLASSES, cls)
    int notStored = 0;
    int ok = hash_zip_entry(f, (const char *) cls, got, &notStored);
    unsigned char cert[32];
    int okCert = v2_cert_digest(f, cert);
    fclose(f);
    if (!ok || !okCert) return 1;
    if (!eq32(got, g_dexWant)) return 1;
    if (!eq32(cert, g_certWant)) return 1;

    char sp[512];
    if (!self_path(sp, sizeof(sp))) return 1;
    if (!sha_file(sp, got) || !eq32(got, g_selfWant)) return 1;

    DECL(S_MAPS, maps)
    f = fopen((const char *) maps, "re");
    if (!f) return 1;
    DECL(S_KILLER, k1) DECL(S_FRIDA, k2) DECL(S_XPOSED, k3) DECL(S_LSPD, k4)
    DECL(S_SUBSTRATE, k5) DECL(S_GUM, k6)
    char line[512];
    int hooked = 0;
    while (fgets(line, sizeof(line), f)) {
        if (strstr(line, (const char *) k1) || strstr(line, (const char *) k2) ||
            strstr(line, (const char *) k3) || strstr(line, (const char *) k4) ||
            strstr(line, (const char *) k5) || strstr(line, (const char *) k6)) { hooked = 1; break; }
    }
    fclose(f);
    if (hooked) return 1;

    DECL(S_STATUS, st)
    f = fopen((const char *) st, "re");
    if (!f) return 1;
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "TracerPid:", 10) == 0) {
            const char *v = line + 10;
            while (*v == ' ' || *v == '\t') v++;
            if (*v && *v != '0') { fclose(f); return 1; }
        }
    }
    fclose(f);
    return 0;
}

static void *watchdog(void *arg) {
    (void) arg;
    for (;;) {
        sleep(18 + (unsigned) (getpid() % 12));
        if (recheck() != 0) {
            g_failed = 1;
            kill(getpid(), SIGKILL);      /* native kill: independent of Java */
            _exit(9);
        }
    }
    return NULL;
}

/* ---------------- JNI ---------------- */
/*
 * mask bits (0 == trusted):
 *  1  classes.dex digest != recorded
 *  2  signing certificate != recorded (parsed from the v2 block in C)
 *  4  Java-reported dex digest != kernel-read digest  (path spoofing)
 *  8  APK layout unexpected (entry missing / recompressed / no v2 block)
 * 16  hooking engine present in this process
 * 32  this library's own bytes != recorded (native patch)
 */
__attribute__((visibility("default")))
jint JNICALL Java_com_raf3ly_app_N_probe(JNIEnv *env, jclass cls,
                                        jbyteArray dexWantArr, jbyteArray dexJavaArr,
                                        jbyteArray certWantArr, jbyteArray selfWantArr) {
    unsigned char dexJava[32];
    int mask = 0;

    if (!take(env, dexWantArr, g_dexWant)) mask |= 8;
    if (!take(env, certWantArr, g_certWant)) mask |= 8;
    if (!selfWantArr || (*env)->GetArrayLength(env, selfWantArr) < 32 * (SELF_SLOT + 1)) {
        mask |= 32;
    } else {
        (*env)->GetByteArrayRegion(env, selfWantArr, 32 * SELF_SLOT, 32, (jbyte *) g_selfWant);
    }
    int haveJava = take(env, dexJavaArr, dexJava);

    char selfsrc[512];
    if (!self_path(selfsrc, sizeof(selfsrc))) {
        mask |= 8;
    } else if (strstr(selfsrc, ".apk")) {
        /* extractNativeLibs=false: the library is mapped straight out of the APK */
        snprintf(g_apk, sizeof(g_apk), "%s", selfsrc);
    }
    char dir[512];
    if (mask == 0 && !g_apk[0] && app_dir(dir, sizeof(dir))) {
        DECL(S_BASEAPK, apkname)
        snprintf(g_apk, sizeof(g_apk), "%s/%s", dir, (const char *) apkname);
    }
    if (!g_apk[0]) {
        mask |= 8;
    } else {
        FILE *f = fopen(g_apk, "rb");
        if (!f) {
            mask |= 8;
        } else {
            unsigned char real[32], cert[32];
            DECL(S_CLASSES, cls2)
            int notStored = 0;
            if (!hash_zip_entry(f, (const char *) cls2, real, &notStored)) mask |= 8;
            else {
                if (!eq32(g_dexWant, real)) mask |= 1;
                if (!haveJava || !eq32(dexJava, real)) mask |= 4;
            }
            if (!v2_cert_digest(f, cert)) mask |= 8;
            else if (!eq32(cert, g_certWant)) mask |= 2;
            fclose(f);
        }
    }

    char sp[512];
    if (!self_path(sp, sizeof(sp))) mask |= 32;
    else {
        unsigned char got[32];
        if (!sha_file(sp, got) || !eq32(got, g_selfWant)) mask |= 32;
    }

    if (mask == 0) {
        g_armed = 1;
        pthread_t t;
        pthread_create(&t, NULL, watchdog, NULL);
        pthread_detach(t);
    }
    if (mask != 0) mask ^= 0x5A;
    return mask;
}

__attribute__((visibility("default")))
jint JNICALL JNI_OnLoad(JavaVM *vm, void *reserved) {
    return JNI_VERSION_1_6;
}
