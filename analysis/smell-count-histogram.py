import pandas as pd


def load_data(csv_file_path):
    df = pd.read_csv(csv_file_path)

    if 'Category' in df.columns:
        df['Category'] = df['Category'].astype(str).str.split('_').str[0]

    smell_columns = list(df.columns[3:])

    for col in smell_columns:
        df[col] = pd.to_numeric(df[col].replace('', 0).fillna(0), errors='coerce').fillna(0).astype(int)

    return df


def calculate_smell_histogram(df):
    smell_columns = list(df.columns[3:])
    module_smells = df.groupby('Module')[smell_columns].max()
    module_binary = (module_smells > 0).astype(int)

    smell_counts = module_binary.sum(axis=1)
    histogram = smell_counts.value_counts().sort_index()
    total_modules = len(smell_counts)

    result = {}
    for smell_count, module_count in histogram.items():
        percentage = (module_count / total_modules * 100) if total_modules > 0 else 0.0
        result[smell_count] = {'count': module_count, 'percentage': percentage}

    return result


def print_results(unverified_hist, verified_hist):
    all_counts = sorted(set(unverified_hist.keys()) | set(verified_hist.keys()))

    for smell_count in all_counts:
        unverified = unverified_hist.get(smell_count, {'count': 0, 'percentage': 0.0})
        verified = verified_hist.get(smell_count, {'count': 0, 'percentage': 0.0})

        print(f"{smell_count:>12d} {unverified['count']:>12d} {unverified['percentage']:>10.1f}% "
              f"{verified['count']:>12d} {verified['percentage']:>10.1f}%")


unverified_data = load_data("unverified-0107.csv")
verified_data = load_data("verified-0107.csv")

unverified_hist = calculate_smell_histogram(unverified_data)
verified_hist = calculate_smell_histogram(verified_data)

print_results(unverified_hist, verified_hist)
