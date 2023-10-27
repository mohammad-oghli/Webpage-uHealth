import plotly.graph_objects as plt


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


def plot_pie(total_a, total_b):
    url_health = ['HEALTHY', 'BROKEN']
    values = [total_a, total_b]
    fig = plt.Figure(
        plt.Pie(
            labels=url_health,
            values=values,
            hoverinfo="label+percent",
            textinfo="percent",
            marker=dict(colors=['#83c9ff', '#b2182b'])
        ))
    return fig


def display_sources(src_arr):
    if len(src_arr) > 0:
        return "\n".join(src_arr)
    else:
        return "Sorry, no sources for this tag"
