import unittest
import csv
import sys
import tempfile
from Indexer import Indexer

# This class creates unit-test for searching, including multiple problematic scenarios
class TestIndexer(unittest.TestCase):

    # Sets up the indexer used in tests
    def setUp(self):
        csv.field_size_limit(sys.maxsize)
        self.indexer = Indexer()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.indexer.index_data('merged.tsv')

    # Cleaning after testing
    def tearDown(self):
        self.temp_dir.cleanup()

    # Unit test for query containing one attribute using OR searching function
    def test_search_documents_or_single_query(self):
        query = "Title:Aberrus"
        number_of_results = 1
        result = self.indexer.search_documents_or(query, number_of_results)
        expected_result = [(1, 'Aberrus Approach', 3.6552107334136963)]
        self.assertEqual(result, expected_result)

    # Unit test for query containing multiple attributes using OR operator and OR searching function
    def test_search_documents_or_multiple_query(self):
        query = "Title:Aberrus OR Paragraphs_content:Sarkareth OR Lists_content:Loot"
        number_of_results = 1
        result = self.indexer.search_documents_or(query, number_of_results)
        expected_result = [(1, 'Aberrus, the Shadowed Crucible: Sarkareth', 5.5987348556518555)]
        self.assertEqual(result, expected_result)

    # Unit test for inputting negative number of wanted documents using OR searching function
    def test_search_documents_or_negative_number_of_documents(self):
        query = "Title:Aberrus"
        number_of_results = -1
        result = self.indexer.search_documents_or(query, number_of_results)
        expected_result = None
        self.assertEqual(result, expected_result)

    # Unit test for multiple results of multiple attribute query using OR operator and OR searching function
    def test_search_documents_or_more_results(self):
        query = "Title:Sarkareth OR Wiki:Aberrus"
        number_of_results = 5
        result = self.indexer.search_documents_or(query, number_of_results)
        expected_result = [(1, 'Scalecommander Sarkareth', 6.411701202392578),
                           (2, 'Mythic: Scalecommander Sarkareth', 3.3069114685058594),
                           (3, 'Scalecommander Sarkareth (tactics)', 3.3069114685058594),
                           (4, 'Cutting Edge: Scalecommander Sarkareth', 2.8840832710266113),
                           (5, 'Aberrus, the Shadowed Crucible: Sarkareth', 2.557124614715576)]
        self.assertEqual(result, expected_result)

    # Unit test for inputting empty query using OR searching function
    def test_search_documents_or_empty_query(self):
        query = ""
        number_of_results = 1
        result = self.indexer.search_documents_or(query, number_of_results)
        expected_result = None
        self.assertEqual(result, expected_result)



    # Unit test for query containing one attribute using AND searching function
    def test_search_documents_and_single_query(self):
        query = "Title:Ysera"
        number_of_results = 1
        result = self.indexer.search_documents_and(query, number_of_results)
        expected_result = [(1, 'Ysera', 4.801149368286133)]
        self.assertEqual(result, expected_result)

    # Unit test for query containing multiple attributes using AND operator and AND searching function
    def test_search_documents_and_multiple_query(self):
        query = "Title:Ysera AND Paragraphs_content:green AND Lists_content:Eye"
        number_of_results = 1
        result = self.indexer.search_documents_and(query, number_of_results)
        expected_result = [(1, 'Ysera', 5.764826774597168)]
        self.assertEqual(result, expected_result)

    # Unit test for inputting negative number of wanted documents using AND searching function
    def test_search_documents_and_negative_number_of_documents(self):
        query = "Title:Aberrus"
        number_of_results = -1
        result = self.indexer.search_documents_and(query, number_of_results)
        expected_result = None
        self.assertEqual(result, expected_result)

    # Unit test for multiple results of multiple attribute query using AND operator and AND searching function
    def test_search_documents_and_more_results(self):
        query = "Title:Sarkareth AND Paragraphs_content:Aberrus"
        number_of_results = 5
        result = self.indexer.search_documents_and(query, number_of_results)
        expected_result = [(1, 'Scalecommander Sarkareth', 6.954096794128418),
                           (2, 'Mythic: Scalecommander Sarkareth', 6.670944690704346),
                           (3, 'Cutting Edge: Scalecommander Sarkareth', 6.1549763679504395),
                           (4, 'Scalecommander Sarkareth (tactics)', 5.999948978424072),
                           (5, 'Aberrus, the Shadowed Crucible: Sarkareth', 5.250162124633789)]
        self.assertEqual(result, expected_result)

    # Unit test for inputting empty query using AND searching function
    def test_search_documents_and_empty_query(self):
        query = ""
        number_of_results = 1
        result = self.indexer.search_documents_and(query, number_of_results)
        expected_result = None
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
