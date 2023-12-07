import csv
import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.functions import explode
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql.functions import expr
from Parser import Parser
import nltk
from nltk.tokenize import sent_tokenize

csv.field_size_limit(1000000)
# nltk.download('punkt')
parser = Parser()


# Cleans wiki page using parser, uses NLTK to tokenize text into sentences and searches for occurrences of entities
# In the end, appends sentences to the entity files
def process_page(row, keywords, output_directory_path):
    title = row["title"]
    content = str(row["_VALUE"])

    # Cleaning
    content = parser.remove_html_tags(content)
    content = parser.remove_wiki_citations(content)
    content = parser.edit_wiki_blockquotes(content)
    content = parser.remove_text_between_nested_curly_brackets(content)
    content = parser.edit_wiki_brackets_apostrophes(content)
    content = parser.remove_wiki_ctg_file_tags(content)
    content = parser.remove_wiki_links(content)
    content = content.replace("|", " or ")
    content = parser.remove_wiki_headings(content)
    content = parser.remove_wiki_ctg_file_text(content)
    content = parser.remove_new_lines(content)

    # Tokenizes text into sentences
    sentences = sent_tokenize(content)

    # Will hold entity - sentences like {"Illidan": ["Illidan is a demon hunter.", "He is using fel energy."]}
    entity_sentences = {}

    # Searches for entities in sentences
    for entity in keywords:
        entity_sentence_occurrences = [sentence for sentence in sentences if
                                       re.search(rf'\b{entity.lower()}\b', sentence.lower())]

        if len(entity_sentence_occurrences):
            entity_sentences.update({entity: entity_sentence_occurrences})

    # Saves sentences into corresponding files
    for entity, entity_sentences_list in entity_sentences.items():
        entity_filename = re.sub(r"[\*\?\"\|\\\/\:<>]", "", entity, flags=re.I | re.M | re.DOTALL)
        f_w = open(f"{wiki_output_directory_path}/" + entity_filename + ".txt", "a", encoding="utf-8")
        f_w.write(f"\n[[{entity}]]\n")
        f_w.write(" ".join(entity_sentences_list))
        f_w.close()


if __name__ == "__main__":

    parsed_data_file_path = "parsed.tsv"
    wiki_output_directory_path = "wiki_parsed"

    # Creates a list of entities to be searched for
    entities = []
    with open(parsed_data_file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')

        for row in reader:
            entities.append(row[0])

    # Initiates spark session
    spark = SparkSession.builder.appName("WikiParser").config("spark.jars.packages",
                                                              "com.databricks:spark-xml_2.12:0.15.0").getOrCreate()

    # Reads wiki dump
    df = spark.read.format('xml').options(rowTag='page', charset='UTF-8').load(
        "wiki_dump/enwiki-20231101-pages-articles-multistream.xml")

    # Terms to filter pages with
    WOW_RELATED_TERMS = ["WoW", "World of Warcraft", "Warcraft", "Blizzard Entertainment"]

    # Creation of filtering condition
    condition = col("title").contains(WOW_RELATED_TERMS[0])
    for term in WOW_RELATED_TERMS[1:]:
        condition = condition | col("title").contains(term)

    # Creates new boolean value column - if the WOW RELATED TERM is in the page title
    df_with_multiword_keyword = df.withColumn("multiword_keyword_present", condition)

    # Filters the dataset
    df_with_multiword_keyword = df_with_multiword_keyword.filter(col("multiword_keyword_present") == "True")

    # Creates a dataset made out of title and revision.text text
    df_with_multiword_keyword = df_with_multiword_keyword.select("title", "revision.text._VALUE")

    # For each row, do process_page function
    df_with_multiword_keyword.foreach(lambda row: process_page(row, entities, wiki_output_directory_path))