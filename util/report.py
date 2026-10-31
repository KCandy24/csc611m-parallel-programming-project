import html
import pandas as pd
from src.shared import RESULTS_DIR

def generate_report(st_time, mt_time, n_workers,  st_file, mt_file, data_dir):

    labels_path = data_dir / "labels.csv"
    st_path = RESULTS_DIR / (st_file + ".csv")
    mt_path = RESULTS_DIR / (mt_file + ".csv")

    labels_df = pd.read_csv(labels_path)
    st_df = pd.read_csv(st_path)
    mt_df = pd.read_csv(mt_path)

    st_df = st_df[['filename', 'text']].rename(columns={'text': 'st_text'})
    mt_df = mt_df[['filename', 'text']].rename(columns={'text': 'mt_text'})

    merged_df = (
        labels_df
            .merge(mt_df, on='filename', how='outer')
            .merge(st_df, on='filename', how='outer')
    )

    print(merged_df.head())

    total_rows = len(merged_df)


    st_errors = (merged_df["word"] != merged_df["st_text"]).sum()
    mt_errors = (merged_df["word"] != merged_df["mt_text"]).sum()

    st_err_pct = (st_errors / total_rows * 100) if total_rows else 0
    mt_err_pct = (mt_errors / total_rows * 100) if total_rows else 0

    def get_style(val, target):
        return ' style="background-color: #ffcccc; color: #900;"' if val != target else ""

    rows = []
    for _, row in merged_df.iterrows():
        fname = html.escape(str(row["filename"]))
        word = html.escape(str(row["word"]))
        st_text = html.escape(str(row["st_text"]))
        mt_text = html.escape(str(row["mt_text"]))

        target = row["word"]

        st_style = get_style(row["st_text"], target)
        mt_style = get_style(row["mt_text"], target)    

        rows.append(
            f"<tr><td>{fname}</td><td>{word}</td><td{st_style}>{st_text}</td><td{mt_style}>{mt_text}</td></tr>"
        )

    tbody = "\n".join(rows)

    table_html = f"""
    <table>
        <thead>
            <tr>
                <th>filename</th>
                <th>text</th>
                <th>st_text</th>
                <th>mt_text</th>
            </tr>
        </thead>
        <tbody>
            {tbody}
        </tbody>
    </table>
    """

    speedup = st_time / mt_time
    efficiency = speedup / n_workers

    html_content = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>Parallel OCR Pipeline Report</title>
    <style>
        table, th, td {{
            border: 1px solid black;
            border-collapse: collapse;
            padding: 6px 10px;
        }}
    </style>
    </head>
    <body>
        <h1>Speedup and Efficiency</h1>
        <div>
            <p>Single Thread Time(ms): {st_time:.4f}</p>
            <p>{n_workers} Threads Time(ms): {mt_time:.4f}</p>
            <p>Speedup: {speedup:.4f}</p>
            <p>Efficiency: {efficiency:.4f}</p>
        </div>


        <h1>Text Comparison Report</h1>

        <div>
            <p>Total Samples: {total_rows:,}</p>
            <p>Single Thread Errors: {st_errors:,} ({st_err_pct:.1f}%), {(total_rows - st_errors)/ total_rows * 100 :.2f}% Accurate</p>
            <p>Multi Thread Errors: {mt_errors:,} ({mt_err_pct:.1f}%), {(total_rows - mt_errors)/ total_rows * 100 :.2f}% Accurate</p>
        </div>
        {table_html}
    </body>
    </html>
    """

    output_path = RESULTS_DIR / f"report_{n_workers}_threads.html"
    output_path.write_text(html_content, encoding="utf-8")
    print(f"Report saved to: {RESULTS_DIR.resolve()}")
        
    