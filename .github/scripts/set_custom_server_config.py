#!/usr/bin/env python3
"""
Set custom RustDesk server config for build.
Reads RUSTDESK_CUSTOM_SERVER env (base64+reversed export string),
decodes and writes RENDEZVOUS_SERVER, RELAY_SERVER, API_SERVER, KEY
to .cargo/config.toml [env] section.
Run from repo root. No-op if RUSTDESK_CUSTOM_SERVER is unset or empty.
"""

import os
import sys


def main() -> None:
    config_str = os.environ.get("RUSTDESK_CUSTOM_SERVER", "")
    if not config_str:
        return

    try:
        import base64
        import json
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        reversed_str = config_str[::-1]
        # 与 Flutter base64UrlEncode 兼容（URL-safe base64）
        padding = 4 - len(reversed_str) % 4
        if padding != 4:
            reversed_str += "=" * padding
        decoded_bytes = base64.urlsafe_b64decode(reversed_str)
        config = json.loads(decoded_bytes.decode("utf-8"))
    except Exception as e:
        print(f"✗ 解析配置失败: {e}", file=sys.stderr)
        sys.exit(1)

    id_server = config.get("host", "")
    relay_server = config.get("relay", "")
    api_server = config.get("api", "")
    key = config.get("key", "")

    cargo_config_path = ".cargo/config.toml"
    os.makedirs(os.path.dirname(cargo_config_path), exist_ok=True)
    with open(cargo_config_path, "a", encoding="utf-8") as f:
        f.write("\n[env]\n")
        if id_server:
            f.write(f'RENDEZVOUS_SERVER = "{id_server}"\n')
        if relay_server:
            f.write(f'RELAY_SERVER = "{relay_server}"\n')
        if api_server:
            f.write(f'API_SERVER = "{api_server}"\n')
        if key:
            f.write(f'KEY = "{key}"\n')

    print("✓ 已设置自定义服务器配置")
    print(f"  ID服务器: {id_server}")
    print(f"  中继服务器: {relay_server}")
    print(f"  API服务器: {api_server}")
    print(f"  密钥: {'已设置' if key else '未设置'}")


if __name__ == "__main__":
    main()
