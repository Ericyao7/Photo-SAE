# coding=utf-8
# from __future__ import with_statement


import os
import sys
import MySQLdb
from PIL import Image
import StringIO
import random
from datetime import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# configuration

import sae.const
from setting import *
import re
from werkzeug import secure_filename
import sae.storage
access_key = sae.const.ACCESS_KEY
secret_key = sae.const.SECRET_KEY
appname = sae.const.APP_NAME


def connect_db():
    return MySQLdb.connect(
        sae.const.MYSQL_HOST, sae.const.MYSQL_USER, sae.const.MYSQL_PASS,
        sae.const.MYSQL_DB, port=int(sae.const.MYSQL_PORT), charset='utf8')


def save_name(filename, size):
    ext = filename.rsplit('.', 1)[1]
    d = filename.rsplit('.', 1)[0]
    fn = datetime.now().strftime('%Y%m%d%H%M%S')
    fn = fn + '_%d' % random.randint(0, 100)
    name = os.path.join(d + size + fn + "." + ext)
    return name


class Posts:

    @staticmethod
    def add_a_post(title, date, local, tags, content, hero, files):
        Photos.add_a_post
        conn = connect_db()
        c = conn.cursor()
        c.execute(
            "INSERT INTO `news` (`title`,`content`,`favor`,`top`,`source`,`link`) VALUES ('%s','%s','%s','%d','%s','%s');" % (news))
        conn.commit()
        id = int(c.lastrowid)
        c.close()
        return id

    @staticmethod
    def get_news_count():
        conn = connect_db()
        c = conn.cursor()
        c.execute(
            'SELECT count(`id`) FROM `naaln_posts`')
        conn.commit()
        count = list(c.fetchall())[0][0]
        c.close()
        count = count if count else 1
        return count

    @staticmethod
    def get_per_count(page):
        page = page - 1
        count = Posts.get_news_count()
        pagecount = (count - 1) / POSTS_PER_PAGE + 1

    @staticmethod
    def get_news_by_page(page):
        page = page - 1
        conn = connect_db()
        c = conn.cursor()
        c.execute(
            'SELECT `id`, `title`, `article`, `color`, `time`, `location`, `content`, `tags` \
            FROM `naaln_posts` ORDER BY `time` DESC LIMIT %s,%s' % (page * POSTS_PER_PAGE, POSTS_PER_PAGE))
        msgs = list(c.fetchall())
        blogs = []
        for id, title, article, color, time, location, content, tags in msgs:
            photos = Photos.get_photos_by_pid(id)
            length = len(photos)
            blog = [id, title, article, color,
                    time, location, content, photos[1:length], [photos[0]]]
            blogs.append(blog)
        mess = tuple(blogs)
        c.close()
        return mess

    @staticmethod
    def get_all_posts():
        conn = connect_db()
        c = conn.cursor()
        c.execute(
            'SELECT `id`, `title`, `article`, `color`, `time`, `location`, `content` FROM `naaln_posts`')
        msgs = list(c.fetchall())
        c.close()

        return msgs


class Photos:

    @staticmethod
    def add_a_photo(file):
        Upload.upload_image(file)

    @staticmethod
    def get_photos_by_pid(id):
        conn = connect_db()
        c = conn.cursor()
        c.execute(
            'SELECT `href`, `src`, `alt` FROM `naaln_photo` WHERE `blog_id` =%s ORDER BY `hero` DESC' % id)
        photos = list(c.fetchall())
        c.close()
        return photos


class Users:

    @staticmethod
    def login(name, password):
        conn = connect_db()
        c = conn.cursor()

        c.execute(
            'SELECT `id`, `user`, `password` FROM `naaln_users` WHERE `user` ="%s"' % name)
        userinfo = c.fetchall()
        c.close()

        msg = {}
        if userinfo:
            for id, user, psd in userinfo:

                if password == psd:
                    msg['state'] = 'successed'
                    msg['message'] = 'You logged in'
                else:
                    msg['state'] = 'fail'
                    msg['message'] = 'Invalid password'

        else:
            msg['state'] = 'fail'
            msg['message'] = 'Invalid username'
        return msg


class Upload:

    @staticmethod
    def upload_image(img, name='_o_', x_s=0, y_s=0):
        x_s = int(x_s)
        img.seek(0)
        bucket = sae.storage.Bucket('upload')
        bucket.put()
        filename = secure_filename(img.filename)

        im = Image.open(img)

        (x, y) = im.size
        out = im

        if int(x_s) == int(y_s) and y_s > 0:
            if x > y:
                x_s = x * y_s / y
                x_c = (x_s - y_s) / 2
                y_c = 0
                x_d = x_c + y_s
                y_d = y_s

            else:
                y_s = y * x_s / x
                x_c = 0
                y_c = (y_s - x_s) / 2
                x_d = x_s
                y_d = y_c + x_s

            out = im.resize((x_s, y_s), Image.ANTIALIAS)
            box = (x_c, y_c, x_d, y_d)
            out = out.crop(box)
        elif x_s > 0:
            y_s = y * x_s / x
            out = im.resize((x_s, y_s), Image.ANTIALIAS)
        elif y_s > 0:
            x_s = x * y_s / y
            out = im.resize((x_s, y_s), Image.ANTIALIAS)

        s_image = save_name(img.filename, name)
        output = StringIO.StringIO()
        out.save(output, 'JPEG')

        bucket.put_object(s_image, output.getvalue())
        output.close()
        url = bucket.generate_url(s_image)

        return url
