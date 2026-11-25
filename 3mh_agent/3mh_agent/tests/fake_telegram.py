# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import json
import time
from typing import Any, Dict, List, Optional, Tuple
from telegram import Bot, Update
from telegram.request import BaseRequest, RequestData
__all__ = ["FakeRequest", "make_bot", "text_update", "photo_update", "callback_update"]


class FakeRequest(BaseRequest):

    def __init__(self, *, fail_methods: Optional[Dict[str, Exception]] = None) -> None:
        self.calls: List[Tuple[str, Dict[str, Any]]] = []
        self.fail_methods = fail_methods or {}
        self._message_id = 100

    @property
    def read_timeout(self) -> float:
        return 10.0

    async def initialize(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None

    async def do_request(
        self,
        url: str,
        method: str,
        request_data: Optional[RequestData] = None,
        read_timeout: Any = None,
        write_timeout: Any = None,
        connect_timeout: Any = None,
        pool_timeout: Any = None,
    ) -> Tuple[int, bytes]:
        api_method = url.rstrip("/").rsplit("/", 1)[-1]
        params: Dict[str, Any] = {}
        if request_data is not None:
            try:
                params = dict(request_data.json_parameters or {})
            except Exception:
                params = {}
        self.calls.append((api_method, params))
        exc = self.fail_methods.get(api_method)
        if exc is not None:
            raise exc
        self._message_id += 1
        chat_id = params.get("chat_id", 42)
        result: Any = True
        if api_method == "getMe":
            result = {"id": 777, "is_bot": True, "first_name": "CF Agent",
                      "username": "cf_agent_test_bot", "can_join_groups": True,
                      "can_read_all_group_messages": False, "supports_inline_queries": False}
        elif api_method in ("sendMessage", "sendDocument", "sendPhoto", "editMessageText"):
            result = {
                "message_id": self._message_id,
                "date": int(time.time()),
                "chat": {"id": int(chat_id) if str(chat_id).lstrip("-").isdigit() else 42,
                         "type": "private", "first_name": "Tester"},
                "from": {"id": 777, "is_bot": True, "first_name": "CF Agent",
                         "username": "cf_agent_test_bot"},
                "text": str(params.get("text", ""))[:4096],
            }
        elif api_method == "getUpdates":
            result = []
        body = json.dumps({"ok": True, "result": result}).encode("utf-8")
        return 200, body

    def sent_texts(self, api_method: str = "sendMessage") -> List[str]:
        return [p.get("text", "") for name, p in self.calls if name == api_method]

    def edited_texts(self) -> List[str]:
        return [p.get("text", "") for name, p in self.calls if name == "editMessageText"]

    def methods(self) -> List[str]:
        return [name for name, _ in self.calls]


def make_bot(request: Optional[FakeRequest] = None) -> Tuple[Bot, FakeRequest]:
    req = request or FakeRequest()
    bot = Bot(token="123456:TEST-FAKE-TOKEN", request=req, get_updates_request=req)
    return bot, req


def text_update(text: str, *, chat_id: int = 42, user_id: int = 111,
                username: str = "tester", message_id: int = 1,
                chat_type: str = "private", reply_to_bot: bool = False) -> Update:
    data: Dict[str, Any] = {
        "update_id": message_id,
        "message": {
            "message_id": message_id,
            "date": int(time.time()),
            "text": text,
            "chat": {"id": chat_id, "type": chat_type, "first_name": "Tester"},
            "from": {"id": user_id, "is_bot": False, "first_name": "Tester",
                     "username": username, "language_code": "ar"},
        },
    }
    if reply_to_bot:
        data["message"]["reply_to_message"] = {
            "message_id": message_id - 1, "date": int(time.time()),
            "text": "رد سابق من البوت",
            "chat": {"id": chat_id, "type": chat_type},
            "from": {"id": 777, "is_bot": True, "first_name": "CF Agent",
                     "username": "cf_agent_test_bot"},
        }
    return Update.de_json(data, None)


def photo_update(caption: str = "", *, chat_id: int = 42, user_id: int = 111) -> Update:
    data = {
        "update_id": 900,
        "message": {
            "message_id": 900,
            "date": int(time.time()),
            "caption": caption,
            "chat": {"id": chat_id, "type": "private"},
            "from": {"id": user_id, "is_bot": False, "first_name": "Tester"},
            "photo": [
                {"file_id": "f_small", "file_unique_id": "u1", "width": 90, "height": 90,
                 "file_size": 1000},
                {"file_id": "f_big", "file_unique_id": "u2", "width": 1200, "height": 800,
                 "file_size": 120000},
            ],
        },
    }
    return Update.de_json(data, None)


def callback_update(data: str, *, chat_id: int = 42, user_id: int = 111,
                    message_text: str = "لوحة") -> Update:
    payload = {
        "update_id": 901,
        "callback_query": {
            "id": "cq1",
            "from": {"id": user_id, "is_bot": False, "first_name": "Tester"},
            "chat_instance": "ci",
            "data": data,
            "message": {
                "message_id": 500, "date": int(time.time()), "text": message_text,
                "chat": {"id": chat_id, "type": "private"},
                "from": {"id": 777, "is_bot": True, "first_name": "CF Agent"},
            },
        },
    }
    return Update.de_json(payload, None)
