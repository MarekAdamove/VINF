import pandas as pd
import re
import os

# Merges the parsed data and wiki data
if __name__ == "__main__":
    print("Merging...")
    # Reads parsed data into pandas dataframe
    parsed_data = pd.read_csv("parsed.tsv", sep="\t", encoding="utf-8")

    # Initiates new "Wiki" column where data from wiki will be saved
    parsed_data["Wiki"] = ""

    # List of all files extracted from wiki
    wiki_data_filenames = os.listdir("wiki_parsed")

    for filename in wiki_data_filenames:
        # Opens file regarding some entity
        wiki_file = open(f"wiki_parsed/{filename}", encoding="utf-8")
        wiki_file_data = wiki_file.read()

        # Looking for entity ID in the file and its cleaning from now useless characters and IDs
        entity = re.search(r"\[\[([^\]]+?)\]\]", wiki_file_data, flags=re.I | re.M | re.DOTALL)
        wiki_file_data = re.sub(r"\[\[[^\]]+?\]\]", "", wiki_file_data, flags=re.I | re.M | re.DOTALL)
        wiki_file_data = re.sub(r"\n|\t|\r", "", wiki_file_data, flags=re.I | re.M | re.DOTALL)

        # Appends new information to the dataframe
        parsed_data.loc[parsed_data["Title"] == entity.groups()[0], "Wiki"] = wiki_file_data

    # Export dataframe to file
    parsed_data.to_csv("merged.tsv", sep='\t', encoding="utf-8", index=False)
    print("Merging complete.")