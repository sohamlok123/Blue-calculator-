import tkinter as tk
from tkinter import messagebox
import math
import re

def calculate(expression):
    try:
        # Security check: Whitelist allowed characters
        # Allowed: digits, ., +, -, *, /, (, ), !, ^, space, and letters for functions
        # But letters could form malicious words. 
        # We need to verify that only allowed functions/constants are present.
        
        # 1. Check for invalid characters broadly
        if not re.match(r'^[0-9+\-*/().e \^!a-zA-Z]+$', expression):
            return "Error"

        # 2. Check that all words are in our whitelist
        # Extract all words
        words = re.findall(r'[a-zA-Z]+', expression)
        allowed_words = {'sin', 'cos', 'tan', 'log', 'ln', 'sqrt', 'pi', 'e'}
        for word in words:
            if word not in allowed_words:
                 return "Error"
        
        # Handle Factorial: number! -> factorial(number)
        while '!' in expression:
            new_expression = re.sub(r'(\d+)!', r'math.factorial(\1)', expression)
            if new_expression == expression:
                 new_expression = re.sub(r'\(([^)]+)\)!', r'math.factorial(\1)', expression)
            expression = new_expression
            if '!' in expression and not re.search(r'(\d+)!', expression) and not re.search(r'\(([^)]+)\)!', expression):
                 return "Error"

        # Replace power operator
        expression = expression.replace('^', '**')

        # Map of user-friendly names to math module names
        # Order matters! Process 'log' before 'ln' because 'ln' -> 'math.log' and 'log' would match 'math.log'
        replacements = [
            ('log', 'math.log10'), # Process log first
            ('ln', 'math.log'),    # Then ln (which creates math.log, safe from log replacement now)
            ('sin', 'math.sin'),
            ('cos', 'math.cos'),
            ('tan', 'math.tan'),
            ('sqrt', 'math.sqrt'),
            ('pi', 'math.pi'),
            ('e', 'math.e')
        ]

        # Apply replacements using regex word boundaries
        for key, value in replacements:
            pattern = r'\b' + re.escape(key) + r'\b'
            expression = re.sub(pattern, value, expression)
        
        # Evaluate
        result = eval(expression)
        return str(result)
    except Exception as e:
        return "Error"

class BlueCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Best Blue Engineering Calculator")
        self.root.geometry("400x520")
        self.root.configure(bg="#e0f7fa")
        self.root.resizable(False, False)

        self.expression = ""
        self.input_text = tk.StringVar()

        # Display
        input_frame = tk.Frame(self.root, width=400, height=50, bd=0, highlightbackground="#0277bd", highlightcolor="#0277bd", highlightthickness=2)
        input_frame.pack(side=tk.TOP, fill=tk.BOTH)

        input_field = tk.Entry(input_frame, font=('arial', 24, 'bold'), textvariable=self.input_text, width=50, bg="#b3e5fc", bd=0, justify=tk.RIGHT)
        input_field.grid(row=0, column=0)
        input_field.pack(ipady=15, fill=tk.BOTH)

        # Buttons
        btns_frame = tk.Frame(self.root, width=400, height=450, bg="#0277bd")
        btns_frame.pack(fill=tk.BOTH, expand=True)

        self.create_buttons(btns_frame)

    def create_buttons(self, frame):
        btn_config = dict(
            fg="white", 
            width=8, 
            height=2, 
            bd=0, 
            bg="#0288d1", 
            cursor="hand2",
            activebackground="#01579b",
            activeforeground="white",
            font=('arial', 12, 'bold')
        )
        
        buttons = [
            ('C', 0, 0), ('DEL', 0, 1), ('(', 0, 2), (')', 0, 3), ('/', 0, 4),
            ('sin', 1, 0), ('cos', 1, 1), ('tan', 1, 2), ('^', 1, 3), ('*', 1, 4),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('log', 2, 3), ('-', 2, 4),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('ln', 3, 3), ('+', 3, 4),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('sqrt', 4, 3), ('=', 4, 4),
            ('0', 5, 0), ('.', 5, 1), ('pi', 5, 2), ('e', 5, 3), ('!', 5, 4)
        ]
        
        for (text, row, col) in buttons:
            cmd = lambda t=text: self.btn_click(t)
            
            if text == '=':
                 tk.Button(frame, text=text, width=8, height=2, bd=0, bg="#01579b", fg="white", font=('arial', 12, 'bold'),
                           cursor="hand2", command=lambda: self.btn_equal()).grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
            elif text == 'C':
                 tk.Button(frame, text=text, **btn_config, command=lambda: self.btn_clear()).grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
            elif text == 'DEL':
                 tk.Button(frame, text=text, **btn_config, command=lambda: self.btn_delete()).grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
            else:
                 tk.Button(frame, text=text, **btn_config, command=cmd).grid(row=row, column=col, padx=1, pady=1, sticky="nsew")

        for i in range(6):
            frame.rowconfigure(i, weight=1)
        for i in range(5):
            frame.columnconfigure(i, weight=1)

    def btn_click(self, item):
        self.expression = self.expression + str(item)
        self.input_text.set(self.expression)

    def btn_clear(self):
        self.expression = ""
        self.input_text.set("")

    def btn_delete(self):
        self.expression = self.expression[:-1]
        self.input_text.set(self.expression)

    def btn_equal(self):
        result = calculate(self.expression)
        self.input_text.set(result)
        if result != "Error":
            self.expression = result
        else:
            self.expression = ""

if __name__ == "__main__":
    root = tk.Tk()
    app = BlueCalculator(root)
    root.mainloop()
