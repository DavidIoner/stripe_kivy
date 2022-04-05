

# ask directory openfiledialog with tkinter
def askdirectory():
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory()



