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

        self.crawl()
    def download_url(self, url):
        return requests.get(url)

    def save_html(self, page):
        page_title_tag = re.search("<title.*>.*</title>", page.text, flags= re.IGNORECASE | re.MULTILINE)
        page_title = re.sub("<.*?>", "", page_title_tag.group())
        page_title = re.sub(r'[/*?:"<>|]', "", page_title)

        self.used_titles.append(page_title)

        if page_title in self.used_titles:
            page_title += f"{self.used_titles.count(page_title)+1}"

        with open(f"{self.SAVE_HTML_PATH}/{page_title}.html", "w", encoding="utf-8") as file:
            if file is None:
                print("Error")
            else:
                file.write(page.text)

    def find_links(self, page):
        link_pattern = r"<a\s+href\s*=\s*[\"\'](/[^\.\"\']+)[\"\'].*>.*</a>"

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



crawler = Crawler("/wiki/World_of_Warcraft:_Dragonflight", 5000,"https://wowpedia.fandom.com")
