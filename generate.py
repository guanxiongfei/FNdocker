# -*- coding: utf-8 -*-
"""飞牛 FnOS 高频 Docker 应用部署生成器。
生成:
  1) compose/<key>.yml  —— 20 个独立 compose 文件
  2) index.html         —— 可交互生成器（筛选 + 自定义主机IP/端口/路径）
  3) README.md          —— 应用清单
"""
import json
import os
import datetime

OUT = os.path.dirname(os.path.abspath(__file__))
COMPOSE_DIR = os.path.join(OUT, "compose")
os.makedirs(COMPOSE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 应用数据模型
# 每个 app: key, name, desc, tag, services[]
# service: name, image, title, ports[{container,proto,web}],
#          volumes[{container,suffix}], envs[{name,value}],
#          privileged, restart, command
# ---------------------------------------------------------------------------
APPS = [
    {
        "key": "qbittorrent", "name": "qBittorrent", "tag": "下载",
        "desc": "开源 BT/PT 下载客户端，Web 管理界面。",
        "services": [{
            "name": "qbittorrent", "image": "linuxserver/qbittorrent:latest",
            "title": "主服务",
            "ports": [{"container": "6881", "proto": "tcp", "web": False},
                      {"container": "6881", "proto": "udp", "web": False},
                      {"container": "8080", "proto": "tcp", "web": True}],
            "volumes": [{"container": "/config", "suffix": "qbittorrent/config"},
                        {"container": "/downloads", "suffix": "qbittorrent/downloads"}],
            "envs": [{"name": "PUID", "value": "1000"},
                     {"name": "PGID", "value": "100"},
                     {"name": "TZ", "value": "Asia/Shanghai"},
                     {"name": "WEBUI_PORT", "value": "8080"}],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "transmission", "name": "Transmission", "tag": "下载",
        "desc": "轻量级 BT 下载，资源占用低。",
        "services": [{
            "name": "transmission", "image": "linuxserver/transmission:latest",
            "title": "主服务",
            "ports": [{"container": "9091", "proto": "tcp", "web": True},
                      {"container": "51413", "proto": "tcp", "web": False},
                      {"container": "51413", "proto": "udp", "web": False}],
            "volumes": [{"container": "/config", "suffix": "transmission/config"},
                        {"container": "/downloads", "suffix": "transmission/downloads"},
                        {"container": "/watch", "suffix": "transmission/watch"}],
            "envs": [{"name": "PUID", "value": "1000"},
                     {"name": "PGID", "value": "100"},
                     {"name": "TZ", "value": "Asia/Shanghai"}],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "aria2", "name": "Aria2 Pro", "tag": "下载",
        "desc": "高速多协议下载（HTTP/FTP/BT），含 AriaNg 前端。",
        "services": [{
            "name": "aria2", "image": "p3terx/aria2-pro:latest",
            "title": "主服务",
            "ports": [{"container": "6800", "proto": "tcp", "web": False},
                      {"container": "6888", "proto": "tcp", "web": True}],
            "volumes": [{"container": "/config", "suffix": "aria2/config"},
                        {"container": "/downloads", "suffix": "aria2/downloads"}],
            "envs": [{"name": "RPC_SECRET", "value": "your_rpc_secret"},
                     {"name": "PUID", "value": "1000"},
                     {"name": "PGID", "value": "100"},
                     {"name": "TZ", "value": "Asia/Shanghai"}],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "jellyfin", "name": "Jellyfin", "tag": "影音",
        "desc": "开源媒体中心，支持转码与多端播放。",
        "services": [{
            "name": "jellyfin", "image": "jellyfin/jellyfin:latest",
            "title": "主服务",
            "ports": [{"container": "8096", "proto": "tcp", "web": True},
                      {"container": "8920", "proto": "tcp", "web": False}],
            "volumes": [{"container": "/config", "suffix": "jellyfin/config"},
                        {"container": "/cache", "suffix": "jellyfin/cache"},
                        {"container": "/media", "suffix": "media"}],
            "envs": [{"name": "TZ", "value": "Asia/Shanghai"}],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "emby", "name": "Emby", "tag": "影音",
        "desc": "媒体服务器，界面友好，部分高级功能需 Premium。",
        "services": [{
            "name": "emby", "image": "emby/embyserver:latest",
            "title": "主服务",
            "ports": [{"container": "8096", "proto": "tcp", "web": True},
                      {"container": "8920", "proto": "tcp", "web": False}],
            "volumes": [{"container": "/config", "suffix": "emby/config"},
                        {"container": "/cache", "suffix": "emby/cache"},
                        {"container": "/media", "suffix": "media"}],
            "envs": [{"name": "UID", "value": "0"},
                     {"name": "GID", "value": "0"},
                     {"name": "GIDLIST", "value": "0"},
                     {"name": "TZ", "value": "Asia/Shanghai"}],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "plex", "name": "Plex", "tag": "影音",
        "desc": "老牌媒体服务器，客户端生态完善。",
        "services": [{
            "name": "plex", "image": "plexinc/pms-docker:latest",
            "title": "主服务",
            "ports": [{"container": "32400", "proto": "tcp", "web": True}],
            "volumes": [{"container": "/config", "suffix": "plex/config"},
                        {"container": "/transcode", "suffix": "plex/transcode"},
                        {"container": "/media", "suffix": "media"}],
            "envs": [{"name": "TZ", "value": "Asia/Shanghai"},
                     {"name": "PLEX_CLAIM", "value": "claim-your-claim-token"},
                     {"name": "PUID", "value": "1000"},
                     {"name": "PGID", "value": "100"}],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "navidrome", "name": "Navidrome", "tag": "影音",
        "desc": "轻量音乐流媒体服务器，支持 Subsonic 协议。",
        "services": [{
            "name": "navidrome", "image": "deluan/navidrome:latest",
            "title": "主服务",
            "ports": [{"container": "4533", "proto": "tcp", "web": True}],
            "volumes": [{"container": "/data", "suffix": "navidrome/data"},
                        {"container": "/music", "suffix": "music"}],
            "envs": [{"name": "ND_MUSICFOLDER", "value": "/music"},
                     {"name": "ND_DATAFOLDER", "value": "/data"},
                     {"name": "TZ", "value": "Asia/Shanghai"}],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "alist", "name": "Alist", "tag": "网盘",
        "desc": "多网盘聚合挂载（阿里/天翼/OneDrive 等），统一 Web 访问。",
        "services": [{
            "name": "alist", "image": "xhofe/alist:latest",
            "title": "主服务",
            "ports": [{"container": "5244", "proto": "tcp", "web": True}],
            "volumes": [{"container": "/opt/alist/data", "suffix": "alist/data"}],
            "envs": [{"name": "PUID", "value": "1000"},
                     {"name": "PGID", "value": "100"},
                     {"name": "TZ", "value": "Asia/Shanghai"}],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "homeassistant", "name": "Home Assistant", "tag": "智能家居",
        "desc": "开源智能家居中枢，支持海量设备接入与自动化。",
        "services": [{
            "name": "homeassistant", "image": "ghcr.io/home-assistant/home-assistant:stable",
            "title": "主服务",
            "ports": [{"container": "8123", "proto": "tcp", "web": True}],
            "volumes": [{"container": "/config", "suffix": "homeassistant/config"}],
            "envs": [{"name": "TZ", "value": "Asia/Shanghai"}],
            "privileged": True, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "vaultwarden", "name": "Vaultwarden", "tag": "密码管理",
        "desc": "Bitwarden 轻量自托管服务端（Rust 实现）。",
        "services": [{
            "name": "vaultwarden", "image": "vaultwarden/server:latest",
            "title": "主服务",
            "ports": [{"container": "80", "proto": "tcp", "web": True}],
            "volumes": [{"container": "/data", "suffix": "vaultwarden/data"}],
            "envs": [{"name": "TZ", "value": "Asia/Shanghai"},
                     {"name": "WEBSOCKET_ENABLED", "value": "true"}],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "nextcloud", "name": "Nextcloud", "tag": "网盘",
        "desc": "私有云盘与协作套件，替代公有网盘。",
        "services": [{
            "name": "nextcloud", "image": "nextcloud:latest",
            "title": "主服务",
            "ports": [{"container": "80", "proto": "tcp", "web": True}],
            "volumes": [{"container": "/var/www/html", "suffix": "nextcloud/html"}],
            "envs": [{"name": "TZ", "value": "Asia/Shanghai"}],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "immich", "name": "Immich", "tag": "照片",
        "desc": "自托管照片/视频备份与 AI 管理（Google Photos 平替）。",
        "services": [
            {"name": "server", "image": "ghcr.io/immich-app/server:release",
             "title": "服务端",
             "ports": [{"container": "2283", "proto": "tcp", "web": True}],
             "volumes": [{"container": "/usr/src/app/upload", "suffix": "immich/upload"}],
             "envs": [{"name": "TZ", "value": "Asia/Shanghai"},
                      {"name": "DB_HOSTNAME", "value": "immich_db"},
                      {"name": "DB_USERNAME", "value": "immich"},
                      {"name": "DB_PASSWORD", "value": "postgres"},
                      {"name": "DB_DATABASE_NAME", "value": "immich"},
                      {"name": "REDIS_HOSTNAME", "value": "immich_redis"}],
             "privileged": False, "restart": "unless-stopped", "command": ""},
            {"name": "db", "image": "tensorchord/pgvecto-rs:pg14-v0.2.0",
             "title": "数据库",
             "ports": [],
             "volumes": [{"container": "/var/lib/postgresql/data", "suffix": "immich/pgdata"}],
             "envs": [{"name": "POSTGRES_PASSWORD", "value": "postgres"},
                      {"name": "POSTGRES_USER", "value": "immich"},
                      {"name": "POSTGRES_DB", "value": "immich"}],
             "privileged": False, "restart": "unless-stopped", "command": ""},
            {"name": "redis", "image": "redis:6.2-alpine",
             "title": "缓存",
             "ports": [],
             "volumes": [{"container": "/data", "suffix": "immich/redis"}],
             "envs": [],
             "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "photoprism", "name": "PhotoPrism", "tag": "照片",
        "desc": "AI 照片管理，自动分类与地图定位。",
        "services": [{
            "name": "photoprism", "image": "photoprism/photoprism:latest",
            "title": "主服务",
            "ports": [{"container": "2342", "proto": "tcp", "web": True}],
            "volumes": [{"container": "/photoprism/storage", "suffix": "photoprism/storage"},
                        {"container": "/photoprism/originals", "suffix": "photos"}],
            "envs": [{"name": "TZ", "value": "Asia/Shanghai"},
                     {"name": "PHOTOPRISM_UPLOAD_NSFW", "value": "true"},
                     {"name": "PHOTOPRISM_ADMIN_PASSWORD", "value": "please_change"}],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "portainer", "name": "Portainer", "tag": "运维",
        "desc": "Docker 可视化管理面板。",
        "services": [{
            "name": "portainer", "image": "portainer/portainer-ce:latest",
            "title": "主服务",
            "ports": [{"container": "9000", "proto": "tcp", "web": True},
                      {"container": "9443", "proto": "tcp", "web": False}],
            "volumes": [{"container": "/data", "suffix": "portainer/data"},
                        {"container": "/var/run/docker.sock", "suffix": "docker.sock", "isSocket": True}],
            "envs": [],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "nginxproxymanager", "name": "Nginx Proxy Manager", "tag": "运维",
        "desc": "可视化反向代理与 SSL 证书管理。",
        "services": [{
            "name": "npm", "image": "jc21/nginx-proxy-manager:latest",
            "title": "主服务",
            "ports": [{"container": "80", "proto": "tcp", "web": False},
                      {"container": "81", "proto": "tcp", "web": True},
                      {"container": "443", "proto": "tcp", "web": False}],
            "volumes": [{"container": "/data", "suffix": "npm/data"},
                        {"container": "/etc/letsencrypt", "suffix": "npm/letsencrypt"}],
            "envs": [],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "adguardhome", "name": "AdGuard Home", "tag": "网络",
        "desc": "自建 DNS 去广告与家庭网络过滤。",
        "services": [{
            "name": "adguardhome", "image": "adguard/adguardhome:latest",
            "title": "主服务",
            "ports": [{"container": "53", "proto": "tcp", "web": False},
                      {"container": "53", "proto": "udp", "web": False},
                      {"container": "3000", "proto": "tcp", "web": True},
                      {"container": "853", "proto": "tcp", "web": False}],
            "volumes": [{"container": "/opt/adguardhome/conf", "suffix": "adguard/conf"},
                        {"container": "/opt/adguardhome/work", "suffix": "adguard/work"}],
            "envs": [],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "heimdall", "name": "Heimdall", "tag": "导航",
        "desc": "自托管应用导航页，聚合常用服务入口。",
        "services": [{
            "name": "heimdall", "image": "linuxserver/heimdall:latest",
            "title": "主服务",
            "ports": [{"container": "7990", "proto": "tcp", "web": True}],
            "volumes": [{"container": "/config", "suffix": "heimdall/config"}],
            "envs": [{"name": "PUID", "value": "1000"},
                     {"name": "PGID", "value": "100"},
                     {"name": "TZ", "value": "Asia/Shanghai"}],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "uptimekuma", "name": "Uptime Kuma", "tag": "监控",
        "desc": "自托管监控与告警（优雅状态页）。",
        "services": [{
            "name": "uptimekuma", "image": "louislam/uptime-kuma:latest",
            "title": "主服务",
            "ports": [{"container": "3001", "proto": "tcp", "web": True}],
            "volumes": [{"container": "/app/data", "suffix": "uptimekuma/data"}],
            "envs": [],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "memos", "name": "Memos", "tag": "笔记",
        "desc": "轻量开源笔记/碎片化记录，支持 Markdown。",
        "services": [{
            "name": "memos", "image": "neosmemo/memos:latest",
            "title": "主服务",
            "ports": [{"container": "5230", "proto": "tcp", "web": True}],
            "volumes": [{"container": "/var/opt/memos", "suffix": "memos/data"}],
            "envs": [],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
    {
        "key": "filebrowser", "name": "File Browser", "tag": "文件",
        "desc": "Web 文件管理器，可浏览/上传/编辑服务器文件。",
        "services": [{
            "name": "filebrowser", "image": "filebrowser/filebrowser:latest",
            "title": "主服务",
            "ports": [{"container": "80", "proto": "tcp", "web": True}],
            "volumes": [{"container": "/srv", "suffix": "filebrowser/srv"},
                        {"container": "/database.db", "suffix": "filebrowser/database.db", "isFile": True},
                        {"container": "/filebrowser.json", "suffix": "filebrowser/filebrowser.json", "isFile": True}],
            "envs": [],
            "privileged": False, "restart": "unless-stopped", "command": ""}]},
]


# ---------------------------------------------------------------------------
# compose 文本生成
# ---------------------------------------------------------------------------
def svc_to_compose(app, svc, host_ip, base_dir, bind_ip, container_name):
    lines = []
    indent = "  "
    lines.append(f'{indent}{svc["name"] if len(app["services"]) > 1 else app["key"]}:')
    lines.append(f'{indent}  image: {svc["image"]}')
    if svc.get("privileged"):
        lines.append(f'{indent}  privileged: true')
    if svc.get("restart"):
        lines.append(f'{indent}  restart: {svc["restart"]}')
    if svc.get("command"):
        lines.append(f'{indent}  command: {svc["command"]}')
    if svc.get("ports"):
        lines.append(f'{indent}  ports:')
        for p in svc["ports"]:
            if bind_ip:
                lines.append(f'{indent}    - "{host_ip}:{p["container"]}:{p["container"]}/{p["proto"]}"')
            else:
                lines.append(f'{indent}    - "{p["container"]}:{p["container"]}/{p["proto"]}"')
    if svc.get("volumes"):
        lines.append(f'{indent}  volumes:')
        for v in svc["volumes"]:
            host = f'{base_dir}/{v["suffix"]}'
            lines.append(f'{indent}    - "{host}:{v["container"]}"')
    if svc.get("envs"):
        lines.append(f'{indent}  environment:')
        for e in svc["envs"]:
            val = e["value"]
            lines.append(f'{indent}    - "{e["name"]}={val}"')
    return "\n".join(lines)


def find_web_port(app):
    for svc in app["services"]:
        for p in svc["ports"]:
            if p.get("web"):
                return p["container"]
    return "—"


def app_to_compose(app, host_ip, base_dir, bind_ip):
    cname = app["key"]
    wp = find_web_port(app)
    header = [
        f'# ============================================',
        f'# {app["name"]} — {app["tag"]}',
        f'# {app["desc"]}',
        f'# 访问地址: http://{host_ip}:{wp}',
        f'# ============================================',
        'services:',
    ]
    body = []
    for svc in app["services"]:
        svc_name = svc["name"] if len(app["services"]) > 1 else app["key"]
        body.append(svc_to_compose(app, svc, host_ip, base_dir, bind_ip, svc_name))
    return "\n".join(header + body) + "\n"


# ---------------------------------------------------------------------------
# 生成 20 个独立 compose 文件
# ---------------------------------------------------------------------------
for app in APPS:
    text = app_to_compose(app, "192.168.1.100", "/vol1/1000/docker", False)
    path = os.path.join(COMPOSE_DIR, f'{app["key"]}.yml')
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
print(f"已生成 {len(APPS)} 个 compose 文件 -> {COMPOSE_DIR}")

# 生成 README 清单
# 说明：README.md 为手工维护的图文说明，仅当仓库缺失时才生成默认清单，
# 避免覆盖用户在 GitHub 上展示的图文版 README。
readme_path = os.path.join(OUT, "README.md")
if not os.path.exists(readme_path):
    readme = ["# 飞牛 FnOS 高频 Docker 应用部署清单", "",
              "> 由生成器自动产出。每个应用一个 compose 文件，位于 `compose/` 目录。",
              "> 主机 IP 默认 192.168.1.100，数据根目录默认 /vol1/1000/docker，可按需修改。", "",
              "## 应用列表（20）", ""]
    readme.append("| # | 应用 | 类别 | 默认 Web 端口 | compose 文件 |")
    readme.append("|---|------|------|-------------|--------------|")
    for i, app in enumerate(APPS, 1):
        web = "—"
        for svc in app["services"]:
            for p in svc["ports"]:
                if p.get("web"):
                    web = p["container"]
                    break
            if web != "—":
                break
        readme.append(f'| {i} | {app["name"]} | {app["tag"]} | {web} | `compose/{app["key"]}.yml` |')
    readme.append("")
    readme.append("## 使用方式")
    readme.append("```bash")
    readme.append("cd compose")
    readme.append("docker compose -f qbittorrent.yml up -d")
    readme.append("```")
    readme.append("")
    readme.append("或使用交互式生成器 `index.html`：勾选应用、自定义主机 IP / 端口 / 映射路径，一键复制 compose 与 docker run。")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(readme))
    print("已生成 README.md（默认清单）")
else:
    print("README.md 已存在，跳过覆盖（手工维护的图文版）。")

# ---------------------------------------------------------------------------
# 生成 index.html
# ---------------------------------------------------------------------------
# HTML 模板已移至 template.html，由下方读取并注入数据。


# ---------------------------------------------------------------------------
# 应用分组 + 默认分组（四类：影音娱乐 / 文件管理 / 生产工具 / 其他）
# ---------------------------------------------------------------------------
GROUP_MAP = {
    "qbittorrent": "media", "transmission": "media", "aria2": "media",
    "jellyfin": "media", "emby": "media", "plex": "media", "navidrome": "media",
    "immich": "media", "photoprism": "media",
    "alist": "file", "nextcloud": "file", "filebrowser": "file",
    "homeassistant": "prod", "vaultwarden": "prod", "memos": "prod",
    "uptimekuma": "prod", "portainer": "prod", "nginxproxymanager": "prod",
    "adguardhome": "prod",
    "heimdall": "other",
}
for a in APPS:
    a["group"] = GROUP_MAP.get(a["key"], "other")

DEFAULT_GROUPS = [
    {"id": "media", "name": "影音娱乐"},
    {"id": "file", "name": "文件管理"},
    {"id": "prod", "name": "生产工具"},
    {"id": "other", "name": "其他"},
]

# ---------------------------------------------------------------------------
# 生成 index.html（读取 template.html，注入应用数据与分组）
# ---------------------------------------------------------------------------
TEMPLATE_PATH = os.path.join(OUT, "template.html")
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = f.read()
html = (template
        .replace("__DATA__", json.dumps(APPS, ensure_ascii=False))
        .replace("__GROUPS__", json.dumps(DEFAULT_GROUPS, ensure_ascii=False)))
with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("已生成 index.html")
print("完成。")
