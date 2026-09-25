from pathlib import Path


def test_gui_has_separate_customtkinter_and_tkinter_diagnostics():
    src = (Path(__file__).parents[1] / "src/toolpack_builder/gui.py").read_text()
    assert "CustomTkinter could not be imported" in src
    assert "Python tkinter is not available" in src
    assert "python3-tk" in src
    assert "tk_filedialog.askdirectory" in src
    assert "tk_messagebox.showerror" in src
