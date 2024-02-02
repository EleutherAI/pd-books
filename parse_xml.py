from lxml import etree
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from dateutil import parser
import fire


def parse_copyrightentry(
    entry: etree.Element, group_author: str | None = None, cutoff_year: int = 1964
) -> dict | None:
    # TODO: Duplicate and partOf fields
    """Parses the copyrightEntry element. Returns None if a correctly parsed date >= cutoff_year"""
    # "regnum" (attribute) is standardized "regNum" (text) (latter is verbatim)
    tag_data = {
        "id": entry.get("id"),
        "regnum": entry.get("regnum"),
    }
    tags = [
        "author/authorName",
        "title",
        "publisher/pubName",
        "publisher/pubPlace",
        "regDate",
        "regNum",
        "prevPub",
        "prev-regNum",
        "edition",
    ]
    for tag_name in tags:
        tag_elements = entry.xpath(".//" + tag_name)
        if tag_elements:
            tag_element = tag_elements[0]
            tag_text = tag_element.text
            if tag_name == "regDate":
                try:
                    if parser.parse(tag_element.attrib.get("date")).year >= cutoff_year:
                        return None
                except:
                    print(f"Date not Parsed: {tag_element.attrib.get('date')}")
                tag_data |= dict(tag_element.attrib)
            if tag_text is not None:
                tag_data[tag_element.tag] = tag_text
    # if the copyrightEntry is inside group then authorName is provided in parent class
    tag_data["authorName"] = tag_data.get("authorName", group_author)
    return tag_data


def parse_xml_file(FILE_PATH: str | Path) -> list[dict] | None:
    """Parses a single XML file"""
    try:
        root = etree.parse(FILE_PATH)
    except Exception as e:
        print(f"Failed to parse {FILE_PATH}: {e}")
        return None
    root = root.getroot()
    # Extract copyrightEntry elements
    extracted_data = []

    # Get metadata
    header = root.find(".//header")
    meta_data = {
        "year": int(header.find(".//year").text),
        "volume": int(header.find(".//volume").text),
        "part": header.find(".//part").text,
        "page": None,
    }

    for element in root:
        if element.tag == "page":
            meta_data["page"] = element.get("pgnum")
        # Extract data
        if element.tag == "entryGroup":
            # copyrightEntries can be grouped together
            # TODO: Some (might) have an `ignore` attrib. Verify
            group_author_elements = element.xpath(".//author/authorName")
            group_author = (
                group_author_elements[0].text if group_author_elements else None
            )
            for child in element:
                if child.tag == "copyrightEntry":
                    if (
                        extracted := parse_copyrightentry(child, group_author)
                    ) is not None:
                        # for incase date <= cutoff_year
                        extracted_data.append(meta_data | extracted)
        elif element.tag == "copyrightEntry":
            if (extracted := parse_copyrightentry(element)) is not None:
                extracted_data.append(meta_data | extracted)
    return extracted_data


def parse_dir(input_path: str, output_path: str) -> None:
    """Parses `dir_path` recursively for xml files and writes the entries to `output_path` (parquet)"""
    input_path: Path = Path(input_path)
    # Initialize an empty DataFrame to store all entries
    all_entries_df = pd.DataFrame()
    for file_path in tqdm(list(input_path.glob("**/*.xml")), desc="Parsing XML"):
        processed_entries = parse_xml_file(file_path)
        if processed_entries:
            print(f"{file_path.name} has {len(processed_entries)}")
            entries_df = pd.DataFrame(processed_entries)
            all_entries_df = pd.concat(
                [all_entries_df, entries_df], ignore_index=True, sort=False
            )
    all_entries_df.to_parquet(output_path, index=False)


if __name__ == "__main__":
    # Download path of xml folder: https://github.com/NYPL/catalog_of_copyright_entries_project/tree/master/xml
    # "/Users/baber/PycharmProjects/catalog_of_copyright_entries_project/xml"
    fire.Fire(parse_dir)
