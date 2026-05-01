# 1. 重新构建
#docker image rm claude-dev
docker build \
  --build-arg DEV_UID=$(id -u) \
  --build-arg DEV_GID=$(id -g) \
  -t claude-dev .

# 2. 停止并删除旧容器
docker stop divident_screening || true
docker rm divident_screening || true

# 3. 启动（注意挂载路径）
docker run -dit \
  --name divident_screening \
  --user dev \
  --gpus all \
  -e DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
  -e MINIMAX_API_KEY="$MINIMAX_API_KEY" \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  -v "$(pwd):/workspace" \
  claude-dev

docker cp ./claude_config_backup/. divident_screening:/home/dev/
docker exec divident_screening ls -la /home/dev/ /workspace
docker exec divident_screening printenv DEEPSEEK_API_KEY
docker exec divident_screening printenv MINIMAX_API_KEY
docker exec divident_screening printenv GEMINI_API_KEY
docker exec divident_screening sed -i "s/{{MINIMAX_API_KEY}}/$MINIMAX_API_KEY/g" /home/dev/.claude/settings.json
docker exec divident_screening cat /home/dev/.claude/settings.json
docker exec divident_screening bash -c "pip install -r /workspace/requirements.txt"
# export LOCAL_DEV_UID=$(id -u)
# export LOCAL_GID=$(id -g)
# docker compose down
# docker compose --build
# docker compose up -d
