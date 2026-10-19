import os
import subprocess
from watchfiles import watch


def compile_cpp(file_path):
    # 过滤掉非 cpp 文件
    if not file_path.endswith(".cpp"):
        return

    print(f"\n[检测到文件变动] {file_path}")
    print("正在执行: g++-13 -std=c++23 ...")

    # 提取文件名（不含后缀）作为默认输出程序名
    base_name = os.path.splitext(file_path)[0]
    output_name = base_name if os.name != "nt" else f"{base_name}.exe"

    # 构建编译命令（你也可以按需修改输出参数，比如加上文件名）
    cmd = ["g++-13", "-std=c++23", file_path, "-o", output_name]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[编译成功] 生成目标文件: {output_name}")
        else:
            print(f"[编译失败]\n{result.stderr}")
    except Exception as e:
        print(f"[执行出错] {e}")


if __name__ == "__main__":
    print("开始监控当前目录下的 C++ 文件变动 (按 Ctrl+C 退出)...")
    # watch('.') 会递归监控当前目录下的所有文件和文件夹
    for changes in watch("."):
        for change_type, path in changes:
            compile_cpp(path)
