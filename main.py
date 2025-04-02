import os
import pty
import select
import subprocess
import sys
import time

def run_aider_session(user_prompt):
    # 创建伪终端
    master, slave = pty.openpty()
    
    # 启动aider进程
    process = subprocess.Popen(
        ['aider', '--config', '.aider.config.yml'],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        preexec_fn=os.setsid
    )
    
    # 关闭子进程端的文件描述符
    os.close(slave)
    
    # 设置非阻塞模式
    os.set_blocking(master, False)
    
    buffer = ""
    prompt_sent = False
    code_mode_sent = False
    
    try:
        while process.poll() is None:
            # 等待输入或输出
            r, _, _ = select.select([master], [], [], 0.1)
            
            for fd in r:
                if fd == master:
                    try:
                        # 读取aider输出
                        output = os.read(master, 2048)
                        if output:
                            # 使用replace错误处理策略进行解码
                            text = output.decode('utf-8', errors='replace')
                            print(text, end='', flush=True)
                            buffer += text
                            
                            # 检查是否需要进入代码模式
                            if not code_mode_sent:
                                time.sleep(1)
                                os.write(master, b"/git init\n")
                                time.sleep(1)
                                os.write(master, b"/code\n")
                                code_mode_sent = True
                                time.sleep(1)
                            
                            # 检查是否需要发送用户prompt
                            if code_mode_sent and not prompt_sent:
                                os.write(master, f"{user_prompt}\n".encode())
                                prompt_sent = True
                            
                            # 检查是否需要回答问题
                            if "(Y)es" in buffer:
                                time.sleep(0.5)
                                if "pip install" in buffer or "time_series.csv" in buffer:
                                    os.write(master, b"no\n")
                                else:
                                    os.write(master, b"yes\n")
                                buffer = ""
                            
                            # 检查是否结束会话
                            if "Goodbye!" in buffer:
                                return
                            
                    except OSError:
                        continue
                        
    except KeyboardInterrupt:
        print("\n用户中断操作")
    finally:
        # 清理资源
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        os.close(master)

if __name__ == "__main__":
    # clear the content of ".aider.chat.history.md" and ".aider.input.history"
    with open(".aider.chat.history.md", "w") as f:
        f.write("")
    with open(".aider.input.history", "w") as f:
        f.write("")
    if len(sys.argv) < 2:
        print("用法: python main.py '你的prompt'")
        sys.exit(1)
    run_aider_session(sys.argv[1])