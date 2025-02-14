import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
from datetime import datetime

class ResumeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ATS Resume Assistant")
        self.root.geometry("800x600")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background='#f0f0f0')
        
        self.create_main_menu()

    def create_main_menu(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main menu frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)
        
        # Header
        ttk.Label(main_frame, text="ATS Resume Assistant", style='Header.TLabel').pack(pady=20)
        
        # Buttons
        ttk.Button(main_frame, text="Analyze Existing Resume", 
                  command=self.create_analyze_ui).pack(pady=10, fill=tk.X)
        ttk.Button(main_frame, text="Create New Resume", 
                  command=self.create_resume_ui).pack(pady=10, fill=tk.X)
    
    def create_analyze_ui(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Analyze frame
        analyze_frame = ttk.Frame(self.root)
        analyze_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Back button
        ttk.Button(analyze_frame, text="← Back", command=self.create_main_menu).grid(row=0, column=0, sticky='w')
        
        # UI Elements
        ttk.Label(analyze_frame, text="Resume Analysis", style='Header.TLabel').grid(row=0, column=1, pady=10)
        
        # Job title input
        ttk.Label(analyze_frame, text="Target Job Title:").grid(row=1, column=0, sticky='e', padx=5)
        self.job_title_entry = ttk.Entry(analyze_frame, width=40)
        self.job_title_entry.grid(row=1, column=1, pady=5, sticky='we')
        
        # File upload
        ttk.Label(analyze_frame, text="Resume PDF:").grid(row=2, column=0, sticky='e', padx=5)
        self.file_path = tk.StringVar()
        ttk.Entry(analyze_frame, textvariable=self.file_path, state='readonly').grid(row=2, column=1, sticky='we')
        ttk.Button(analyze_frame, text="Browse", command=self.browse_file).grid(row=2, column=2, padx=5)
        
        # Analyze button
        ttk.Button(analyze_frame, text="Analyze Resume", 
                  command=self.perform_analysis).grid(row=3, column=1, pady=20)
        
        # Result display
        self.result_text = tk.Text(analyze_frame, height=15, width=60, state='disabled')
        self.result_text.grid(row=4, column=0, columnspan=3, pady=10)
        
        analyze_frame.grid_columnconfigure(1, weight=1)
    
    def create_resume_ui(self):
        # Resume creation UI implementation
        pass  # (Similar structure to analyze UI)

    def browse_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if filepath:
            self.file_path.set(filepath)
    
    def perform_analysis(self):
        job_title = self.job_title_entry.get().strip()
        file_path = self.file_path.get()
        
        if not job_title or not file_path:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            resume_text = self.extract_text_from_pdf(file_path)
            analysis = self.analyze_resume(job_title, resume_text)
            
            if not analysis:
                messagebox.showerror("Error", "Invalid job title")
                return
            
            self.display_results(analysis)
            report_file = self.generate_analysis_report(analysis, job_title)
            messagebox.showinfo("Success", f"Report generated: {report_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
    
    def display_results(self, analysis):
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        
        # Display score
        self.result_text.insert(tk.END, f"ATS Score: {analysis['score']}%\n\n", 'bold')
        self.result_text.tag_configure('bold', font=('Arial', 12, 'bold'))
        
        # Found keywords
        self.result_text.insert(tk.END, "Matched Keywords:\n", 'subheader')
        self.result_text.tag_configure('subheader', font=('Arial', 10, 'underline'))
        for kw in analysis['found_keywords']:
            self.result_text.insert(tk.END, f"- {kw.capitalize()}\n", 'green')
        
        # Missing keywords
        self.result_text.insert(tk.END, "\nMissing Keywords:\n", 'subheader')
        for kw in analysis['missing_keywords']:
            self.result_text.insert(tk.END, f"- {kw.capitalize()}\n", 'red')
        
        self.result_text.tag_configure('green', foreground='#006400')
        self.result_text.tag_configure('red', foreground='#8b0000')
        self.result_text.config(state='disabled')
    
    # Existing backend functions from previous implementation
    def extract_text_from_pdf(self, file_path):
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text.lower()
    
    def analyze_resume(self, job_title, resume_text):
        with open('ats_keywords.json') as f:
            ats_keywords = json.load(f)
        
        if job_title not in ats_keywords:
            return None
        
        target_keywords = [kw.lower() for kw in ats_keywords[job_title]]
        found_keywords = []
        
        for keyword in target_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', resume_text):
                found_keywords.append(keyword)
        
        score = (len(found_keywords)/len(target_keywords)) * 100
        missing_keywords = list(set(target_keywords) - set(found_keywords))
        
        return {
            'score': round(score, 1),
            'found_keywords': found_keywords,
            'missing_keywords': missing_keywords,
            'total_keywords': len(target_keywords)
        }
    
    def generate_analysis_report(self, data, job_title):
        # Existing PDF generation code
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeApp(root)
    root.mainloop()