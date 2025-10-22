import pandas as pd


def load_data(csv_file_path):
    df = pd.read_csv(csv_file_path)

    if 'Category' in df.columns:
        df['Category'] = df['Category'].astype(str).str.split('_').str[0]

    smell_columns = list(df.columns[3:])

    for col in smell_columns:
        df[col] = pd.to_numeric(df[col].replace('', 0).fillna(0), errors='coerce').fillna(0).astype(int)

    return df


def calculate_smell_by_category(df):
    smell_columns = list(df.columns[3:])
    module_groups = df.groupby(['Module', 'Category'])[smell_columns].max().reset_index()

    results = {}

    for category in ['High', 'Medium', 'Low']:
        category_data = module_groups[module_groups['Category'].str.lower() == category.lower()]
        binary_data = (category_data[smell_columns] > 0).astype(int)
        total_modules = len(binary_data)

        results[category] = {}
        for smell in smell_columns:
            count = binary_data[smell].sum()
            percentage = (count / total_modules * 100) if total_modules > 0 else 0.0
            results[category][smell] = {'count': count, 'percentage': percentage}

    return results


def print_results(results):
    all_smells = sorted(set().union(*[r.keys() for r in results.values()]))

    for smell in all_smells:
        high = results.get('High', {}).get(smell, {'count': 0, 'percentage': 0.0})
        medium = results.get('Medium', {}).get(smell, {'count': 0, 'percentage': 0.0})
        low = results.get('Low', {}).get(smell, {'count': 0, 'percentage': 0.0})

        print(f"{smell:<45} {high['count']:>8d} {high['percentage']:>6.1f}% "
              f"{medium['count']:>8d} {medium['percentage']:>6.1f}% "
              f"{low['count']:>8d} {low['percentage']:>6.1f}%")


csv_file = "unverified-0107.csv"

data = load_data(csv_file)
results = calculate_smell_by_category(data)
print_results(results)
