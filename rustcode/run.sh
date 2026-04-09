# 1. 重新构建
#docker image rm claude-dev
docker build \
  --build-arg DEV_UID=$(id -u) \
  --build-arg DEV_GID=$(id -g) \
  -t claude-dev .

# 2. 停止并删除旧容器
docker stop rustcode || true
docker rm rustcode || true

# 3. 启动（注意挂载路径）
docker run -dit \
  --name rustcode \
  --user dev \
  -e DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
  -e MINIMAX_API_KEY="$MINIMAX_API_KEY" \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  -v "$(pwd):/workspace" \
  claude-dev

docker cp ./claude_config_backup/. rustcode:/home/dev/
docker exec rustcode ls -la /home/dev/ /workspace
docker exec rustcode printenv DEEPSEEK_API_KEY
docker exec rustcode printenv MINIMAX_API_KEY
docker exec rustcode printenv GEMINI_API_KEY
docker exec rustcode sed -i "s/{{MINIMAX_API_KEY}}/$MINIMAX_API_KEY/g" /home/dev/.claude/settings.json
docker exec rustcode cat /home/dev/.claude/settings.json
docker exec rustcode curl --proto '=https' ==tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
# docker exec rustcode rustc --version
# docker exec rustcode cargo --version
