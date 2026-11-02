import html
import pandas as pd
from src.shared import RESULTS_DIR

def generate_report(runs, data_dir):
    # It runs one dict per worker count, sorted by workers
    # Each dict has "workers", "time_ms", and "csv" (path to that run's CSV)

    # labels.txt is CSV text with the columns filename,word
    labels_df = pd.read_csv(data_dir / "labels.txt")
    total_rows = len(labels_df)

    merged_df = labels_df
    for run in runs:
        run_df = pd.read_csv(run["csv"])
        run_df = run_df[['filename', 'text']].rename(columns={'text': f"text_{run['workers']}"})
        merged_df = merged_df.merge(run_df, on='filename', how='outer')

    # Speedup S = T1 / Tn, efficiency E = S / n
    baseline_time = runs[0]["time_ms"]
    for run in runs:
        run["speedup"] = baseline_time / run["time_ms"]
        run["efficiency"] = run["speedup"] / run["workers"]
        errors = (merged_df["word"] != merged_df[f"text_{run['workers']}"]).sum()
        run["accuracy"] = (total_rows - errors) / total_rows * 100 if total_rows else 0

    best = max(runs, key=lambda run: run["speedup"])

    # Speedup table, with the best worker count highlighted
    speed_rows = []
    for run in runs:
        style = ' style="background-color: #ccffcc; font-weight: bold;"' if run is best else ""
        speed_rows.append(
            f"<tr{style}><td>{run['workers']}</td><td>{run['time_ms']:.4f}</td>"
            f"<td>{run['speedup']:.4f}</td><td>{run['efficiency']:.4f}</td>"
            f"<td>{run['accuracy']:.2f}%</td></tr>"
        )

    def get_style(val, target):
        return ' style="background-color: #ffcccc; color: #900;"' if val != target else ""

    # Text table: one column per worker count, wrong words in red
    text_rows = []
    for _, row in merged_df.iterrows():
        target = row["word"]
        cells = "".join(
            f"<td{get_style(row[f'text_{run['workers']}'], target)}>"
            f"{html.escape(str(row[f'text_{run['workers']}']))}</td>"
            for run in runs
        )
        text_rows.append(
            f"<tr><td>{html.escape(str(row['filename']))}</td>"
            f"<td>{html.escape(str(target))}</td>{cells}</tr>"
        )

    worker_headers = "".join(f"<th>{run['workers']} workers</th>" for run in runs)

    html_content = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>Parallel OCR Pipeline Benchmark</title>
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
        <p>Baseline: 1 worker, {baseline_time:.4f} ms</p>
        <p>Best speedup: {best['workers']} workers ({best['speedup']:.4f}x)</p>
        <table>
            <thead>
                <tr><th>workers</th><th>time (ms)</th><th>speedup</th><th>efficiency</th><th>accuracy</th></tr>
            </thead>
            <tbody>
                {"".join(speed_rows)}
            </tbody>
        </table>

        <h1>Text Comparison Report</h1>
        <p>Total Samples: {total_rows:,}</p>
        <table>
            <thead>
                <tr><th>filename</th><th>text</th>{worker_headers}</tr>
            </thead>
            <tbody>
                {"".join(text_rows)}
            </tbody>
        </table>
    </body>
    </html>
    """

    output_path = RESULTS_DIR / "benchmark_report.html"
    output_path.write_text(html_content, encoding="utf-8")
    print(f"Report saved to: {output_path}")
    return output_path
