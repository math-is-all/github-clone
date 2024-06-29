import os
import subprocess
import json
import urllib3
import argparse

def get_github_repos(user, repo_type):
    http = urllib3.PoolManager()
    if repo_type == "starred":
        url = f"https://api.github.com/users/{user}/starred"
    else:
        url = f"https://api.github.com/users/{user}/repos"
    response = http.request('GET', url)
    
    if response.status != 200:
        raise Exception(f"Error fetching repositories for user {user}: {response.status}")
    
    repos = json.loads(response.data.decode('utf-8'))
    
    if repo_type == "all":
        return [repo['clone_url'] for repo in repos]
    elif repo_type == "starred":
        return [repo['clone_url'] for repo in repos]
    elif repo_type == "forked":
        return [repo['clone_url'] for repo in repos if repo['fork']]
    elif repo_type == "original":
        return [repo['clone_url'] for repo in repos if not repo['fork']]

def clone_repo(clone_url, clone_dir):
    if not os.path.exists(clone_dir):
        os.makedirs(clone_dir)
    subprocess.run(["git", "clone", clone_url], cwd=clone_dir)

def main():
    parser = argparse.ArgumentParser(description="Clone repositories of a GitHub user.")
    parser.add_argument('-u', '--username', help='GitHub username')
    parser.add_argument('-o', '--output', help='Directory to clone the repositories into')
    parser.add_argument('-t', '--type', choices=['all', 'starred', 'forked', 'original'], help='Type of repositories to clone (all, starred, forked, original)')

    args = parser.parse_args()

    github_user = args.username
    clone_directory = args.output
    repo_type = args.type

    if not github_user:
        github_user = input("请输入GitHub用户名: ")
    
    if not clone_directory:
        clone_directory = input("请输入克隆到本地的目录: ")

    if not repo_type:
        repo_type = input("请选择要克隆的仓库类型 (all, starred, forked, original): ")

    print(f"正在获取用户 {github_user} 的 {repo_type} 仓库...")
    repos = get_github_repos(github_user, repo_type)
    
    print(f"找到 {len(repos)} 个仓库.")
    
    for repo in repos:
        print(f"正在克隆仓库: {repo}")
        clone_repo(repo, clone_directory)
    
    print("所有仓库已克隆完成.")

if __name__ == "__main__":
    main()
