from lxml import etree
import pandas as pd
from pathlib import Path
from tqdm import tqdm


def parse_xml_file(file_path):
    def process_element(element):
        if element.tag == 'regDate':
            return element.get('date')  # Get the 'date' attribute
        # If the element has children, recursively return a dict of its children
        if len(element):
            return {child.tag: process_element(child) for child in element}
        # If the element has no children, return its text
        return element.text

    tree = etree.parse(file_path)
    root = tree.getroot()
    processed_entries = []
    for child in root:
        if child.tag == "entryGroup":
            group_author = child.findtext('author/authorName', default="")
            for entry in child.findall('copyrightEntry'):
                entry_data = {subchild.tag: process_element(subchild) for subchild in entry}
                entry_data['groupAuthor'] = group_author
                processed_entries.append(entry_data)
        elif child.tag == 'copyrightEntry':
            entry_data = {subchild.tag: process_element(subchild) for subchild in child}
            entry_data.update(child.attrib)
            if child.getparent().tag != 'entryGroup':
                processed_entries.append(entry_data)
    return processed_entries


if __name__ == "__main__":
    # path to xml folder from https://github.com/NYPL/catalog_of_copyright_entries_project/tree/master/xml
    DIR_PATH = Path("xml")
    # Initialize an empty DataFrame to store all entries
    all_entries_df = pd.DataFrame()
    for file_path in tqdm(list(DIR_PATH.glob('**/*.xml')), desc="Parsing XML"):
        processed_entries = parse_xml_file(file_path)

        entries_df = pd.DataFrame(processed_entries)
        all_entries_df = pd.concat([all_entries_df, entries_df], ignore_index=True, sort=False)
    all_entries_df.to_csv("combined.csv", index=False)
