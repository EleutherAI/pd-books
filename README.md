# PD-Books

This repo holds the WIP code for  matching and analyzing datasets of copyright submissions and renewals based on the excellent work done by The New York Public Library (NYPL).

# Tips

The datasets have been converted to HF datasets: [registrations](https://huggingface.co/datasets/baber/NYPL_entries), [renewals](https://huggingface.co/datasets/baber/cce-renewals).

The registration data has been parsed from xml files with this [script](parse_xml.py). To replicate clone [this](https://github.com/NYPL/catalog_of_copyright_entries_project) repo (or download the `xml` folder) and call:
```bash
python ./parse_xml.py --input_path <path_to_xml_folder> --output_path <output.parquet>
```
The renewals dataset, [available](https://github.com/NYPL/cce-renewals) in tab-delimited format, has been aggregated and uploaded as well.

Some exploratory analysis and preliminary results [here](preliminary_analysis.ipynb).
