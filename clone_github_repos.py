import urllib
import urllib.request as urllib2
import re
import threading
import queue
import os
import zipfile
import time
from optparse import OptionParser

headers = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'identity',
}

def get_page(url_list):
    q = queue.Queue()

    def get_p(url):
        try:
            headers['Host'] = 'github.com'
            request = urllib2.Request(url, headers=headers)
            response = urllib2.urlopen(request)
            time.sleep(1)
            q.put(str(response.read()))
        except urllib.error.HTTPError as e:
            print(f"HTTPError: {e.code} for URL: {url}")
            q.put('')

    threads = []

    for i in url_list:
        t = threading.Thread(target=get_p, args=(i,))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    page_list = []

    while not q.empty():
        page_list.append(q.get())

    return page_list

def get_url(home_url, page_num, tab_num):
    tab = ['stars', 'repositories']
    return home_url + '?page={}&tab={}'.format(page_num, tab[tab_num])

def get_repo(home_url, tab_num):
    max_num = 1
    pages = get_page([get_url(home_url, 1, tab_num)])
    
    if pages and pages[0]:
        first_start_page = pages[0]
        pattern = [r'.*>(\d+)<.*"next_page".*?',
                   r'.*>(\d+)<.*next_page.*']
        ma = re.search(pattern[tab_num], first_start_page)

        if ma is not None:
            max_num = int(ma.group(1))
    else:
        print(f"Failed to retrieve first page for {home_url}")
        return []

    url_list = []
    for i in range(1, max_num + 1):
        url_list.append(get_url(home_url, i, tab_num))

    pattern = [
        r'd-inline-block mb-1.*?href="(.*?)"', r'<h3>.*?href="(.*?)".*?codeRepository']
    project_list = []
    for i in get_page(url_list):
        if i:
            project_list += re.findall(pattern[tab_num], i)
    return project_list

def download(project_list, directory):
    threads = []
    if not os.path.exists(directory):
        os.mkdir(directory)

    for i in project_list:
        print(f'downloading {i} to {directory}/')
        t = threading.Thread(target=git_clone, args=(i, directory))
        threads.append(t)

    print("downloading, please don't stop it")

    for t in threads:
        time.sleep(2)
        t.start()

def git_clone(name, path, branch_name='master'):
    try:
        username, projectname = re.match(r'/(.*?)/(.*)', name).groups()
        url = f'https://codeload.github.com/{username}/{projectname}/zip/{branch_name}'
        filename = os.path.join(path, projectname)
        zipfile_name = f'{filename}.zip'
        print(url)
        data = urllib2.urlopen(url)
        
        with open(zipfile_name, 'wb') as f:
            f.write(data.read())

        with zipfile.ZipFile(zipfile_name, 'r') as f:
            f.extractall(path + '.')

        os.rename(f'{filename}-master', filename)
        os.remove(zipfile_name)
    except Exception as e:
        print(f"Error downloading {name}: {e}")

def main():
    parse = OptionParser()
    parse.add_option('-u', '--username', dest='user_name', help="destination's github username or link")
    parse.add_option('-t', '--tab', dest='tab', help="download stars(s) or repositories(r) or all(a). default: repositories")
    parse.add_option('-o', '--output', action='store', dest='directory', help="output directory. default: ./Github")

    (option, _) = parse.parse_args()

    if option.user_name is None:
        print('please input username')
        os._exit(1)

    user_name = option.user_name.strip('/')
    tab_num = 1
    director = os.path.join(os.getcwd(), 'GitHub').replace('\\', '/')
    repo_list = []

    if option.tab:
        tab = option.tab[0].lower()
        if tab == 's':
            tab_num = 0
        elif tab == 'r':
            tab_num = 1
        elif tab == 'a':
            tab_num = 2

    home_url = f'https://github.com/orgs/{user_name}/'
    if tab_num == 2:
        repo_list += get_repo(home_url, 1)
        repo_list += get_repo(home_url, 0)
    else:
        repo_list = get_repo(home_url, tab_num)

    if option.directory:
        director = option.directory

    download(repo_list, director)

if __name__ == '__main__':
    main()
