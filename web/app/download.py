import os
import re
import sys
from urllib import request
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import date
import time
import traceback
import logging
from app import app, db
from app.models import Movie
movie_count = 1

def get_new_movie():
    base_url = 'http://www.ygdy8.net%s'
    url = 'http://www.ygdy8.net/html/gndy/dyzz/index.html'
    last_movie_id = db.session.query(Movie).order_by(Movie.id.desc()).first().movie_id
    response = requests.get(url)
    response.encoding = 'gb2312'
    html = response.text
    soup = BeautifulSoup(html, "lxml")
    result = soup.find_all('a', class_='ulink')
    result = result[::-1]
    urls = []
    for each in result:
        movie_id = int(each['href'].split('/')[-1].split('.')[0])
        if last_movie_id < movie_id:
            urls.append(base_url % each['href'])
    if not urls:
        print('no new movie.......')
    for url in urls:
        time.sleep(1)
        get_movie_info_by_url(url)
            
    

def save_break_point(page_num, movie_id):
    print('saving break point')
    f = open('breakpoint.txt', 'w')
    f.write(str(page_num))
    f.write('\n')
    f.write(str(movie_id))
    f.write('\n')
    f.close()


def recover():
    if not os.path.exists('breakpoint.txt'):
        return (-1, -1)
    f = open('breakpoint.txt', 'r')
    # print('recovering from break point')
    lines = f.readlines()
    if (len(lines) == 0):
        return (-1, -1)
    page_num = int(lines[0])
    movie_id = int(lines[1])
    print('recvoering from page %d and id %d' % (page_num, movie_id))
    f.close()
    return (page_num, movie_id)

def restart_program():
    print("restarting.....")
    python = sys.executable   
    os.execl(python, python, *sys.argv) 

def add_movie(movie):
    if db.session.query(Movie).filter(Movie.translated_title == movie.translated_title).all():
        # print(db.session.query(Movie).filter(Movie.translated_title == movie.translated_title).all())
        return 'already in database'
    try:
        db.session.add(movie)
        db.session.commit()
        return 'add to database successful'
    except Exception as e:
        s = traceback.format_exc()
        logging.error(s)
        print(e)
        return 'something go wrong'


def get_movie_urls(page_num, movie_id):
    base_url = 'http://www.ygdy8.net%s'
    category_base_url = 'http://www.ygdy8.net/html/gndy/dyzz/list_23_%d.html'
    count = 195
    recover = False
    if page_num != -1:
        count = page_num
        recover = True
    while (True):
        try:
            print('-----  Page %d  -----' % count)
            response = requests.get(category_base_url % count)
        except Exception as e:
            print('the max page num is %d' % (count))
            print(e)
            break
        # print(category_base_url % count)
        response.encoding = 'gb2312'
        html = response.text
        # print(html)
        soup = BeautifulSoup(html, "lxml")
        # print(soup.prettify)
        result = soup.find_all('a', class_='ulink')
        result = result[::-1]
        urls = []
        for each in result:
            if recover:
                last_movie_id = int(each['href'].split('/')[-1].split('.')[0])
                # print('movie_id:%d'%id)
                if last_movie_id < movie_id:
                    continue
                else:
                    urls.append(base_url % each['href'])
                    recover = False
            else:
                urls.append(base_url % each['href'])

        # time.sleep(1)
        for url in urls:
            time.sleep(1)
            try:
                get_movie_info_by_url(url)
            except AttributeError:
                s = traceback.format_exc()
                logging.error(s)
                continue
            except ValueError:
                s = traceback.format_exc()
                logging.error(s)
                continue
            except Exception as e:
                movie_id = url.split('/')[-1].split('.')[0]
                save_break_point(count, int(movie_id)+1)
                print('page_num:%d , movie_id:%s' % (count, movie_id))
                s = traceback.format_exc()
                logging.error(s)
                print(e)
                restart_program()
                exit(1)
        count -= 1
        if (count == 0):
            break
        # break


def get_movie_info_by_url(url):
    global movie_count
    response = requests.get(url)
    response.encoding = 'gbk'
    movie_id = url.split('/')[-1].split('.')[0]
    upload_date = url.split('/')[-2]
    html = response.text
    # print(html)
    soup = BeautifulSoup(html, "lxml")
    # print(soup.prettify)

    # print(download_url)
    contents = soup.find('div', id='Zoom')
    magnet_url = soup.find('a', attrs={'href': re.compile("magnet")})
    if magnet_url:
        magnet_url = magnet_url['href']
    else:
        magnet_url = '暂无磁力链接'
    download_url = soup.find('a', attrs={'href': re.compile("ftp")})
    # download_url = soup.find(re.compile("ftp"))
    if download_url:
        download_url = download_url['href']
    else:
        download_url = soup.find(text=re.compile("ftp"))
        if not download_url:
            download_url = '暂时无下载链接'
    img = contents.find('img')
    # print(contents)
    cover_url = img['src']
    translated_title = contents.find(text=re.compile("译(.*)名"))
    if not translated_title:
        translated_title = contents.find(text=re.compile("又(.*)名"))
    translated_title = translated_title.split('名')[1].strip()
    print('----- No.%d  %s -----' % (movie_count, translated_title))
    title = contents.find(text=re.compile("片(.*)名"))
    title = title.split('名')[1].strip()
    year = contents.find(text=re.compile("年(.*)代"))
    if year:
        year = year.split('代')[1].strip()
    else:
        year = '未知'
    country = contents.find(text=re.compile("产(.*)地"))
    if country:
        country = country.split('地')[1].strip()
    else:
        country = contents.find(text=re.compile("国(.*)家"))
        if country:
            country = country.split('家')[1].strip()
        else:
            country = contents.find(text=re.compile("地(.*)区"))
            country = country.split('区')[1].strip()
    categories = contents.find(text=re.compile("类(.*)别"))
    if categories:
        categories = categories.split('别')[1].strip()
    else:
        categories = '未知'
    language = contents.find(text=re.compile("语(.*)言"))
    if language:
        language = language.split('言')[1].strip()
    else:
        language = '未知'
    date = contents.find(text=re.compile("上映日期"))
    if date:
        date = date.split('期')[1].strip()
    else:
        date = '未知'
    tags = contents.find(text=re.compile("标(.*)签"))
    if tags:
        tags = tags.split('签')[1].strip()
    else:
        tags = '无'
    score = contents.find(text=re.compile("豆瓣评分"))
    if score:
        score = score.split('评分')[1].split('/')[0].strip()
        if len(score) == 0:
            score = 0.0
        else:
            score = float(score)
    else:
        score = 0.0
    length = contents.find(text=re.compile("片(.*)长"))
    if length:
        length = length.split('长')[1].strip()
    else:
        length = '未知'
    director = contents.find(text=re.compile("导(.*)演"))
    director = director.split('演')[1].strip()
    star_in_elem = contents.find(text=re.compile("主(.*)演"))
    # star_in = star_in_elem.split("演")[1]
    if star_in_elem:
        star_in = star_in_elem.split("演")[1].strip()+"\n"
        while (True):
            star_in_elem = star_in_elem.next_sibling
            if not star_in_elem:
                break
            if not isinstance(star_in_elem, Tag):
                # if "简" in star_in_elem or '标' in star_in_elem:
                if re.search(r'简(.*)介', star_in_elem) or re.search(r'标(.*)签', star_in_elem):
                    break
                else:
                    star_in += star_in_elem.strip()+'\n'
    else:
        star_in = '无'
    descr_elem = contents.find(text=re.compile("简(.*)介"))
    description = ''
    if not descr_elem:
        description = '暂无简介'
    else:
        while (True):
            descr_elem = descr_elem.next_sibling
            if not descr_elem:
                break
            if isinstance(descr_elem, Tag):
                if descr_elem.name != 'br':
                    break
            else:
                if '获奖情况' in descr_elem:
                    break
                description += descr_elem.strip()+"\n"

    # print(title)
    # print(year)
    # print(country)
    # print(categories)
    # print(language)
    # print(date)
    # print(score)
    # print(length)
    # print(tags)
    # print(director)
    # print(star_in)
    # print(description)
    movie = Movie(movie_id=movie_id, title=title, translated_title=translated_title, upload_date=upload_date, year=year, country=country, categories=categories, language=language,
                  date=date, score=score, length=length, director=director, star_in=star_in,
                  description=description, cover_url=cover_url, download_url=download_url, magnet_url=magnet_url)
    print(add_movie(movie))
    movie_count += 1


# if __name__ == '__main__':
def get_movies():
    print('start gettng movies')
    get_new_movie()
    # page_num, movie_id = recover()
    # get_movie_urls(page_num, movie_id)
