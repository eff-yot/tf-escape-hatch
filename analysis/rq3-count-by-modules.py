import pandas as pd


def load_data(csv_file_path):
    df = pd.read_csv(csv_file_path)

    if 'Category' in df.columns:
        df['Category'] = df['Category'].astype(str).str.split('_').str[0]

    smell_columns = list(df.columns[3:])

    for col in smell_columns:
        df[col] = pd.to_numeric(df[col].replace('', 0).fillna(0), errors='coerce').fillna(0).astype(int)

    return df


def calculate_smell_prevalence(df):
    smell_columns = list(df.columns[3:])
    module_smells = df.groupby('Module')[smell_columns].max()
    module_binary = (module_smells > 0).astype(int)
    total_modules = len(module_binary)

    prevalence = {}
    for smell in smell_columns:
        count = module_binary[smell].sum()
        percentage = (count / total_modules * 100) if total_modules > 0 else 0.0
        prevalence[smell] = {'count': count, 'percentage': percentage}

    return prevalence, total_modules


def print_results(unverified_prev, verified_prev):
    all_smells = sorted(set(unverified_prev.keys()) | set(verified_prev.keys()))

    for smell in all_smells:
        unverified = unverified_prev.get(smell, {'count': 0, 'percentage': 0.0})
        verified = verified_prev.get(smell, {'count': 0, 'percentage': 0.0})

        print(f"{smell:<45} {unverified['count']:>8d} {unverified['percentage']:>6.1f}% "
              f"{verified['count']:>8d} {verified['percentage']:>6.1f}%")


unverified_data = load_data("unverified-0107.csv")
verified_data = load_data("verified-0107.csv")

unverified_prev, unverified_total = calculate_smell_prevalence(unverified_data)
verified_prev, verified_total = calculate_smell_prevalence(verified_data)

print_results(unverified_prev, verified_prev)
