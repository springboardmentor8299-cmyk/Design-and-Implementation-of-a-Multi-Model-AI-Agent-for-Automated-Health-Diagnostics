from extractor import extract_parameters
from pipeline import run_analysis
from text_extractor import extract_text   # your first OCR code

file_path = input("Enter report file path: ")

# STEP 1 — Extract raw text
text = extract_text(file_path)

# STEP 2 — Run analysis pipeline
results = run_analysis(text)

# STEP 3 — Print results
print("\n--- PARAMETERS ---")
print(results["parameters"])

print("\n--- ANALYSIS ---")
print(results["analysis"])

print("\n--- RISKS ---")
print(results["risks"])

print("\n--- RECOMMENDATIONS ---")
for r in results["recommendations"]:
    print("-", r)
