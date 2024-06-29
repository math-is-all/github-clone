这是一个让Chatgpt写的python小脚本用于clone一个作者的所有公开github仓库，于整理zlib-searcher/book-searcher时需要。


使用方法：

```bash
python -m venv venv 
./venv/bin/activate
pip install urllib3
python clone_github_repos.py -u 用户名 -o 保存的位置 -t 仓库类型 #当缺省时会通过交互的方式获取参数
```

仓库类型有：all, starred, forked, original



