import streamlit as st
from bs4 import BeautifulSoup
import requests
from requests.sessions import Session
from requests import exceptions
from threading import Thread, local
from queue import Queue
import time
import plotly.graph_objects as plt
from helper import validate_webpage, scrap_links, display_sources

# Global Variables
q = Queue(maxsize=0)
thread_local = local()
h_links = []
uh_links = []


def get_session() -> Session:
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()  # Create a new Session if not exists
    return thread_local.session


def fetch_link() -> None:
    '''fetch link worker, get URL from queue until no url left in the queue'''
    session = get_session()
    while not q.empty():
        url = q.get()
        try:
            session.get(url['sc_link'], timeout=3)
            h_links.append(url)
        except (exceptions.ConnectionError, exceptions.Timeout, exceptions.InvalidSchema):
            uh_links.append(url)
        q.task_done()  # tell the queue, this url fetching work is done


def fetch_all(urls) -> None:
    thread_num = 10
    for i in range(thread_num):
        t_worker = Thread(target=fetch_link())
        t_worker.start()
    q.join()


def analyze_webpage(wp_url):
    '''
    Check web page URLs health

    :param
    wp_url(str): Valid url of the web page

    :return
    web_page(dict): Dictionary containing analytics information of the requested web page URLs,

    if web page url is invalid it will return message indicating url error
    '''
    web_page = {}
    sc_links = []
    # Local h_links, uh_links variables
    h_links = []
    uh_links = []
    links = []
    title = ""
    avg_h = 0.0
    try:
        wp_url = wp_url.strip()
        response = requests.get(wp_url)
        if not validate_webpage(response):
            msg = "Sorry, the requested url isn't a web page."
            return msg
        data = response.text
        soup = BeautifulSoup(data, "html.parser")  # create a soup object using the variable 'data'
        if soup.find('title'):
            title = soup.find('title').string.strip()
        if not soup.findAll('a', href=True) is None:
            links = soup.findAll('a', href=True)
        # print(links)
        if len(links) > 0:
            sc_links = scrap_links(wp_url, links)
        # print(sc_links)

    except exceptions.ConnectionError:
        msg = "Sorry, the requested web page url is invalid."
        return msg
    except exceptions.MissingSchema:
        msg = "Incorrect requested url format!"
        return msg

    for url in sc_links:
        try:
            # if not 'linkedin' in url['sc_link']:
            requests.get(url['sc_link'], timeout=3)
            h_links.append(url)
            # print(res.status_code)
        except (exceptions.ConnectionError, exceptions.Timeout, exceptions.InvalidSchema):
            uh_links.append(url)

    if len(links) > 0:
        avg_h = round((len(h_links) * 100) / len(sc_links), 2)
        # avg_h = round((len(h_links) * 100) / (len(h_links) + len(uh_links)), 2)
    summary = f"""____________Summary______________
Webpage Title: {title}
Total link: {len(sc_links)}
Total Healthy link: {len(h_links)}
Total Broken link: {len(uh_links)}
Average Healthy linking: {avg_h} %
"""
    web_page['s'] = summary
    web_page['href'] = len(links)
    web_page['h_links'] = h_links
    web_page['uh_links'] = uh_links
    web_page['avg_h'] = avg_h
    # web_page['display'] = display_sources
    return web_page


def analyze_webpage_opt(wp_url):
    '''
    Check web page URLs health (Optimized version using Multi-Threading)

    :param
    wp_url(str): Valid url of the web page

    :return
    web_page(dict): Dictionary containing analytics information of the requested web page URLs,

    if web page url is invalid it will return message indicating url error
    '''
    web_page = {}
    sc_links = []
    links = []
    title = ""
    avg_h = 0.0
    try:
        wp_url = wp_url.strip()
        response = requests.get(wp_url)
        if not validate_webpage(response):
            msg = "Sorry, the requested url isn't a web page."
            return msg
        data = response.text
        soup = BeautifulSoup(data, "html.parser")  # create a soup object using the variable 'data'

        if soup.find('title'):
            title = soup.find('title').string.strip()
        if not soup.findAll('a', href=True) is None:
            links = soup.findAll('a', href=True)
        # print(links)
        if len(links) > 0:
            sc_links = scrap_links(wp_url, links)
            # print(sc_links)
            for url in sc_links:
                q.put(url)

    except exceptions.ConnectionError:
        msg = "Sorry, the requested web page url is invalid."
        return msg
    except exceptions.MissingSchema:
        msg = "Incorrect requested url format!"
        return msg
    # print(display_sources(sc_links))
    fetch_all(sc_links)

    if len(links) > 0:
        avg_h = round((len(h_links) * 100) / len(sc_links), 2)
        # avg_h = round((len(h_links) * 100) / (len(h_links) + len(uh_links)), 2)
    summary = f"""____________Summary______________
Webpage Title: {title}
Total link: {len(sc_links)}
Total Healthy link: {len(h_links)}
Total Broken link: {len(uh_links)}
Average Healthy linking: {avg_h} %
"""
    web_page['s'] = summary
    web_page['href'] = len(links)
    web_page['h_links'] = h_links
    web_page['uh_links'] = uh_links
    web_page['avg_h'] = avg_h
    # web_page['display'] = display_sources
    return web_page


def st_ui():
    '''
    Render the User Interface of the application endpoints
    '''
    st.title("Web Page Linking Health")
    st.caption("Meta Data Validation")
    st.info("Developed by Oghli")
    st.header("Enter a web page url to check it")
    url = st.text_input(label='Web Site URL', placeholder='type your url')
    if url:
        start = time.time()
        analyze_result = analyze_webpage_opt(url)
        end = time.time()
        print(f'Analyzing: {end - start} seconds')
        if type(analyze_result) is dict:
            summary = analyze_result['s']
            st.subheader("Brief Information")
            summary += f"Analyzing Elapsed Time: {round(end - start, 2)} seconds"
            st.text(summary)
            url_health = ['HEALTHY', 'BROKEN']
            values = [len(analyze_result['h_links']), len(analyze_result['uh_links'])]
            fig = plt.Figure(
                plt.Pie(
                    labels=url_health,
                    values=values,
                    hoverinfo="label+percent",
                    textinfo="percent",
                    marker=dict(colors=['#83c9ff', '#b2182b'])
                ))
            st.header("URL HEALTH")
            st.plotly_chart(fig)
            st.subheader("Detailed Information")
            if analyze_result['h_links']:
                st.write("##### _Healthy Links Source_")
                for item in analyze_result['h_links']:
                    st.write(f"{item['name']} [{item['sc_link']}]")
                st.markdown("""---""")
            if analyze_result['uh_links']:
                st.write("##### _Broken Links Source_")
                for item in analyze_result['uh_links']:
                    st.write(f"{item['name']} [{item['sc_link']}]")
                st.markdown("""---""")
        else:
            st.error(analyze_result)


if __name__ == "__main__":
    # render the app using streamlit ui function
    st_ui()
    # url = "https://stackoverflow.com"
    # analyze_result = analyze_webpage(url)
    # if type(analyze_result) is dict:
    #     summary = analyze_result['s']
    #     print(summary)
    # else:
    #     print(analyze_result)
