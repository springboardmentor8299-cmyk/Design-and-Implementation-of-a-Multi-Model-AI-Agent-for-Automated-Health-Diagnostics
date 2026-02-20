import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from pdf_parser import PdfParser
from component_extractor import ComponentExtractor


class BloodComponentAnalyzerGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Blood Component Analyzer")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f0f0")

        # ---------------- STYLE ----------------

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton", font=("Helvetica", 10))
        style.configure("TLabel", font=("Helvetica", 10), background="#f0f0f0")

        style.configure("Title.TLabel",
                        font=("Helvetica", 18, "bold"),
                        background="#f0f0f0")

        # ---------------- NORMAL RANGES ----------------
        # Added RBC and WBC

        self.normal_ranges = {
            "Hemoglobin": (12, 16),
            "Glucose": (80, 140),
            "Cholesterol": (0, 200),
            "RBC": (4.0, 6.0),        # in million cells/mcL
            "WBC": (4000, 11000),     # cells/mcL
        }

        # ---------------- MAIN FRAME ----------------

        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill="both", expand=True)

        # ---------------- TITLE ----------------

        title_label = ttk.Label(
            main_frame,
            text="Blood Component Analyzer",
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 20))

        # ---------------- FILE FRAME ----------------

        file_frame = ttk.LabelFrame(
            main_frame,
            text="Step 1: Select PDF File",
            padding="10"
        )
        file_frame.pack(fill="x", pady=(0, 15))

        self.file_path_var = tk.StringVar(value="No file selected")

        file_path_label = ttk.Label(
            file_frame,
            textvariable=self.file_path_var,
            foreground="gray"
        )
        file_path_label.pack(side="left", fill="x", expand=True)

        browse_button = ttk.Button(
            file_frame,
            text="Browse",
            command=self.browse_file
        )
        browse_button.pack(side="right")

        # ---------------- RESULTS FRAME ----------------

        results_frame = ttk.LabelFrame(
            main_frame,
            text="Step 2: Extracted Blood Components",
            padding="10"
        )
        results_frame.pack(fill="both", expand=True)

        columns = ("Component", "Level", "Status")

        self.tree = ttk.Treeview(
            results_frame,
            columns=columns,
            height=15,
            show="headings"
        )

        self.tree.heading("Component", text="Component")
        self.tree.heading("Level", text="Level Value")
        self.tree.heading("Status", text="Status")

        self.tree.column("Component", width=250)
        self.tree.column("Level", width=150)
        self.tree.column("Status", width=150)

        scrollbar = ttk.Scrollbar(
            results_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---------------- BUTTON FRAME ----------------

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)

        analyze_button = ttk.Button(
            button_frame,
            text="Analyze PDF",
            command=self.analyze_pdf
        )
        analyze_button.pack(side="left", padx=5)

        clear_button = ttk.Button(
            button_frame,
            text="Clear Results",
            command=self.clear_results
        )
        clear_button.pack(side="left", padx=5)

        # ---------------- STATUS BAR ----------------

        self.status_var = tk.StringVar(value="Ready")

        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief="sunken",
            foreground="green"
        )
        status_bar.pack(fill="x")

        # ---------------- OBJECTS ----------------

        self.pdf_parser = PdfParser()
        self.component_extractor = ComponentExtractor()
        self.selected_file = None

    # ---------------- FILE BROWSER ----------------

    def browse_file(self):

        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf")]
        )

        if file_path:
            self.selected_file = file_path
            self.file_path_var.set(file_path)
            self.status_var.set("File selected successfully")

    # ---------------- STATUS DETECTOR ----------------

    def get_status(self, component, value):

        try:
            value = float(value)
        except:
            return "Invalid"

        if component not in self.normal_ranges:
            return "Unknown"

        low, high = self.normal_ranges[component]

        if value < low:
            return "Low"
        elif value > high:
            return "High"
        else:
            return "Normal"

    # ---------------- ANALYZE PDF ----------------

    def analyze_pdf(self):

        if not self.selected_file:
            messagebox.showwarning(
                "Warning",
                "Please select a PDF file first"
            )
            return

        try:
            self.status_var.set("Analyzing PDF...")
            self.root.update()

            text = self.pdf_parser.parse_pdf(self.selected_file)
            components = self.component_extractor.extract_components(text)

            self.clear_results()

            if not components:
                messagebox.showinfo(
                    "Info",
                    "No components found"
                )
                return

            for component, level in components.items():
                status = self.get_status(component, level)

                self.tree.insert(
                    "",
                    "end",
                    values=(component, level, status)
                )

            self.status_var.set("Analysis completed successfully")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error occurred")

    # ---------------- CLEAR ----------------

    def clear_results(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        self.status_var.set("Results cleared")


# ---------------- MAIN ----------------

def main():

    root = tk.Tk()
    app = BloodComponentAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
