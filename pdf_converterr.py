# Lightweight, self-contained PDFConverter implementation for tests
import re
import pandas as pd
from pathlib import Path

class PDFConverter:
    """Minimal implementation providing the methods used by the tests.
    This keeps the project self-contained and focused for unit tests.
    """

    date_re = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})")
    code_re = re.compile(r"(\d{2} \d{2} \d{2})")

    def _clean_sheets_inplace(self, excel_path: str):
        p = Path(excel_path)
        # read all sheets and rewrite cleaned sheets in place
        with pd.ExcelFile(p) as x:
            sheets = {name: x.parse(name, header=None) for name in x.sheet_names}

        for name, df in sheets.items():
            df = df.fillna("")
            # find header row (first few rows containing 'Date')
            header_idx = None
            for i in range(min(6, len(df))):
                if df.iloc[i].astype(str).str.contains('Date').any():
                    header_idx = i
                    break
            if header_idx is None:
                # nothing to do for this sheet
                sheets[name] = df
                continue
            header = df.iloc[header_idx].astype(str).tolist()
            body = df.iloc[header_idx+1:].copy()
            body.columns = header
            # extract dates from Description into Date column when missing
            if 'Date' in body.columns and 'Description' in body.columns:
                for idx in body.index:
                    date_val = str(body.at[idx, 'Date']).strip()
                    desc = str(body.at[idx, 'Description'])
                    if (not date_val) or date_val == 'nan':
                        m = self.date_re.search(desc)
                        if m:
                            body.at[idx, 'Date'] = m.group(1)
            # write back with header row as a proper first row (no header in written sheet)
            header_row = pd.DataFrame([dict(zip(header, header))])
            new_df = pd.concat([header_row, body.reset_index(drop=True)], ignore_index=True)
            sheets[name] = new_df

        # save back to the same file
        with pd.ExcelWriter(p, engine='openpyxl') as w:
            for name, df in sheets.items():
                df.to_excel(w, sheet_name=name, index=False, header=False)

    def _consolidate_sheets(self, raw_path: str, consolidated_path: str):
        raw = Path(raw_path)
        with pd.ExcelFile(raw) as x:
            out_rows = []
            for name in x.sheet_names:
                df = x.parse(name, header=None).fillna("")
                # find header row
                header_idx = None
                for i in range(min(6, len(df))):
                    if df.iloc[i].astype(str).str.contains('Code').any():
                        header_idx = i
                        break
                if header_idx is None:
                    continue
                header = df.iloc[header_idx].astype(str).tolist()
                body = df.iloc[header_idx+1:].copy()
                body.columns = header
                out_rows.append(body[['Code','Description']])
            if out_rows:
                result = pd.concat(out_rows, ignore_index=True)
            else:
                result = pd.DataFrame(columns=['Code','Description'])
        out = Path(consolidated_path)
        with pd.ExcelWriter(out, engine='openpyxl') as w:
            result.to_excel(w, sheet_name='Consolidated_6_21', index=False)

    def _parse_sections_and_finalize(self, consolidated_in: str, out_path: str):
        inp = Path(consolidated_in)
        with pd.ExcelFile(inp) as x:
            df = x.parse('Consolidated_6_21')
        df = df.fillna('')
        # fill Code from Description when missing
        for idx in df.index:
            if not str(df.at[idx, 'Code']).strip():
                m = self.code_re.search(str(df.at[idx, 'Description']))
                if m:
                    df.at[idx, 'Code'] = m.group(1)
        # split Code into Section/Subsection/Item
        parts = df['Code'].astype(str).str.split(' ', expand=True)
        df['Section'] = parts.get(0, '')
        df['Subsection'] = parts.get(1, '')
        df['Item'] = parts.get(2, '')
        outp = Path(out_path)
        with pd.ExcelWriter(outp, engine='openpyxl') as w:
            df.to_excel(w, sheet_name='All_Sections', index=False)

    def _dedupe_and_trim(self, inp: str, outp: str):
        p = Path(inp)
        with pd.ExcelFile(p) as x:
            df = x.parse('All_Sections')
        df = df.drop_duplicates()
        # remove Source and Category if present
        for col in ('Source','Category'):
            if col in df.columns:
                df = df.drop(columns=[col])
        out = Path(outp)
        with pd.ExcelWriter(out, engine='openpyxl') as w:
            df.to_excel(w, sheet_name='All_Sections', index=False)


if __name__ == '__main__':
    # quick smoke test
    print('PDFConverter module loaded')
