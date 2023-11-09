import os
import re


class Parser:

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

    def get_paragraphs(self, document):
        return re.findall(self.html_paragraph_pattern, document, flags=re.I | re.M | re.DOTALL)

    def get_main_title(self, document):
        main_title = re.search(self.main_title_pattern, document, flags=re.I | re.M | re.DOTALL)

        if main_title is None:
            main_title = re.search(self.main_title_alternative_pattern, document, flags=re.I | re.M | re.DOTALL).groups()[0]
            main_title = self.remove_html_tags(main_title)
            return main_title

        return main_title.groups()[0]

    def get_html_list_text(self, document):
        main_content = re.search(self.html_main_pattern, document, flags=re.I | re.M | re.DOTALL).groups()[0]
        return re.findall(self.list_pattern, main_content, flags=re.I | re.M | re.DOTALL)

    def remove_html_tags(self, text):
        return re.sub(self.html_tag_pattern, "", text, flags=re.I | re.M | re.DOTALL)

    def remove_html_special_characters(self, text):
        return re.sub(self.html_special_character_pattern, "", text, flags=re.I | re.M | re.DOTALL)

    def remove_citations(self, text):
        text = re.sub(self.citation_pattern, "", text, flags=re.I | re.M | re.DOTALL)
        text = re.sub(self.dot_citation_pattern, "", text, flags=re.I | re.M | re.DOTALL)
        return re.sub(self.leftover_citation_pattern, "", text, flags=re.I | re.M | re.DOTALL)

    def remove_new_lines(self, text):
        return re.sub(self.new_line_pattern, "", text, flags=re.I | re.M | re.DOTALL)

    def remove_tabs(self, text):
        return re.sub(self.tab_pattern, "", text, flags=re.I | re.M | re.DOTALL)

    def remove_returns(self, text):
        return re.sub(self.return_pattern, "", text, flags=re.I | re.M | re.DOTALL)

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


parser = Parser()

f_w = open("parsed.tsv", "w", encoding="utf-8")
f_w.write("Title\tParagraphs_content\tLists_content\n")

ls = os.listdir("data")
current_file_numer = 1
for file_name in ls:
    file = open(f"data/{file_name}", "r", encoding="utf-8")
    file_content = file.read()

    main_page_title = parser.get_main_title(file_content)
    print(f"[{current_file_numer}]: {main_page_title}")
    current_file_numer += 1

    parsed_paragraphs = " ".join(parser.parse_paragraphs(file_content))

    parsed_lists = " ".join(parser.parse_lists(file_content))

    f_w.write(f"{main_page_title if main_page_title is not None else ''}\t{parsed_paragraphs}\t{parsed_lists}\n")
    file.close()
