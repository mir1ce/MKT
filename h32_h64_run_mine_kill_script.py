# 此代码文件主要用于完成挖矿木马专杀，使用情况，请根据实际场景进行修改。
#
# 作者: 爱做梦的大米饭
# 日期: 2025-02-14
#
# 版权声明: 本代码遵循 MIT 开源协议，你可以自由使用、修改和分发，但需保留此版权声明。
# 本程序仅用于学习或研究，用于生产环境，请根据实际情况进行编写。如出现安全问题，本人概不负责。

import os
import subprocess
import sys

# ANSI 转义序列
BLUE = "\033[34m"
RESET = "\033[0m"

def get_process_info(ip_address):
    try:
        netstat_output = subprocess.check_output(['netstat', '-anoplt'], stderr=subprocess.DEVNULL).decode()
        for line in netstat_output.splitlines():
            if ip_address in line:
                parts = line.split()
                net_pid = parts[6].split('/')[0]
                net_name = parts[6].split('/')[1]
                return net_pid, net_name
    except subprocess.CalledProcessError as e:
        print(f"{BLUE}[-] 获取进程信息时出错: {e}{RESET}")
    return None, None

def get_virus_file_path(pid):
    try:
        virus_file_path = os.readlink(f"/proc/{pid}/exe")
        return virus_file_path, os.path.dirname(virus_file_path)
    except Exception as e:
        print(f"{BLUE}[-]获取病毒文件路径时出错: {e}{RESET}")
    return None, None

def terminate_process(pid):
    choice = input(f"{BLUE}[?] 确认终止进程 {pid} 吗? (y/n): {RESET}")
    if choice.lower() == 'y':
        try:
            print(f"{BLUE}[!] 正在终止进程 {pid}...{RESET}")
            subprocess.call(['kill', '-9', str(pid)])
            subprocess.call(['sleep', '2'])  
        except Exception as e:
            print(f"{BLUE}[-] 终止进程时出错: {e}{RESET}")
    else:
        print(f"{BLUE}[!] 已取消终止进程。{RESET}")

def check_crontab():
    try:
        print(f"{BLUE}[*] 检查全系统计划任务...{RESET}")
        cron_files = subprocess.check_output(['find', '/var/spool/cron', '-type', 'f'], stderr=subprocess.DEVNULL).decode().splitlines()

        for cron_file in cron_files:
            try:
                with open(cron_file, 'r') as f:
                    if '.cached/update' in f.read():
                        print(f"{BLUE}[!] 发现恶意计划任务: {cron_file}{RESET}")
            except Exception as e:
                print(f"{BLUE}[-] 读取计划任务文件 {cron_file} 时出错: {e}{RESET}")

        # 检查当前用户的 crontab
        try:
            user_crontab = subprocess.check_output(['crontab', '-l'], stderr=subprocess.DEVNULL).decode()
            if '.cached/update' in user_crontab:
                print(f"{BLUE}[!] 发现恶意计划任务，正在清理...{RESET}")
                new_crontab = '\n'.join(line for line in user_crontab.splitlines() if '.cached/update' not in line)
                subprocess.run(['crontab', '-'], input=new_crontab.encode())
        except subprocess.CalledProcessError:
            print(f"{BLUE}[-] 无法获取当前用户的 crontab，可能没有设置计划任务。{RESET}")
    except Exception as e:
        print(f"{BLUE}[-] 检查计划任务时出错: {e}{RESET}")

def delete_virus_file(virus_folder_path):
    if os.path.isdir(virus_folder_path):
        choice = input(f"{BLUE}[?] 确认删除病毒文件夹 {virus_folder_path}? (y/n): {RESET}")
        if choice.lower() == 'y':
            try:
                subprocess.call(['sudo', 'rm', '-rf', virus_folder_path])
                print(f"{BLUE}[*] 病毒文件夹已删除。{RESET}")
            except Exception as e:
                print(f"{BLUE}[-] 删除病毒文件夹时出错: {e}{RESET}")
    else:
        print(f"{BLUE}[-] 病毒文件不存在或已被移除{RESET}")

def main():
    ip_address = "172.86.83.142"
    net_pid, net_name = get_process_info(ip_address)

    if net_name and net_pid:
        print(f"{BLUE}[*] 发现可疑进程：{RESET}")
        print(f"{BLUE}[*] 进程名称: {net_name}{RESET}")
        print(f"{BLUE}[*] 进程ID: {net_pid}{RESET}")
    else:
        print(f"{BLUE}[-] 未发现与IP 172.86.83.142 相关的进程。{RESET}")
        sys.exit(1)

    virus_file_path, virus_folder_path = get_virus_file_path(net_pid)

    terminate_process(net_pid)
    check_crontab()
    delete_virus_file(virus_folder_path)

if __name__ == "__main__":
    main()
