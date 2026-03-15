# 1. 重新构建
#docker image rm claude-dev3
docker build \
  --build-arg DEV_UID=$(id -u) \
  --build-arg DEV_GID=$(id -g) \
  -t claude-dev3 .

# 2. 停止并删除旧容器
docker stop claude-sandbox3 || true
docker rm claude-sandbox3 || true

cp -rf claude_config_backup
# 3. 启动（注意挂载路径）
docker run -dit \
  --name claude-sandbox3 \
  --user dev \
  -v "$(pwd):/workspace" \
  claude-dev3
docker cp claude_config_backup/. claude-sandbox3:/home/dev/
docker exec claude-sandbox3 ls -la /home/dev/
# export LOCAL_DEV_UID=$(id -u)
# export LOCAL_GID=$(id -g)
# docker compose down
# docker compose --build
# docker compose up -d
