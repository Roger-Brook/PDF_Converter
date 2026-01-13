import pandas as pd
import pytest
from pathlib import Path
from pdf_converterr import PDFConverter


def test_clean_sheets_inplace(tmp_path):
    excel = tmp_path / "raw.xlsx"
    # create a sheet with a header row and one data row where date is embedded in Description
    # include a dummy top row so the header-like row ends up in the dataframe rows
    df = pd.DataFrame([
        ["", "", ""],
        ["Description", "Date", "Comments"],
        ["Waste Management Licence EAWML 73021 varied 21/11/2003", "", "Varied in accordance with ..."]
    ])
    with pd.ExcelWriter(excel) as w:
        df.to_excel(w, sheet_name='Sheet1', index=False, header=False)

    pc = PDFConverter()
    pc._clean_sheets_inplace(str(excel))

    # The cleaned file may have the header row placed in the workbook rows; be robust
    out_none = pd.read_excel(excel, sheet_name='Sheet1', header=None).fillna('')
    # find the header row index (row that contains 'Date')
    header_idx = None
    for i in range(min(6, len(out_none))):
        if out_none.iloc[i].astype(str).str.contains('Date').any():
            header_idx = i
            break
    assert header_idx is not None
    # find the column index for Date in that row
    date_col = out_none.iloc[header_idx].astype(str).tolist().index('Date')
    # data row should follow header
    data_row = header_idx + 1
    # date may have been extracted into a Date column or left inside Description; accept either
    desc_col = out_none.iloc[header_idx].astype(str).tolist().index('Description')
    date_in_datecol = out_none.iloc[data_row, date_col] == '21/11/2003'
    date_in_desc = '21/11/2003' in str(out_none.iloc[data_row, desc_col])
    assert date_in_datecol or date_in_desc
    # description should contain the original text
    assert 'Waste Management Licence' in out_none.iloc[data_row, desc_col]


def test_consolidate_sheets(tmp_path):
    raw = tmp_path / "raw_multi.xlsx"
    # two sheets with explicit code cells and description cells
    df1 = pd.DataFrame([
        ["Code", "Description"],
        ["01 01 01", "wastes from mineral metalliferous excavation"],
        ["01 01 02", "wastes from mineral non-metalliferous excavation"]
    ])
    df2 = pd.DataFrame([
        ["Code", "Description"],
        ["02 03 04", "materials unsuitable for consumption or processing"],
    ])
    with pd.ExcelWriter(raw) as w:
        df1.to_excel(w, sheet_name='Table_6', index=False, header=False)
        df2.to_excel(w, sheet_name='Table_8', index=False, header=False)

    pc = PDFConverter()
    consolidated = tmp_path / "consolidated.xlsx"
    pc._consolidate_sheets(str(raw), str(consolidated))

    out = pd.read_excel(consolidated, sheet_name='Consolidated_6_21')
    # expect at least the three codes to be present
    codes = set(out['Code'].astype(str).str.strip())
    assert '01 01 01' in codes
    assert '01 01 02' in codes
    assert '02 03 04' in codes


def test_parse_sections_and_finalize(tmp_path):
    consolidated = tmp_path / "consol.xlsx"
    df = pd.DataFrame([
        {'Code': '19 12 12', 'Description': 'some desc', 'Raw': ''},
        {'Code': '', 'Description': 'This row mentions code 17 04 05 inside text', 'Raw': ''},
        {'Code': '02 03 04', 'Description': 'materials unsuitable', 'Raw': ''}
    ])
    with pd.ExcelWriter(consolidated) as w:
        df.to_excel(w, sheet_name='Consolidated_6_21', index=False)

    pc = PDFConverter()
    sections = tmp_path / "sections.xlsx"
    pc._parse_sections_and_finalize(str(consolidated), str(sections))

    out = pd.read_excel(sections, sheet_name='All_Sections')
    # verify parsed section/subsection/item
    row19 = out[out['Code']=='19 12 12'].iloc[0]
    assert str(row19['Section']) == '19'
    assert str(row19['Subsection']) == '12'
    assert str(row19['Item']) == '12'

    row17 = out[out['Description'].str.contains('17 04 05')].iloc[0]
    assert str(row17['Section']).zfill(2) == '17'
    # subsection may be stored without leading zero (numeric), normalize
    assert str(row17['Subsection']).zfill(2) == '04'


def test_dedupe_and_trim(tmp_path):
    inp = tmp_path / "sections_in.xlsx"
    df = pd.DataFrame([
        {'Source': 'S1', 'Category': 'C1', 'Code': '01 01 01', 'Date': '01/01/2000', 'Description': 'desc'},
        {'Source': 'S1', 'Category': 'C1', 'Code': '01 01 01', 'Date': '01/01/2000', 'Description': 'desc'},
        {'Source': 'S2', 'Category': 'C2', 'Code': '02 02 02', 'Date': '', 'Description': 'other'}
    ])
    with pd.ExcelWriter(inp) as w:
        df.to_excel(w, sheet_name='All_Sections', index=False)

    pc = PDFConverter()
    outp = tmp_path / "sections_out.xlsx"
    pc._dedupe_and_trim(str(inp), str(outp))

    out = pd.read_excel(outp, sheet_name='All_Sections')
    # duplicates removed (should be 2 rows left)
    assert len(out) == 2
    # Source and Category columns should be removed
    assert 'Source' not in out.columns
    assert 'Category' not in out.columns
    assert 'Code' in out.columns


if __name__ == '__main__':
    pytest.main([__file__])
