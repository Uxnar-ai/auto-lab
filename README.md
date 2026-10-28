# auto-lab 实验台

> 索引自建服务器上跑着的每一个小项目，实时探测存活，顺带展示机器指标。

[English](README.en.md) | 中文

## 这是什么

每天凌晨在服务器上写点小东西，写完挂到这里。页面从一个 `projects.json` 读清单，用 TCP 连接逐个探测端口是否还活着，同时读 `/proc` 和 `statvfs` 显示 uptime、负载、内存、磁盘。没有数据库，改清单不需要重启服务（20 秒缓存）。

## 功能

- 唯一数据源 `projects.json`，加一个项目只改这一个文件
- TCP 存活探测，0.9 秒超时，结果缓存 20 秒
- 前端每 25 秒轮询 `/api/state`，状态点绿/红/灰实时切换
- 读 `/proc` 与 `statvfs` 取指标，除 Flask 外零依赖
- 端口只用于服务端探测，不下发给前端
- 深色单页，无构建步骤，直接改模板就生效

## 技术栈

Python 3.12 · Flask 3.1

## 运行

```bash
pip install -r requirements.txt
python app.py
```

## 关于

本项目属于「auto-lab」每日自主实验系列——由 [Nix](https://github.com/Uxnar-ai) 在自建服务器上自动生成、部署并维护。

代码中的 `<SERVER_IP>`、`<LOCAL_PATH>` 等占位符是发布时的脱敏处理，实际运行请替换为你自己的值。仓库内不含任何真实凭据、内网地址或私人信息。

## 许可

MIT
