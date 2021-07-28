#!/usr/bin/env python3
# encoding:utf-8

import requests
from bs4 import BeautifulSoup
import json
import re
from concurrent.futures import as_completed, ThreadPoolExecutor
import logging
import datetime
import os


def get_theme_list():
    "从hexo官网上获取主题列表"
    url = 'https://hexo.io/themes/'
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'lxml')
    themes = soup.find_all('li', attrs={'class': 'plugin on'})
    __themes_list = []
    for theme in themes:
        x = {}
        x['name'] = theme.find('a', attrs={'class': 'plugin-name'}).text
        x['link'] = theme.find('a', attrs={'class': 'plugin-name'}).get('href')
        x['description'] = theme.find('p', attrs={'class': 'plugin-desc'}).text
        __themes_list.append(x)
    return __themes_list


def get_theme_info(link):
    "从链接获取github上关注信息"
    try:
        assert link.startswith('https://github.com/')
        print("downloading {}".format(link))

        a = requests.get(link,timeout=7)
        a.raise_for_status()
        soup = BeautifulSoup(a.text, 'lxml')
        tags = soup.select('.pagehead-actions')[0]
        tag_list = tags.find_all("a", attrs={'class': 'social-count'})
        # watch star fork link
        watch, star, fork = [
            int(re.sub(r"[^\d]+", '', x.text.strip())) for x in tag_list]
        return {'watch': watch, 'star': star, 'fork': fork}
    except AssertionError:
        return None
    except KeyboardInterrupt:
        exit()
    except requests.exceptions.HTTPError:
        print('{} 连接异常'.format(link))
        return None
    except requests.exceptions.ConnectionError:
        print('{} 连接异常'.format(link))
        return None
    except requests.exceptions.ReadTimeout:
        print('{} 连接超时'.format(link))
        return None
    except Exception as e:
        logging.exception(e)
        exit("没能成功访问Github链接{}".format(link))


def main():
    themes = get_theme_list()
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_info = {executor.submit(
            get_theme_info, theme['link']): theme for theme in themes}
        for future in as_completed(future_to_info):
            theme = future_to_info[future]
            try:
                if(future.result()):
                    _ = theme.copy()
                    _.update(future.result())
                    print(_)
                    results.append(_)
            except KeyboardInterrupt:
                exit()
            except Exception as e:
                logging.exception(e)

    theme_star_top_10 = sorted(
        results, key=lambda k: k['star'], reverse=True)[:10]
    theme_fork_top_10 = sorted(
        results, key=lambda k: k['fork'], reverse=True)[:10]
    theme_watch_top_10 = sorted(
        results, key=lambda k: k['watch'], reverse=True)[:10]

    def write_out(theme_list, file_name):
        with open(file_name, 'w') as f:
            f.write(json.dumps(theme_list, indent=4, ensure_ascii=False))
    paths = ["report/{}".format(x) for x in ['star', 'fork', 'watch']]
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)
    today_date = datetime.datetime.today().strftime('%Y-%m-%d')
    write_out(theme_star_top_10, "{}/{}.json".format(paths[0], today_date))
    write_out(theme_fork_top_10, "{}/{}.json".format(paths[1], today_date))
    write_out(theme_watch_top_10, "{}/{}.json".format(paths[2], today_date))


if __name__ == '__main__':
    main()
