import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.formula import ArrayFormula  # Required to prevent the '@' prefix

def write_stocks_side_by_side(
    csv_path: str,
    output_excel_path: str,
    start_date_df: list,
    end_date: str = "2024-12-31",
):
    """Reads stock metadata from a CSV and places dynamic =STOCKHISTORY formulas

    side-by-side on a single master Excel worksheet without the '@' operator.
    """
    row_nb = 0
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Source CSV not found: '{csv_path}'")

    # 1. Read Ticker CSV
    df = pd.read_csv(csv_path)
    cols_lower = {col.lower(): col for col in df.columns}
    if "symbol" not in cols_lower:
        raise ValueError("Input CSV must contain a 'symbol' column.")
    symbol_col = cols_lower["symbol"]

    # 2. Initialize openpyxl Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Stock History Side-by-Side"
    ws.views.sheetView[0].showGridLines = True

    # Define Header Styling
    banner_fill = PatternFill(
        start_color="1F4E78", end_color="1F4E78", fill_type="solid"
    )
    banner_font = Font(name="Calibri", size=12, bold=True, color="FFFFFF")

    # 3. Iterate through Tickers and space formulas across columns
    col_idx = 1
    for _, row in df.iterrows():
        raw_symbol = str(row[symbol_col]).strip()
        if not raw_symbol or raw_symbol.lower() == "nan":
            continue

        # Get column letters for the ticker block (e.g., A, B, C for 3-column block)
        start_col_letter = get_column_letter(col_idx)

        # Handle potential missing/NaN IPO years safely
        start_year = start_date_df[row_nb]
        row_nb += 1
        
        if pd.isna(start_year):
            start_date_str = "2020-01-01"  # Fallback year if empty
        else:
            start_date_str = f"{int(start_year) + 1}-01-01"

        # Construct the formula string
        formula_string = f'=STOCKHISTORY("{raw_symbol}", "{start_date_str}", "{end_date}", 0, 1, 0, 1, 3)'
        
        # Define the target cell coordinate (e.g., "A2", "E2", "I2")
        cell_coordinate = f"{start_col_letter}1"
        
        # Inject using ArrayFormula to tell Excel it's a dynamic array formula
        ws[cell_coordinate] = ArrayFormula(cell_coordinate, formula_string)

        # Advance column index for the next stock (3 data columns + 1 spacer column)
        col_idx += 3

    # 4. Auto-fit column widths using column indices
    for c in range(1, col_idx):
        col_letter = get_column_letter(c)
        ws.column_dimensions[col_letter].width = 15

    # 5. Save Workbook
    out_dir = os.path.dirname(output_excel_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    wb.save(output_excel_path)
    print(
        f"Successfully created side-by-side stock history sheet: '{output_excel_path}'"
    )

# --- Execution ---
csv_file_path = "Data/Stock_data_shorter.csv"

# Load the IPO year series
ipo_year_series = pd.read_csv(csv_file_path)['ipoyear']

# Generate the spreadsheet
write_stocks_side_by_side(
    csv_path=csv_file_path,
    output_excel_path="Stock_History_Formulas.xlsx",
    start_date_df=list(ipo_year_series),
    end_date="2026-11-01",
)
