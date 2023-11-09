import requests
import re


class Crawler:

    def __init__(self, starting_url, num_pages_to_download, root_url=""):
        self.SAVE_HTML_PATH = 'data'
        self.ROOT_URL = root_url
        self.visited_urls = []
        self.unvisited_urls = [starting_url]
        self.num_pages_to_download = num_pages_to_download
        self.used_titles = []
        self.counter = 0

        self.crawl()
    def download_url(self, url):
        return requests.get(url)

    def get_main_title(self, document):
        main_title = re.search(r"<span\s+class\s*=\s*[\"\']mw-page-title-main[\"\']>([^<>]+)</span>", document, flags=re.I | re.M | re.DOTALL)

        if main_title is None:
            main_title = re.search(r"<h1\s+[^>)]*id=[\"\']firstHeading[\"\'][^>]*>(.*)<\/h1>", document, flags=re.I | re.M | re.DOTALL).groups()[0]
            main_title = re.sub(r"<.*?>", main_title,flags=re.I | re.M | re.DOTALL)
            return main_title

        return main_title.groups()[0]

    def save_html(self, page):
        page_title_tag = re.search("<title.*>.*</title>", page.text, flags= re.IGNORECASE | re.MULTILINE)
        page_title = re.sub("<.*?>", "", page_title_tag.group())
        page_title = re.sub(r'[/*?:"<>|]', "", page_title)

        # if page_title not in self.used_titles:
        #     self.used_titles.append(page_title)
        # else:
        #     self.used_titles.append(page_title)
        #     page_title += f"{self.used_titles.count(page_title)}"

        with open(f"{self.SAVE_HTML_PATH}/{page_title}_{self.counter}.html", "w", encoding="utf-8") as file:
            file.write(page.text)
            file.close()

        self.counter += 1

    def find_links(self, page):
        #link_pattern = r"<a\s+href\s*=\s*[\"\'](/[^\.\"\']+)[\"\'].*>.*</a>"
        link_pattern = r"<a\s+href\s*=\s*[\"\'](/wiki/(?!(?:Forum:|User:|File:|Special:))[^\"\']+).*>.*</a>"

        return re.findall(link_pattern, page.text, flags= re.IGNORECASE | re.MULTILINE)

    def crawl(self):
        for relative_link in self.unvisited_urls:
            if relative_link in self.visited_urls:
                self.unvisited_urls.remove(relative_link)
                continue

            if len(self.visited_urls) < self.num_pages_to_download:
                response = self.download_url(self.ROOT_URL + relative_link)
                self.visited_urls.append(relative_link)
                self.unvisited_urls.remove(relative_link)

                self.save_html(response)
                self.unvisited_urls += self.find_links(response)

                print(f"[{len(self.visited_urls)}/{self.num_pages_to_download}] Page: {self.ROOT_URL}{relative_link} downloaded.")
            else:
                break



crawler = Crawler("/wiki/World_of_Warcraft:_Dragonflight", 13000,"https://warcraft.wiki.gg")
