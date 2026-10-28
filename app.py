#!/usr/bin/env python3
"""auto-lab 实验台：索引 <HOST> 上每天做的小项目，并实时探测存活。"""
import json
import os
import socket
import threading
import time
from datetime import date, datetime

from flask import Flask, jsonify, render_template

BASE = os.path.dirname(os.path.abspath(__file__))
PROJECTS_FILE = os.path.join(BASE, "projects.json")
CACHE_TTL = 20
PORT = int(os.environ.get("LAB_PORT", "8810"))

app = Flask(__name__)
_lock = threading.Lock()
_cache = {"ts": 0.0, "data": None}


def load_manifest():
    try:
        with open(PROJECTS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"started": str(date.today()), "projects": []}


def probe(host, port, timeout=0.9):
    """TCP 连通性探测。返回 True / False / None（未配置端口）。"""
    if not port:
        return None
    try:
        with socket.create_connection((host or "127.0.0.1", int(port)), timeout=timeout):
            return True
    except OSError:
        return False


def read_metrics():
    m = {}
    try:
        m["load"] = [round(x, 2) for x in os.getloadavg()]
    except OSError:
        m["load"] = []
    try:
        up = int(float(open("/proc/uptime").read().split()[0]))
        d, rem = divmod(up, 86400)
        h, rem = divmod(rem, 3600)
        m["uptime"] = f"{d}天{h}时{rem // 60}分"
    except Exception:
        m["uptime"] = "—"
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":", 1)
                info[k] = int(v.strip().split()[0])
        total = info["MemTotal"]
        avail = info.get("MemAvailable", info.get("MemFree", 0))
        used = total - avail
        m["mem"] = {"used": used // 1024, "total": total // 1024,
                    "pct": round(used * 100.0 / total, 1)}
    except Exception:
        m["mem"] = None
    try:
        st = os.statvfs("/")
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        total = st.f_blocks * st.f_frsize
        m["disk"] = {"used": round(used / 2 ** 30, 1),
                     "total": round(total / 2 ** 30, 1),
                     "pct": round(used * 100.0 / total, 1)}
    except Exception:
        m["disk"] = None
    return m


def build_state():
    now = time.time()
    with _lock:
        if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
            return _cache["data"]

    man = load_manifest()
    started = man.get("started") or str(date.today())
    try:
        day_no = (date.today() - date.fromisoformat(started)).days + 1
    except ValueError:
        day_no = 1

    projects = []
    for p in man.get("projects", []):
        alive = probe(p.get("probe_host", "127.0.0.1"), p.get("port"))
        # 端口只用于探测，不下发给前端 —— 页面对外只说明「活着 / 没活着」
        item = {k: v for k, v in p.items() if k not in ("port", "probe_host")}
        item["alive"] = alive
        projects.append(item)
    projects.sort(key=lambda x: (x.get("created", ""), x.get("id", "")), reverse=True)

    data = {
        "projects": projects,
        "count": len(projects),
        "alive": sum(1 for x in projects if x["alive"] is True),
        "metrics": read_metrics(),
        "day_no": day_no,
        "started": started,
        "ts": int(now),
        "checked": datetime.now().strftime("%m-%d %H:%M:%S"),
    }
    with _lock:
        _cache["ts"] = now
        _cache["data"] = data
    return data


@app.route("/")
def index():
    return render_template("index.html", st=build_state())


@app.route("/api/state")
def api_state():
    return jsonify(build_state())


@app.route("/healthz")
def healthz():
    return {"ok": True}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, threaded=True)
