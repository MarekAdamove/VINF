import os
import re


# Class which offers numerous parsing methods
class Parser:

    # Contructor
    # Creates regex patterns
    def __init__(self):
        self.html_paragraph_pattern = r"<p[^>]*>(.*?)<\/p>"
        self.html_tag_pattern = r"<.*?>"
        self.html_special_character_pattern = r"&[A-Za-z0-9]+;|&#[0-9]+;"
        self.html_main_pattern = r"<main>(.*)</main>"
        self.list_pattern = r"<\s*ul[^>]*>.*?<\s*/\s*ul\s*>"
        self.citation_pattern = r"<a\s+href=[\"\']\#cite_note-[0-9]*[\"\']>[^<>]*<\/a>"
        self.main_title_pattern = r"<span\s+class\s*=\s*[\"\']mw-page-title-main[\"\']>([^<>]+)</span>"
        self.main_title_alternative_pattern = r"<h1\s+[^>)]*id=[\"\']firstHeading[\"\'][^>]*>(.*?)<\/h1>"
        self.dot_citation_pattern = r"<a\s+href=[\"\']\#cite_note-[^\"\']*[\"\']>[^<>]*<\/a>"
        self.leftover_citation_pattern = r"\[[0-9]+\]"
        self.new_line_pattern = r"\n"
        self.tab_pattern = r"\t"
        self.return_pattern = r"\r"
        self.wiki_citation_pattern = r"{{cite[^}]*}}"
        self.wiki_blockquote_pattern = r"{{blockquote\|[^}]+?}}"
        self.wiki_blockquote_content_pattern = r"{{blockquote\|([^}]+?)}}"
        self.wiki_curly_braces_content_pattern = r'\{\{.*?\}\}'
        self.wiki_ctg_file_pattern = r"\[\[(?:Category|File)\:[^\]]+\]\]"
        self.wiki_brackets_apostrophes_pattern = r"\[\[|\]\]|\'\'|\*"
        self.wiki_links_pattern = r"\"?\'?\[http[^]]+\]\"?\'?"
        self.wiki_headings_pattern = r"\=+[^\=]+\=+"
        self.wiki_ctg_file_text_pattern = r"(?:File|Category)\:.+?$\n?"

    # Given an HTML document, returns all paragraphs in it
    # @param document <str>: content of the HTML file
    def get_paragraphs(self, document):
        return re.findall(self.html_paragraph_pattern, document, flags=re.I | re.M | re.DOTALL)

    # Given an HTML document, returns the main title of the page
    # @param document <str>: content of the HTML file
    def get_main_title(self, document):
        main_title = re.search(self.main_title_pattern, document, flags=re.I | re.M | re.DOTALL)

        if main_title is None:
            main_title = \
            re.search(self.main_title_alternative_pattern, document, flags=re.I | re.M | re.DOTALL).groups()[0]
            main_title = self.remove_html_tags(main_title)
            return main_title

        return main_title.groups()[0]

    # Given a wiki document, returns the document cleared of wiki headings
    # @param document <str>: page from wiki dump
    def remove_wiki_headings(self, document):
        return re.sub(self.wiki_headings_pattern, "", document, flags=re.I | re.M | re.DOTALL)

    # Given a wiki document, returns the document cleared of custom categories and file mentions from text
    # @param document <str>: page from wiki dump
    def remove_wiki_ctg_file_text(self, document):
        return re.sub(self.wiki_ctg_file_text_pattern, "", document, flags=re.I | re.M | re.DOTALL)

    # Given an HTML document, returns the content of lists inside page's main content
    # @param document <str>: content of the HTML file
    def get_html_list_text(self, document):
        main_content = re.search(self.html_main_pattern, document, flags=re.I | re.M | re.DOTALL).groups()[0]
        return re.findall(self.list_pattern, main_content, flags=re.I | re.M | re.DOTALL)

    # Given a wiki document, returns the document cleared of custom categories and file tags
    # @param document <str>: page from wiki dump
    def remove_wiki_ctg_file_tags(self, document):
        return re.sub(self.wiki_ctg_file_pattern, "", document, flags=re.I | re.M | re.DOTALL)

    # Given a wiki document, returns the document cleared of wiki citations
    # @param document <str>: page from wiki dump
    def remove_wiki_citations(self, document):
        return re.sub(self.wiki_citation_pattern, "", document, flags=re.I | re.M | re.DOTALL)

    # Given a wiki document, returns the document cleared of nested curly brackets
    # @param document <str>: page from wiki dump
    def remove_text_between_nested_curly_brackets(self, document):
        n = 1
        while n:
            document, n = re.subn(r'\{[^{}]*\}', '', document)
        return document

    # Given a wiki document, returns the document cleared of apostrophe & brackets pattern inside the wiki
    # @param document <str>: page from wiki dump
    def edit_wiki_brackets_apostrophes(self, document):
        return re.sub(self.wiki_brackets_apostrophes_pattern, "", document, flags=re.I | re.M | re.DOTALL)

    # Given a wiki document, returns the document cleared of wiki links
    # @param document <str>: page from wiki dump
    def remove_wiki_links(self, document):
        return re.sub(self.wiki_links_pattern, "", document, flags=re.I | re.M | re.DOTALL)

    # Given a wiki document, returns the document with blockquotes cleared of wiki syntax
    # @param document <str>: page from wiki dump
    def edit_wiki_blockquotes(self, document):
        quote = re.search(self.wiki_blockquote_content_pattern, document, flags=re.I | re.M | re.DOTALL)
        return re.sub(self.wiki_blockquote_pattern,
                      quote.group(0) if quote is not None else "",
                      document,
                      flags=re.I | re.M | re.DOTALL)

    # Given a text, returns text cleared of html tags
    # @param text <str>: text to process
    def remove_html_tags(self, text):
        return re.sub(self.html_tag_pattern, "", text, flags=re.I | re.M | re.DOTALL)

    # Given a text, returns text cleared of special html characters
    # @param text <str>: text to process
    def remove_html_special_characters(self, text):
        return re.sub(self.html_special_character_pattern, "", text, flags=re.I | re.M | re.DOTALL)

    # Given a text, returns text cleared of citations
    # @param text <str>: text to process
    def remove_citations(self, text):
        text = re.sub(self.citation_pattern, "", text, flags=re.I | re.M | re.DOTALL)
        text = re.sub(self.dot_citation_pattern, "", text, flags=re.I | re.M | re.DOTALL)
        return re.sub(self.leftover_citation_pattern, "", text, flags=re.I | re.M | re.DOTALL)

    # Given a text, returns text cleared of new lines
    # @param text <str>: text to process
    def remove_new_lines(self, text):
        return re.sub(self.new_line_pattern, "", text, flags=re.I | re.M | re.DOTALL)

    # Given a text, returns text cleared of tabulators
    # @param text <str>: text to process
    def remove_tabs(self, text):
        return re.sub(self.tab_pattern, "", text, flags=re.I | re.M | re.DOTALL)

    # Given a text, returns text cleared of escape return characters
    # @param text <str>: text to process
    def remove_returns(self, text):
        return re.sub(self.return_pattern, "", text, flags=re.I | re.M | re.DOTALL)

    # Given an HTML document, returns cleaned content of the document
    # @param document <str>: document to clean
    def parse_paragraphs(self, document):
        clean_paragraphs = []
        paragraphs = self.get_paragraphs(document)
        for paragraph in paragraphs:
            clean_paragraph = self.remove_citations(paragraph)
            clean_paragraph = self.remove_html_tags(clean_paragraph)
            clean_paragraph = self.remove_html_special_characters(clean_paragraph)
            clean_paragraph = self.remove_new_lines(clean_paragraph)
            clean_paragraph = self.remove_tabs(clean_paragraph)
            clean_paragraph = self.remove_returns(clean_paragraph)

            clean_paragraphs.append(clean_paragraph)

        return clean_paragraphs

    # Given an HTML document, returns cleaned content of the lists inside the document
    # @param document <str>: document to clean
    def parse_lists(self, document):
        clean_lists = []
        lists = self.get_html_list_text(document)
        for list in lists:
            clean_list = self.remove_citations(list)
            clean_list = self.remove_html_tags(clean_list)
            clean_list = self.remove_html_special_characters(clean_list)
            clean_list = self.remove_new_lines(clean_list)
            clean_list = self.remove_tabs(clean_list)
            clean_list = self.remove_returns(clean_list)

            clean_lists.append(clean_list)

        return clean_lists


if __name__ == "__main__":
    # Create parser object
    parser = Parser()

    crawled_data_path = "crawled_data"
    parsed_data_output_directory = "."

    # Open file where parsed data will be stored & create header
    f_w = open(f"{parsed_data_output_directory}/parsed.tsv", "w", encoding="utf-8")
    f_w.write("Title\tParagraphs_content\tLists_content\n")

    # Lists all the HTML in the directory
    ls = os.listdir(crawled_data_path)

    current_file_numer = 1
    for file_name in ls:
        file = open(fr"{crawled_data_path}/{file_name}", "r", encoding="utf-8")
        file_content = file.read()

        # Get main title of the document
        main_page_title = parser.get_main_title(file_content)

        print(f"[{current_file_numer}]: {main_page_title}")
        current_file_numer += 1

        parsed_paragraphs = " ".join(parser.parse_paragraphs(file_content))
        parsed_lists = " ".join(parser.parse_lists(file_content))
        f_w.write(f"{main_page_title if main_page_title is not None else ''}\t{parsed_paragraphs}\t{parsed_lists}\n")

        file.close()
