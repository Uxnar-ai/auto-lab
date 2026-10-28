# auto-lab dashboard

> An index of every small project running on a self-hosted box — live liveness probes plus host metrics.

English | [中文](README.md)

## What it is

Small projects get written on the server overnight and listed here. The page reads a single `projects.json`, probes each port with a TCP connect to see whether it is still alive, and reads `/proc` plus `statvfs` for uptime, load, memory and disk. No database; editing the manifest needs no restart thanks to a 20-second cache.

## Features

- One manifest (`projects.json`) is the only source of truth
- TCP liveness probe with a 0.9s timeout, results cached for 20s
- Frontend polls `/api/state` every 25s; status dots flip green/red/grey
- Host metrics read straight from `/proc` and `statvfs` — Flask is the only dependency
- Ports stay server-side; the API never exposes them
- Dark single page, no build step, edit the template and reload

## Stack

Python 3.12 · Flask 3.1

## Run

```bash
pip install -r requirements.txt
python app.py
```

## About

Part of the **auto-lab** series — small projects written, deployed and maintained automatically by [Nix](https://github.com/Uxnar-ai) on a self-hosted server.

Placeholders such as `<SERVER_IP>` and `<LOCAL_PATH>` are sanitised values applied at publish time. This repository contains no credentials, internal addresses or personal data.

## License

MIT
