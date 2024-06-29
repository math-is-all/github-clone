import os
import subprocess
import json
import urllib3

def get_github_repos(user):
    http = urllib3.PoolManager()
    url = f"https://api.github.com/users/{user}/repos"
    response = http.request('GET', url)
    
    if response.status != 200:
        raise Exception(f"Error fetching repositories for user {user}: {response.status}")
    
    repos = json.loads(response.data.decode('utf-8'))
    return [repo['clone_url'] for repo in repos]

def clone_repo(clone_url, clone_dir):
    if not os.path.exists(clone_dir):
        os.makedirs(clone_dir)
    subprocess.run(["git", "clone", clone_url], cwd=clone_dir)

def main():
    github_user = input("请输入GitHub用户名: ")
    clone_directory = input("请输入克隆到本地的目录: ")

    print(f"正在获取用户 {github_user} 的公开仓库...")
    repos = get_github_repos(github_user)
    
    print(f"找到 {len(repos)} 个仓库.")
    
    for repo in repos:
        print(f"正在克隆仓库: {repo}")
        clone_repo(repo, clone_directory)
    
    print("所有仓库已克隆完成.")

if __name__ == "__main__":
    main()
