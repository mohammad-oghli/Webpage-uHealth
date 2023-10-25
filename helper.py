import requests
from requests.sessions import Session
from requests import exceptions
from threading import Thread
import config


def get_session() -> Session:
    if not hasattr(config.thread_local, 'session'):
        config.thread_local.session = requests.Session()  # Create a new Session if not exists
    return config.thread_local.session


def fetch_link() -> None:
    '''fetch link worker, get URL from queue until no url left in the queue'''
    session = get_session()
    while not config.q.empty():
        url = config.q.get()
        try:
            session.get(url['sc_link'], timeout=3)
            config.h_links.append(url)
        except (exceptions.ConnectionError, exceptions.Timeout, exceptions.InvalidSchema):
            config.uh_links.append(url)
        config.q.task_done()  # tell the queue, this url downloading work is done


def fetch_all(urls) -> None:
    thread_num = 10
    for i in range(thread_num):
        t_worker = Thread(target=fetch_link())
        t_worker.start()
    config.q.join()


def validate_webpage(r):
    if 'text/html' in r.headers['content-type']:
        return True
    return False


def scrap_links(url, links):
    link_list = []
    for a in links:
        link_dict = {}
        link_dict['name'] = ' '.join(a.text.split())
        href = a.get('href')
        if href:
            # print(href)
            if href[0] == "#":
                link_dict['sc_link'] = url + "/#"
                # sc_links.append(url + "/#")
            elif href[0] == "/":
                link_dict['sc_link'] = url + href
                # sc_links.append(url + href)
            else:
                if "http" in href:
                    link_dict['sc_link'] = href
                    # sc_links.append(href)
            if 'sc_link' in link_dict:
                link_list.append(link_dict)
    return link_list


def display_sources(src_arr):
    if len(src_arr) > 0:
        return "\n".join(src_arr)
    else:
        return "Sorry, no sources for this tag"
