from extractor import run_extraction
from model1 import interpret_parameters

file_path = input("Enter file path: ")

data = run_extraction(file_path, "TEST001")

print("\n========== EXTRACTED DATA ==========\n")

for k, v in sorted(data.items()):
    if v is not None:
        print(f"{k:<25} : {v}")

# ---------- RUN MODEL 1 ----------
analysis = interpret_parameters(data)

print("\n========== ANALYSIS ==========\n")

for param, info in sorted(analysis.items()):
    print(f"{param:<25} : {info['value']} → {info['status']} (Normal: {info['range']})")
