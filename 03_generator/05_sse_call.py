# 05_sse_call.py

from __future__ import annotations

import json
import os
from typing import Generator

import requests

API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:streamGenerateContent?alt=sse"
)

# 교육 실습용: 환경변수 GOOGLE_API_KEY가 없을 때 기본 키 사용
DEFAULT_API_KEY = "AIzaSyD-fpjUiFHKuUwYAG-9DB7sUw9UlDshqPU"


def gemini_sse_text_stream(prompt: str) -> Generator[str, None, None]:
    api_key = os.getenv("GOOGLE_API_KEY", DEFAULT_API_KEY)
    if not api_key:
        raise RuntimeError("API 키가 비어 있습니다.")

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}],
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key,
    }

    with requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=60) as response:
        response.raise_for_status() # 서버 오류시 안전장치

        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue

            line = raw_line.strip()
            if not line.startswith("data:"):
                continue

            data = line.removeprefix("data:").strip()
            if data == "[DONE]":
                break

            try:
                event = json.loads(data)
                text = event["candidates"][0]["content"]["parts"][0].get("text", "")
                if text:
                    yield text
            except (KeyError, IndexError, json.JSONDecodeError):
                continue


def sse_demo() -> None:
    prompt = "이터레이터와 제너레이터 차이를 3줄로 설명해줘."

    print("[Gemini SSE 실습]")
    print("프롬프트:", prompt)
    print("응답:")

    for chunk in gemini_sse_text_stream(prompt):
        print(chunk, end="", flush=True)

    print("\n\n(스트리밍 종료)")


if __name__ == "__main__":
    try:
        sse_demo()
    except requests.HTTPError as exc:
        print(f"\nHTTP 오류: {exc}")
        print("API 키/권한/청구 설정을 확인하세요.")
    except Exception as exc:
        print(f"\n실행 오류: {exc}")
