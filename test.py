import json, glob, os
comparison_results_files = glob.glob('data/comparison_results_*.json')

print(f"Looking for comparison results files...")
print(f"Found {len(comparison_results_files)} comparison result files")

if comparison_results_files:
	latest_comparison_file = max(comparison_results_files, key=os.path.getctime)
	print(f"✓ Using existing comparison results from: {latest_comparison_file}")
	print(f"✓ Skipping comparison step - results already exist")