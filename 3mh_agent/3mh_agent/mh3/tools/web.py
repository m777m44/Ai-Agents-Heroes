# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import asyncio
import ipaddress
import json
import re
import socket
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, quote, unquote, urlparse, urlunparse
import aiohttp
from . import ToolRegistry, truncate
_MAX_BYTES = 3 * 1024 * 1024
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36")
_UA_API = "3mh-agent/2.0 (+http://3mh.pages.dev; contact: t.me/j49_c)"
_WIKI_HOSTS = ("wikipedia.org", "wikimedia.org", "wiktionary.org", "wikidata.org", "wikibooks.org")


def _wiki_ua(settings: Any = None) -> str:
    ua = getattr(settings, "wiki_user_agent", "") if settings is not None else ""
    return ua or _UA_API


def _ua_for(url: str) -> str:
    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        return _UA
    return _UA_API if any(host == d or host.endswith("." + d) for d in _WIKI_HOSTS) else _UA
_SKIP_TAGS = {"script", "style", "noscript", "template", "svg", "head", "iframe", "form"}


class UnsafeURL(ValueError):
    pass


def _assert_public(url: str, *, allow_private: bool = False) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        raise UnsafeURL(f"البروتوكول غير مسموح: {parsed.scheme or '—'}")
    host = parsed.hostname or ""
    if not host:
        raise UnsafeURL("الرابط بلا اسم مضيف")
    if allow_private:
        return parsed.geturl()
    if host.lower() in ("localhost", "metadata.google.internal"):
        raise UnsafeURL("الوصول إلى localhost ممنوع")
    try:
        infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as exc:
        raise UnsafeURL(f"تعذّر حل اسم المضيف: {host}") from exc
    for info in infos:
        ip_str = info[4][0]
        try:
            ip = ipaddress.ip_address(ip_str.split("%")[0])
        except ValueError:
            continue
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise UnsafeURL(f"العنوان {ip_str} خاص/محلي — الوصول ممنوع")
    return parsed.geturl()


def _clean_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        raise UnsafeURL("رابط فارغ")
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    parsed = urlparse(url)
    if not parsed.path:
        url = urlunparse(parsed._replace(path="/"))
    return url


async def _fetch(
    url: str,
    *,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    body: Any = None,
    timeout: float = 25.0,
    max_bytes: int = _MAX_BYTES,
    allow_private: bool = False,
    user_agent: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Tuple[int, Dict[str, str], bytes, str]:
    final_url = _assert_public(_clean_url(url), allow_private=allow_private)
    if params:
        from urllib.parse import urlencode
        sep = "&" if "?" in final_url else "?"
        final_url = final_url + sep + urlencode({k: v for k, v in params.items() if v not in (None, "")})
    req_headers = {"User-Agent": user_agent or _ua_for(final_url),
                   "Accept": "*/*", "Accept-Language": "en,ar;q=0.8"}
    if headers:
        req_headers.update({str(k): str(v) for k, v in headers.items()})
    client_timeout = aiohttp.ClientTimeout(total=timeout, connect=12)
    connector = aiohttp.TCPConnector(limit=4, ssl=True, ttl_dns_cache=300)
    async with aiohttp.ClientSession(timeout=client_timeout, connector=connector) as session:
        kwargs: Dict[str, Any] = {"headers": req_headers, "allow_redirects": True, "max_redirects": 8}
        if body is not None:
            if isinstance(body, (dict, list)):
                kwargs["json"] = body
            else:
                kwargs["data"] = body
        async with session.request(method.upper(), final_url, **kwargs) as resp:
            chunks: List[bytes] = []
            total = 0
            async for chunk in resp.content.iter_chunked(64 * 1024):
                chunks.append(chunk)
                total += len(chunk)
                if total >= max_bytes:
                    break
            data = b"".join(chunks)[:max_bytes]
            return resp.status, dict(resp.headers), data, str(resp.url)


def _html_to_text(html: str) -> Dict[str, Any]:
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        title = (soup.title.get_text(strip=True) if soup.title else "") or ""
        desc = ""
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            desc = str(meta.get("content"))[:400]
        for tag in soup(list(_SKIP_TAGS)):
            tag.decompose()
        main = soup.find("main") or soup.find("article") or soup.find(attrs={"role": "main"})
        root = main or soup.body or soup
        text = root.get_text("\n")
        lines: List[str] = []
        for line in text.splitlines():
            line = re.sub(r"[ \t]+", " ", line).strip()
            if line:
                lines.append(line)
            elif lines and lines[-1] != "":
                lines.append("")
        links = []
        for a in soup.find_all("a", href=True)[:40]:
            href = str(a["href"]).strip()
            label = a.get_text(" ", strip=True)[:120]
            if href.startswith(("http://", "https://")) and label:
                links.append({"text": label, "url": href})
        return {"title": title, "description": desc, "text": "\n".join(lines), "links": links[:25]}
    except Exception:
        text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s{2,}", "\n", text)
        return {"title": "", "description": "", "text": text, "links": []}


def _decode_text(data: bytes, headers: Dict[str, str]) -> str:
    ctype = (headers.get("Content-Type") or headers.get("content-type") or "").lower()
    m = re.search(r"charset=([\w\-]+)", ctype)
    encoding = m.group(1) if m else "utf-8"
    try:
        return data.decode(encoding, errors="replace")
    except LookupError:
        return data.decode("utf-8", errors="replace")


def _ddg_redirect(href: str) -> str:
    if href.startswith("//"):
        href = "https:" + href
    if "duckduckgo.com/l/" in href or "uddg=" in href:
        qs = parse_qs(urlparse(href).query)
        if "uddg" in qs:
            return unquote(qs["uddg"][0])
    return href


def register(reg: ToolRegistry) -> None:
    t = reg.tool

    @t(name="web_fetch", category="web", needs_web=True, timeout=40,
       description=(
           "Fetch a web page and return its readable text content (HTML is stripped), plus "
           "title, description and links. Use it to read documentation, articles, APIs returning "
           "HTML, or any URL. Returns JSON/plain text as-is when the response is not HTML."
       ),
       parameters={
           "type": "object",
           "properties": {
               "url": {"type": "string", "description": "Full URL (https://…)"},
               "max_chars": {"type": "integer", "description": "Max characters of text to return (default 12000)"},
               "include_links": {"type": "boolean", "description": "Include extracted links (default false)"},
               "raw_html": {"type": "boolean", "description": "Return raw HTML instead of extracted text"},
           },
           "required": ["url"],
           "additionalProperties": False,
       })

    async def web_fetch(args: Dict[str, Any], ctx) -> Any:
        url = str(args.get("url") or "")
        max_chars = int(args.get("max_chars") or 12000)
        try:
            status, headers, data, final_url = await _fetch(
                url, timeout=30, allow_private=ctx.is_admin)
        except UnsafeURL as exc:
            return {"error": str(exc)}
        except asyncio.TimeoutError:
            return {"error": "انتهت مهلة الجلب (30 ثانية)", "url": url}
        except aiohttp.ClientError as exc:
            return {"error": f"فشل الاتصال: {type(exc).__name__}: {exc}"[:300], "url": url}
        ctype = (headers.get("Content-Type") or headers.get("content-type") or "").lower()
        out: Dict[str, Any] = {"url": final_url, "status": status, "content_type": ctype,
                               "bytes": len(data)}
        if "json" in ctype:
            try:
                out["json"] = json.loads(_decode_text(data, headers))
                out["text"] = truncate(json.dumps(out["json"], ensure_ascii=False, indent=1), max_chars)
            except Exception:
                out["text"] = truncate(_decode_text(data, headers), max_chars)
            return out
        body_text = _decode_text(data, headers)
        if "html" in ctype or body_text.lstrip()[:1] == "<":
            parsed = _html_to_text(body_text)
            if args.get("raw_html"):
                out["html"] = truncate(body_text, max_chars)
            else:
                out["title"] = parsed["title"]
                if parsed["description"]:
                    out["description"] = parsed["description"]
                out["text"] = truncate(parsed["text"], max_chars)
                if args.get("include_links"):
                    out["links"] = parsed["links"]
        else:
            out["text"] = truncate(body_text, max_chars)
        return out

    @t(name="web_search", category="web", needs_web=True, timeout=40,
       description=(
           "Search the public web and return ranked results (title, url, snippet). "
           "Use for current events, facts you are unsure about, prices, news, documentation, "
           "or anything after your knowledge cutoff. Combine with web_fetch to read a result. "
           "Supports Arabic and English queries."
       ),
       parameters={
           "type": "object",
           "properties": {
               "query": {"type": "string", "description": "Search query"},
               "max_results": {"type": "integer", "description": "Default 6, max 15"},
               "region": {"type": "string", "description": "e.g. ar-sa, us-en (optional)"},
               "time_filter": {"type": "string", "enum": ["d", "w", "m", "y"],
                               "description": "Restrict to day/week/month/year"},
           },
           "required": ["query"],
           "additionalProperties": False,
       })

    async def web_search(args: Dict[str, Any], ctx) -> Any:
        query = str(args.get("query") or "").strip()
        if not query:
            return {"error": "استعلام فارغ"}
        limit = min(max(int(args.get("max_results") or 6), 1), 15)
        region = str(args.get("region") or "")
        time_filter = str(args.get("time_filter") or "")
        allow_private = bool(ctx.is_admin)
        results: List[Dict[str, str]] = []
        engines: List[str] = []
        errors: List[str] = []
        try:
            api_results = await _api_search(query, limit=limit, settings=ctx.settings)
            if api_results:
                return {"query": query, "count": len(api_results),
                        "results": api_results[:limit], "engines_tried": ["api"], "errors": None}
        except Exception as exc:
            errors.append(f"api: {type(exc).__name__}: {exc}"[:160])
        for engine in (_ddg_search, _bing_search):
            try:
                batch = await engine(query, limit=limit, region=region,
                                     time_filter=time_filter, allow_private=allow_private)
            except Exception as exc:
                errors.append(f"{engine.__name__}: {type(exc).__name__}: {exc}"[:160])
                continue
            engines.append(engine.__name__.replace("_search", ""))
            if batch:
                results = batch
                break
        if not results:
            engines.append("wikipedia")
            wiki = await _wiki_search(query, lang="ar" if re.search(r"[\u0600-\u06FF]", query) else "en",
                                      limit=limit, allow_private=allow_private,
                                      user_agent=_wiki_ua(ctx.settings))
            results = [{"title": w["title"], "url": w["url"], "snippet": w.get("extract", "")}
                       for w in (wiki.get("results") or [])]
        if not results:
            return {"error": "لم يُعِد أي محرك نتائج (قد تكون محجوبة من شبكة الخادم)",
                    "query": query, "engines_tried": engines, "details": errors[:3],
                    "hint": "جرّب web_fetch على رابط معروف مباشرة، أو wikipedia، أو http_request على واجهة برمجية."}
        return {"query": query, "count": len(results), "results": results[:limit],
                "engines_tried": engines, "errors": errors[:2] if errors else None}

    @t(name="wikipedia", category="web", needs_web=True, timeout=30,
       description=(
           "Look up an encyclopedic topic on Wikipedia. Use 'search' to find pages, "
           "'summary' for a short overview, 'extract' for longer plain text, and 'page' for "
           "the full article text. Supports any language code (ar, en, fr, …)."
       ),
       parameters={
           "type": "object",
           "properties": {
               "operation": {"type": "string", "enum": ["search", "summary", "extract", "page"]},
               "title": {"type": "string", "description": "Page title or search query"},
               "lang": {"type": "string", "description": "Wikipedia language code (default: en)"},
               "max_chars": {"type": "integer", "description": "Max characters (default 6000)"},
               "limit": {"type": "integer"},
           },
           "required": ["operation", "title"],
           "additionalProperties": False,
       })

    async def wikipedia(args: Dict[str, Any], ctx) -> Any:
        op = str(args.get("operation") or "search")
        title = str(args.get("title") or "").strip()
        lang = re.sub(r"[^\w\-]", "", str(args.get("lang") or "en"))[:8] or "en"
        limit = min(int(args.get("max_chars") or 6000), 40000)
        if op == "search":
            return await _wiki_search(title, lang=lang, limit=int(args.get("limit") or 6))
        if op == "summary":
            url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(title.replace(' ', '_'))}"
            try:
                status, headers, data, final_url = await _fetch(url, timeout=20,
                                                            user_agent=_wiki_ua(ctx.settings))
            except (UnsafeURL, aiohttp.ClientError, asyncio.TimeoutError) as exc:
                return {"error": f"فشل الاتصال: {exc}"}
            if status != 200:
                return {"error": f"لم تُوجد الصفحة (HTTP {status})", "title": title}
            try:
                payload = json.loads(_decode_text(data, headers))
            except Exception:
                return {"error": "استجابة غير صالحة"}
            return {"title": payload.get("title"), "extract": payload.get("extract", "")[:limit],
                    "url": payload.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "description": payload.get("description", "")}
        params = {
            "action": "query", "prop": "extracts", "explaintext": "1",
            "titles": title, "format": "json", "redirects": "1",
        }
        if op == "extract":
            params["exintro"] = "1"
        url = f"https://{lang}.wikipedia.org/w/api.php?" + "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
        try:
            status, headers, data, final_url = await _fetch(url, timeout=25,
                                                            user_agent=_wiki_ua(ctx.settings))
        except (UnsafeURL, aiohttp.ClientError, asyncio.TimeoutError) as exc:
            return {"error": f"فشل الاتصال: {exc}"}
        try:
            payload = json.loads(_decode_text(data, headers))
            pages = payload.get("query", {}).get("pages", {})
            page = next(iter(pages.values()), {})
            text = page.get("extract", "")
            return {"title": page.get("title"), "chars": len(text),
                    "text": truncate(text, limit),
                    "url": f"https://{lang}.wikipedia.org/?curid={page.get('pageid')}"}
        except Exception as exc:
            return {"error": f"تعذّر تحليل الاستجابة: {exc}"}

    @t(name="http_request", category="web", needs_web=True, timeout=45,
       description=(
           "Perform a raw HTTP request to any public API and return status, headers and body. "
           "Supports GET/POST/PUT/PATCH/DELETE, custom headers, query params, JSON or text body. "
           "Use it for REST APIs, webhooks, downloading JSON/CSV/XML data. "
           "Private/localhost addresses are blocked for non-admin users."
       ),
       parameters={
           "type": "object",
           "properties": {
               "url": {"type": "string"},
               "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"]},
               "headers": {"type": "object", "description": "Header name → value"},
               "params": {"type": "object", "description": "Query parameters"},
               "body": {"description": "JSON object or raw text body"},
               "max_chars": {"type": "integer", "description": "Truncate response body (default 12000)"},
               "timeout_seconds": {"type": "integer"},
           },
           "required": ["url"],
           "additionalProperties": False,
       })

    async def http_request(args: Dict[str, Any], ctx) -> Any:
        url = str(args.get("url") or "")
        params = args.get("params")
        if isinstance(params, dict) and params:
            sep = "&" if "?" in url else "?"
            url = url + sep + "&".join(f"{quote(str(k))}={quote(str(v))}" for k, v in params.items())
        try:
            status, headers, data, final_url = await _fetch(
                url,
                method=str(args.get("method") or "GET"),
                headers=args.get("headers") if isinstance(args.get("headers"), dict) else None,
                body=args.get("body"),
                timeout=min(float(args.get("timeout_seconds") or 25), 40),
                allow_private=ctx.is_admin,
            )
        except UnsafeURL as exc:
            return {"error": str(exc)}
        except asyncio.TimeoutError:
            return {"error": "انتهت مهلة الطلب"}
        except aiohttp.ClientError as exc:
            return {"error": f"{type(exc).__name__}: {exc}"[:300]}
        text = _decode_text(data, headers)
        max_chars = int(args.get("max_chars") or 12000)
        out: Dict[str, Any] = {"status": status, "url": final_url,
                               "headers": {k: v for k, v in list(headers.items())[:25]}}
        try:
            out["json"] = json.loads(text)
            out["body"] = truncate(json.dumps(out["json"], ensure_ascii=False, indent=1), max_chars)
        except Exception:
            out["body"] = truncate(text, max_chars)
        return out

    @t(name="url_info", category="web", needs_web=True, timeout=25,
       description="Check a URL: does it resolve, what status/redirects/content-type/size, without downloading the full body.",
       parameters={
           "type": "object",
           "properties": {"url": {"type": "string"}, "follow": {"type": "boolean"}},
           "required": ["url"],
           "additionalProperties": False,
       })

    async def url_info(args: Dict[str, Any], ctx) -> Any:
        url = str(args.get("url") or "")
        try:
            clean = _assert_public(_clean_url(url), allow_private=ctx.is_admin)
        except UnsafeURL as exc:
            return {"error": str(exc)}
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.head(clean, headers={"User-Agent": _UA},
                                        allow_redirects=bool(args.get("follow", True))) as resp:
                    return {"url": str(resp.url), "status": resp.status,
                            "content_type": resp.headers.get("Content-Type"),
                            "content_length": resp.headers.get("Content-Length"),
                            "server": resp.headers.get("Server")}
        except Exception as exc:
            return {"error": f"{type(exc).__name__}: {exc}"[:250], "url": url}


async def _ddg_search(query: str, *, limit: int = 6, region: str = "",
                      time_filter: str = "", allow_private: bool = False) -> List[Dict[str, str]]:
    params: Dict[str, Any] = {"q": query, "kl": region or "wt-wt"}
    if time_filter in ("d", "w", "m", "y"):
        params["df"] = time_filter
    status, headers, data, _final = await _fetch(
        "https://html.duckduckgo.com/html/", params=params, timeout=20,
        allow_private=allow_private)
    if status != 200 or b"result__a" not in data:
        lite_status, lite_headers, lite_data, _ = await _fetch(
            "https://lite.duckduckgo.com/lite/", params=params, timeout=20,
            allow_private=allow_private)
        if lite_status == 200 and b"result-link" in lite_data:
            return _parse_ddg_lite(_decode_text(lite_data, lite_headers), limit)
        return []
    html = _decode_text(data, headers)
    results: List[Dict[str, str]] = []
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.select("div.result, div.web-result"):
            anchor = item.select_one("a.result__a")
            if not anchor:
                continue
            snippet_el = item.select_one(".result__snippet")
            url = _ddg_redirect(str(anchor.get("href", "")))
            if not url.startswith("http"):
                continue
            results.append({
                "title": anchor.get_text(" ", strip=True)[:200],
                "url": url,
                "snippet": (snippet_el.get_text(" ", strip=True)[:400] if snippet_el else ""),
            })
            if len(results) >= limit:
                break
    except Exception:
        pattern = re.compile(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S)
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.S)
        for idx, m in enumerate(pattern.finditer(html)):
            if len(results) >= limit:
                break
            url = _ddg_redirect(m.group(1))
            if not url.startswith("http"):
                continue
            results.append({
                "title": re.sub(r"<[^>]+>", "", m.group(2)).strip()[:200],
                "url": url,
                "snippet": re.sub(r"<[^>]+>", "", snippets[idx]).strip()[:400]
                if idx < len(snippets) else "",
            })
    return results


def _parse_ddg_lite(html: str, limit: int) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        anchors = soup.select("a.result-link")
        snippets = [td.get_text(" ", strip=True)
                    for td in soup.select("td.result-snippet")]
        for idx, anchor in enumerate(anchors[:limit]):
            url = _ddg_redirect(str(anchor.get("href", "")))
            if not url.startswith("http"):
                continue
            results.append({
                "title": anchor.get_text(" ", strip=True)[:200],
                "url": url,
                "snippet": snippets[idx][:400] if idx < len(snippets) else "",
            })
    except Exception:
        for m in re.finditer(r'<a[^>]+class="result-link"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                             html, re.S):
            if len(results) >= limit:
                break
            url = _ddg_redirect(m.group(1))
            results.append({"title": re.sub(r"<[^>]+>", "", m.group(2)).strip()[:200],
                            "url": url, "snippet": ""})
    return results


def _decode_bing_url(href: str) -> str:
    if "bing.com/ck/" not in href:
        return href
    try:
        import base64
        values = parse_qs(urlparse(href).query).get("u", [])
        if values and values[0].startswith("a1"):
            payload = values[0][2:]
            payload += "=" * (-len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload).decode("utf-8", "replace")
            if decoded.startswith("http"):
                return decoded
    except Exception:
        pass
    return href


async def _api_search(query: str, *, limit: int, settings: Any) -> List[Dict[str, str]]:
    provider = str(getattr(settings, "search_provider", "auto") or "auto").lower()
    key = str(getattr(settings, "search_api_key", "") or "")
    searxng = str(getattr(settings, "searxng_url", "") or "")
    if provider == "auto":
        if key:
            provider = "tavily"
        elif searxng:
            provider = "searxng"
        else:
            return []
    if provider == "tavily" and key:
        st, hd, data, _ = await _fetch(
            "https://api.tavily.com/search", method="POST",
            headers={"Content-Type": "application/json"},
            body={"api_key": key, "query": query, "max_results": limit, "include_answer": False},
            timeout=25)
        if st != 200:
            return []
        payload = json.loads(_decode_text(data, hd))
        return [{"title": str(r.get("title", ""))[:200], "url": str(r.get("url", "")),
                 "snippet": str(r.get("content", ""))[:400]}
                for r in (payload.get("results") or [])[:limit]]
    if provider == "brave" and key:
        st, hd, data, _ = await _fetch(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": str(limit)},
            headers={"X-Subscription-Token": key, "Accept": "application/json"}, timeout=25)
        if st != 200:
            return []
        payload = json.loads(_decode_text(data, hd))
        return [{"title": str(r.get("title", ""))[:200], "url": str(r.get("url", "")),
                 "snippet": str((r.get("description") or ""))[:400]}
                for r in ((payload.get("web") or {}).get("results") or [])[:limit]]
    if provider == "serper" and key:
        st, hd, data, _ = await _fetch(
            "https://google.serper.dev/search", method="POST",
            headers={"X-API-KEY": key, "Content-Type": "application/json"},
            body={"q": query, "num": limit}, timeout=25)
        if st != 200:
            return []
        payload = json.loads(_decode_text(data, hd))
        return [{"title": str(r.get("title", ""))[:200], "url": str(r.get("link", "")),
                 "snippet": str(r.get("snippet", ""))[:400]}
                for r in (payload.get("organic") or [])[:limit]]
    if provider == "searxng" and searxng:
        st, hd, data, _ = await _fetch(
            searxng.rstrip("/") + "/search",
            params={"q": query, "format": "json"}, timeout=25)
        if st != 200:
            return []
        payload = json.loads(_decode_text(data, hd))
        return [{"title": str(r.get("title", ""))[:200], "url": str(r.get("url", "")),
                 "snippet": str(r.get("content", ""))[:400]}
                for r in (payload.get("results") or [])[:limit]]
    return []


async def _bing_search(query: str, *, limit: int = 6, region: str = "",
                       time_filter: str = "", allow_private: bool = False) -> List[Dict[str, str]]:
    params: Dict[str, Any] = {"q": query, "count": str(min(limit * 2, 20)), "setlang": "en"}
    if region:
        params["mkt"] = region.replace("-", "_") if "-" in region else region
    if time_filter in ("d", "w", "m", "y"):
        params["qft"] = {"d": 'interval~"7"', "w": 'interval~"8"',
                         "m": 'interval~"9"', "y": 'interval~"10"'}[time_filter]
    status, headers, data, _final = await _fetch(
        "https://www.bing.com/search", params=params, timeout=20, allow_private=allow_private)
    if status != 200:
        return []
    html = _decode_text(data, headers)
    results: List[Dict[str, str]] = []
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.select("li.b_algo"):
            anchor = item.select_one("h2 a[href]")
            if not anchor:
                continue
            url = str(anchor.get("href", ""))
            if not url.startswith("http"):
                continue
            snippet_el = item.select_one(".b_caption p, p.b_lineclamp2, p")
            results.append({
                "title": anchor.get_text(" ", strip=True)[:200],
                "url": _decode_bing_url(url),
                "snippet": (snippet_el.get_text(" ", strip=True)[:400] if snippet_el else ""),
            })
            if len(results) >= limit:
                break
    except Exception:
        for m in re.finditer(r'<li class="b_algo".*?<h2><a href="(http[^"]+)"[^>]*>(.*?)</a>', html, re.S):
            if len(results) >= limit:
                break
            results.append({"title": re.sub(r"<[^>]+>", "", m.group(2)).strip()[:200],
                            "url": _decode_bing_url(m.group(1)), "snippet": ""})
    return results


async def _wiki_search(query: str, lang: str = "en", limit: int = 6,
                       allow_private: bool = False,
                       user_agent: Optional[str] = None) -> Dict[str, Any]:
    lang = re.sub(r"[^\w\-]", "", lang)[:8] or "en"
    url = ("https://%s.wikipedia.org/w/api.php?action=query&list=search&srsearch=%s"
           "&srlimit=%d&format=json&utf8=1" % (lang, quote(query), min(limit, 20)))
    try:
        status, headers, data, final_url = await _fetch(url, timeout=20,
                                                        allow_private=allow_private,
                                                        user_agent=user_agent or _UA_API)
        payload = json.loads(_decode_text(data, headers))
        items = payload.get("query", {}).get("search", [])
        results = []
        for item in items[:limit]:
            snippet = re.sub(r"<[^>]+>", "", str(item.get("snippet", "")))
            results.append({
                "title": item.get("title"),
                "url": f"https://{lang}.wikipedia.org/wiki/{quote(str(item.get('title', '')).replace(' ', '_'))}",
                "extract": snippet,
                "wordcount": item.get("wordcount"),
            })
        return {"query": query, "lang": lang, "count": len(results), "results": results}
    except Exception as exc:
        return {"query": query, "lang": lang, "error": f"{type(exc).__name__}: {exc}"[:200], "results": []}
