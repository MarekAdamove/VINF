import lucene
import os
import csv
import sys
from java.nio.file import Paths
from java.lang import Integer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, StringField, TextField, FieldType
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader, IndexOptions
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.search import IndexSearcher, BooleanQuery, BooleanClause
from org.apache.lucene.queryparser.classic import QueryParser

# Indexer class
class Indexer:
    JVM_INITIALIZED = False

    @classmethod
    def init_jvm(cls):
        if not cls.JVM_INITIALIZED:
            lucene.initVM()
            cls.JVM_INITIALIZED = True

    ## Initiates pylucene, index directory, standard analyzer, index config and index writer
    def __init__(self):
        self.init_jvm()
        self.index_directory = "index"
        if not os.path.exists(self.index_directory):
            os.mkdir(self.index_directory)

        self.index_path = Paths.get(self.index_directory)

        self.analyzer = StandardAnalyzer()
        self.config = IndexWriterConfig(self.analyzer)
        self.config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        self.writer = IndexWriter(FSDirectory.open(self.index_path), self.config)
        self.dir = FSDirectory.open(self.index_path)

    # Create a new index from the input file
    def index_data(self, path_to_parsed_data):
        with open(path_to_parsed_data, "r", encoding='utf-8') as parsed_data:
            reader = csv.reader(parsed_data, delimiter="\t")
            # Reads header, that will be used as document fields
            header = next(reader)
            for i, line in enumerate(reader):
                doc = Document()

                field_type = FieldType()
                field_type.setStored(True)
                field_type.setIndexOptions(IndexOptions.DOCS)

                for j, field_name in enumerate(header):
                    doc.add(Field(field_name, line[j], field_type))

                self.writer.addDocument(doc)

        self.writer.commit()
        self.writer.close()

    # Search index
    # @param query <str>: Query for index; e.g. "Title:Illidan AND Wiki:fel"
    def search_documents_and(self, query, number_of_results):
        if number_of_results < 0:
            return None

        if query == "":
            return None

        counter = 0

        multi_queries = query.split(" AND ")
        searcher = IndexSearcher(DirectoryReader.open(self.dir))

        # Boolean query builder helps with boolean queries
        bool_query = BooleanQuery.Builder()

        for multi_query in multi_queries:
            column_to_search, keyword = multi_query.split(":")
            parsed_query = QueryParser(column_to_search, self.analyzer).parse(f"{keyword}")
            bool_query.add(parsed_query, BooleanClause.Occur.MUST)

        results = searcher.search(bool_query.build(), number_of_results)

        return_results = []

        for result in results.scoreDocs:
            counter += 1
            return_results.append((counter, searcher.doc(result.doc).get("Title"), result.score))

            if counter >= number_of_results:
                break

        return return_results

# Search index
    # @param query <str>: Query for index; e.g. "Title:Illidan OR Wiki:fel"
    def search_documents_or(self, query, number_of_results):
        if number_of_results < 0:
            return None

        if query == "":
            return None

        counter = 0

        multi_queries = query.split(" OR ")
        searcher = IndexSearcher(DirectoryReader.open(self.dir))

        # Boolean query builder helps with boolean queries
        bool_query = BooleanQuery.Builder()

        for multi_query in multi_queries:
            column_to_search, keyword = multi_query.split(":")
            parsed_query = QueryParser(column_to_search, self.analyzer).parse(f"{keyword}")
            bool_query.add(parsed_query, BooleanClause.Occur.SHOULD)

        results = searcher.search(bool_query.build(), number_of_results)

        return_results = []

        for result in results.scoreDocs:
            counter += 1
            return_results.append((counter, searcher.doc(result.doc).get("Title"), result.score))

            if counter >= number_of_results:
                break

        return return_results

    # Prints results to stdout
    # @param results <list>: results to be printed; contains tuples (int, str, float)
    def print_results(self, results):
        if len(results) == 0:
            print("No results found =(")
            return

        for counter, doc_name, doc_score in results:
            print(f"  {counter}\n======")
            print("=  Title: ", doc_name, "\n=\tScore: %.5f" % doc_score)
            print("======\n")

if __name__ == "__main__":
    csv.field_size_limit(sys.maxsize)
    indexer = Indexer()
    print("Please select one of the options:\n\t[1]: Create new index\n\t[2]: Query\n\t[3]: Exit")
    start_choice = input("Choice: ")

    if start_choice not in ["1", "2"]:
        quit()

    if start_choice == "1":
        data_file_path = input("Path to the file to be indexed: ")
        indexer.index_data(data_file_path)
        continue_query = input("Indexing finished. Do you wish to proceed to queries? Y/N: ")

        if continue_query == "Y":
            start_choice = "2"
        else:
            quit()

    while start_choice == "2":
        or_and = str(input("Is your next query using OR or AND searcher? [OR/AND] "))
        query = str(input("\tEnter your query: "))
        number_of_results = int(input("\t\tHow many results do you wish? "))
        results = []
        if or_and == "OR":
            results = indexer.search_documents_or(query, number_of_results)
        elif or_and == "AND":
            results = indexer.search_documents_and(query, number_of_results)
        else:
            quit()
        indexer.print_results(results)
        repeat = input("Do you wish to create another query? Y/N: ")
        if repeat != "Y":
            quit()
