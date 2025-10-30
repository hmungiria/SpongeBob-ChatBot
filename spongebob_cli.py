#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpongeBob CLI Chatbot using OpenAI-compatible API at https://ai.sooners.us
- Keeps multi-turn chat history
- Loads API key and settings from ~/.soonerai.env (DO NOT commit)
- Uses model: gemma3:4b (default) and /api/chat/completions endpoint

Usage:
  pip install -r requirements.txt
  python spongebob_cli.py
  # Type :help for commands
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

DEFAULT_SYSTEM = (
    "You are SpongeBob SquarePants. Speak cheerfully with nautical puns, "
    "occasional 'barnacles!' and 'jellyfishing' references. Be upbeat, kind, "
    "and whimsical. Keep replies concise (1–5 sentences). Avoid harmful content."
)

def load_env():
    # Load ~/.soonerai.env 
    env_path = Path.home() / ".soonerai.env"
    load_dotenv(env_path)
    api_key = os.getenv("SOONERAI_API_KEY")
    base_url = (os.getenv("SOONERAI_BASE_URL", "https://ai.sooners.us") or "").rstrip("/")
    model = os.getenv("SOONERAI_MODEL", "gemma3:4b")
    return api_key, base_url, model

def make_client(api_key: str, base_url: str):
    if not api_key:
        raise RuntimeError("Missing SOONERAI_API_KEY in ~/.soonerai.env")
    if not base_url:
        raise RuntimeError("Missing SOONERAI_BASE_URL (expected 'https://ai.sooners.us')")
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    })
    return session, f"{base_url}/api/chat/completions"

def truncate_history(history, max_pairs: int):
    """Keep system + last N (user,assistant) pairs."""
    if max_pairs <= 0:
        return history[:1]  # only system
    # system is history[0]; the rest are alternating user/assistant
    body = history[1:]
    # We want last 2*max_pairs messages
    trimmed = body[-(2*max_pairs):] if len(body) > 2*max_pairs else body
    return [history[0], *trimmed]

def call_api(session: requests.Session, url: str, model: str, messages, temperature: float, timeout: int = 60):
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    resp = session.post(url, json=payload, timeout=timeout)
    if resp.status_code != 200:
        # Try to include server message for easier debugging
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"Unexpected response format: {json.dumps(data, indent=2)}") from e

def save_transcript(history, path: Path):
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for m in history:
            role = m.get("role", "?").capitalize()
            content = m.get("content", "")
            f.write(f"{role}: {content}\n\n")
    return path

def parse_args():
    ap = argparse.ArgumentParser(description="SpongeBob CLI chatbot (SoonerAI / OpenAI-compatible).")
    ap.add_argument("--max-turns", type=int, default=8, help="How many prior user/assistant pairs to keep (default: 8).")
    ap.add_argument("--temperature", type=float, default=0.6, help="Sampling temperature (default: 0.6).")
    ap.add_argument("--system", type=str, default=None, help="Override system prompt (optional).")
    ap.add_argument("--base-url", type=str, default=None, help="Override base URL (optional, default from env).")
    ap.add_argument("--model", type=str, default=None, help="Override model name (optional, default from env).")
    ap.add_argument("--timeout", type=int, default=60, help="Request timeout seconds (default: 60).")
    return ap.parse_args()

def print_banner(model, base_url):
    print("="*72)
    print("  SpongeBob CLI Chatbot  —  OpenAI-compatible Chat Completions")
    print(f"  Model: {model} | Endpoint: {base_url}/api/chat/completions")
    print("  Commands: :help  :reset  :save [path]  :quit")
    print("="*72)

def main():
    args = parse_args()
    api_key, env_base_url, env_model = load_env()
    base_url = (args.base_url or env_base_url).rstrip("/")
    model = (args.model or env_model)
    system_prompt = args.system or DEFAULT_SYSTEM

    session, url = make_client(api_key, base_url)

    history = [
        {"role": "system", "content": system_prompt}
    ]

    print_banner(model, base_url)
    try:
        while True:
            try:
                user = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye! 🧽")
                break

            if not user:
                continue

            # Commands
            if user.startswith(":"):
                parts = user.split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""
                if cmd in (":quit", ":q", ":exit"):
                    print("Bye! 🧽")
                    break
                elif cmd == ":help":
                    print("Commands:")
                    print("  :help                Show this help")
                    print("  :reset               Clear history (keep system prompt)")
                    print("  :save                Save transcript to a file (txt)")
                    print("  :quit / :q / :exit   Exit the chatbot")
                elif cmd == ":reset":
                    history = [history[0]]
                    print("History cleared (system prompt kept).")
                elif cmd == ":save":
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    default_name = f"spongebob_chat_{ts}.txt"
                    path = Path(arg) if arg else Path(default_name)
                    saved = save_transcript(history, path)
                    print(f"Saved transcript to: {saved}")
                else:
                    print(f"Unknown command: {cmd}. Type :help")
                continue

            # Normal chat turn
            history.append({"role": "user", "content": user})
            trimmed = truncate_history(history, args.max_turns)
            try:
                reply = call_api(session, url, model, trimmed, args.temperature, timeout=args.timeout)
            except Exception as e:
                print(f"SpongeBob (error): {e}")
                # Keep history coherent by adding an assistant error message
                history.append({"role": "assistant", "content": f"(Error: {e})"})
                continue

            print(f"SpongeBob: {reply}")
            history.append({"role": "assistant", "content": reply})

    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
