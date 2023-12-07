import requests
import re

# Crawler class -> one instance suits as one crawler
class Crawler:

    # Constructor
    # @param num_pages_to_download <int>: number of pages to download; e.g. 15000
    # @param save_html_path <str>: path to directory, where downloaded HTML files should be saved; e.g. "crawled_data"
    # @param root_url <str>: root starting URL to start crawling; e.g. "https://warcraft.wiki.gg"
    # @param starting_url <str>: relative URL address to root_url the crawling; e.g. "/wiki/World_of_Warcraft:_Dragonflight"
    def __init__(self, num_pages_to_download, save_html_path, root_url="", starting_url=""):
        self.SAVE_HTML_PATH = save_html_path
        self.ROOT_URL = root_url
        self.visited_urls = []
        self.unvisited_urls = [starting_url]
        self.num_pages_to_download = num_pages_to_download
        self.used_titles = []
        self.counter = 0

        self.crawl()

    # Sends a request to given url and returns response from server
    # @param url <str>: url to send request to; e.g. "https://warcraft.wiki.gg"
    def download_url(self, url):
        return requests.get(url)

    # Given an HTML document, finds and returns main title of the page's content
    # @param document <str>: HTML document
    def get_main_title(self, document):
        main_title = re.search(r"<span\s+class\s*=\s*[\"\']mw-page-title-main[\"\']>([^<>]+)</span>", document, flags=re.I | re.M | re.DOTALL)

        if main_title is None:
            main_title = re.search(r"<h1\s+[^>)]*id=[\"\']firstHeading[\"\'][^>]*>(.*?)<\/h1>", document, flags=re.I | re.M | re.DOTALL).groups()[0]
            main_title = re.sub(r"<.*?>","", main_title, flags=re.I | re.M | re.DOTALL)
            return main_title

        return main_title.groups()[0]

    # Given a server response, saves the HTML to the saving directory
    # @param page <Response>: response from server
    def save_html(self, page):
        page_title_tag = re.search("<title.*>.*</title>", page.text, flags= re.IGNORECASE | re.MULTILINE)
        page_title = re.sub("<.*?>", "", page_title_tag.group())
        page_title = re.sub(r'[/*?:"<>|]', "", page_title)

        with open(f"{self.SAVE_HTML_PATH}/{page_title}_{self.counter}.html", "w", encoding="utf-8") as file:
            file.write(page.text)
            file.close()

        self.counter += 1

    # Given a server response, returns a list of all links found within the HTML
    # @param page <Response>: response from server
    def find_links(self, page):
        link_pattern = r"<a\s+href\s*=\s*[\"\'](/wiki/(?!(?:Forum:|User:|File:|Special:))[^\"\']+).*>.*</a>"

        return re.findall(link_pattern, page.text, flags= re.IGNORECASE | re.MULTILINE)

    # Method, which initiates crawling on root url + starting (relative) url using BFS algorithm
    def crawl(self):

        # For each link that is in unvisited_urls list, checks if the relative link is in the visited_urls list
        # if so, removes that link from unvisited_urls and goes to another relative link; further, it is checked
        # whether we already have downloaded a given number of pages - if so, crawling stops; further, it is checked
        # through main title of the page for the duplicates - if the page is duplicate, we don't count nor save it
        for relative_link in self.unvisited_urls:
            if relative_link in self.visited_urls:
                self.unvisited_urls.remove(relative_link)
                continue

            if len(self.visited_urls) < self.num_pages_to_download:
                response = self.download_url(self.ROOT_URL + relative_link)
                main_title = self.get_main_title(response.text)
                if main_title in self.used_titles:
                    continue
                print(f"[{self.counter}] {main_title}\n")
                self.used_titles.append(main_title)
                self.visited_urls.append(relative_link)
                self.unvisited_urls.remove(relative_link)

                self.save_html(response)
                self.unvisited_urls += self.find_links(response)
            else:
                break


if __name__ == "__main__":
    crawler = Crawler(13000, "crawled_data","https://warcraft.wiki.gg","/wiki/World_of_Warcraft:_Dragonflight")