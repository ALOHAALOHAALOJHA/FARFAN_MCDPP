import json
import pandas as pd
from collections import Counter

# Load the JSON file
with open('canonic_questionnaire_central/questionnaire_monolith.json', 'r') as f:
    data = json.load(f)

# Extract micro_questions
micro_questions = data.get('blocks', {}).get('micro_questions', [])

# Create a list of (question_id, method_class, method_function) tuples
method_mappings = []
for question in micro_questions:
    question_id = question.get('question_id')
    policy_area_id = question.get('policy_area_id')
    method_sets = question.get('method_sets', [])
    for method in method_sets:
        method_class = method.get('class')
        method_function = method.get('function')
        method_mappings.append((question_id, policy_area_id, method_class, method_function))

# Create a DataFrame
df = pd.DataFrame(method_mappings, columns=['question_id', 'policy_area_id', 'class', 'function'])
df['method'] = df['class'] + '.' + df['function']

# --- Analysis ---

# 1. Method Frequency
method_counts = df['method'].value_counts().reset_index()
method_counts.columns = ['method', 'count']
print("--- Method Frequency ---")
print(method_counts.to_string())
print("\n")

# 2. Class Frequency
class_counts = df['class'].value_counts().reset_index()
class_counts.columns = ['class', 'count']
print("--- Class Frequency ---")
print(class_counts.to_string())
print("\n")

# 3. Methods per Policy Area
methods_per_pa = df.groupby('policy_area_id')['method'].nunique().reset_index()
methods_per_pa.columns = ['policy_area_id', 'unique_method_count']
print("--- Unique Methods per Policy Area ---")
print(methods_per_pa.to_string())
print("\n")

# 4. Top methods per Policy Area
top_methods_per_pa = df.groupby(['policy_area_id', 'method']).size().reset_index(name='count')
top_methods_per_pa = top_methods_per_pa.sort_values(['policy_area_id', 'count'], ascending=[True, False])
print("--- Top Methods per Policy Area ---")
# Using a for loop to print each group separately for better readability
for pa_id, group in top_methods_per_pa.groupby('policy_area_id'):
    print(f"Policy Area: {pa_id}")
    print(group.head(5).to_string(index=False))
    print("\n")

# Save to file for later use in the audit report
method_counts.to_csv('method_frequency.csv', index=False)
class_counts.to_csv('class_frequency.csv', index=False)
methods_per_pa.to_csv('methods_per_pa.csv', index=False)
top_methods_per_pa.to_csv('top_methods_per_pa.csv', index=False)

print("Analysis complete. Results saved to CSV files.")
