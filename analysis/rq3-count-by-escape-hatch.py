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

    module_groups = df.groupby(['Module', 'Provisioner'])[smell_columns].max().reset_index()

    results = {}
    totals = module_groups['Provisioner'].value_counts().to_dict()

    for provisioner in module_groups['Provisioner'].unique():
        provisioner_data = module_groups[module_groups['Provisioner'] == provisioner]
        binary_data = (provisioner_data[smell_columns] > 0).astype(int)
        total_modules = len(binary_data)

        results[provisioner] = {}
        for smell in smell_columns:
            count = binary_data[smell].sum()
            percentage = (count / total_modules * 100) if total_modules > 0 else 0.0
            results[provisioner][smell] = {'count': count, 'percentage': percentage}

    return results, totals


def print_results(results, totals):
    provisioners = sorted(results.keys())
    all_smells = sorted(set().union(*[r.keys() for r in results.values()]))

    for smell in all_smells:
        row = f"{smell:<45}"
        for provisioner in provisioners:
            data = results.get(provisioner, {}).get(smell, {'count': 0, 'percentage': 0.0})
            row += f" {data['count']:>8d} {data['percentage']:>6.1f}%"
        print(row)


csv_file = "unverified-0107.csv"

data = load_data(csv_file)
results, totals = calculate_smell_prevalence(data)
print_results(results, totals)
