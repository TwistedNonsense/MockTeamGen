#!/usr/bin/env python3

"""
Simple GUI to generate bcrypt password_hash values using Flask-Bcrypt.
"""
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox

try:
    from flask_bcrypt import Bcrypt
except Exception as e:
    Bcrypt = None  # type: ignore[assignment]
    _BCRYPT_IMPORT_ERROR = e
else:
    _BCRYPT_IMPORT_ERROR = None

if Bcrypt is None:
    HASHING_AVAILABLE = False
    _BCRYPT_INIT_ERROR = _BCRYPT_IMPORT_ERROR
else:
    try:
        _ = Bcrypt()
    except Exception as e:
        HASHING_AVAILABLE = False
        _BCRYPT_INIT_ERROR = e
    else:
        HASHING_AVAILABLE = True
        _BCRYPT_INIT_ERROR = None

APP_TITLE = "Password Hash Generator"

class HashPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=12)

        self._bcrypt = None
        if HASHING_AVAILABLE and Bcrypt is not None:
            try:
                self._bcrypt = Bcrypt()
            except Exception as e:
                self._bcrypt = None
                self._bcrypt_error = e
            else:
                self._bcrypt_error = None
        else:
            self._bcrypt_error = _BCRYPT_INIT_ERROR

        if self._bcrypt is None:
            banner = tk.Label(
                self,
                text=(
                    "Password hashing is unavailable because the dependency 'flask-bcrypt' (and 'bcrypt') "
                    "is not installed or could not be initialized.\n\nInstall: pip install flask-bcrypt bcrypt"
                ),
                justify="left",
                fg="firebrick",
            )
            banner.pack(fill="x", pady=(0, 10))

        # Input
        frm_in = ttk.Frame(self)
        frm_in.pack(fill="x")

        ttk.Label(frm_in, text="Password").grid(row=0, column=0, sticky="w")
        self.ent_pwd = ttk.Entry(frm_in, width=64)
        self.ent_pwd.grid(row=0, column=1, columnspan=4, sticky="we", padx=(8, 0))
        frm_in.columnconfigure(4, weight=1)

        ttk.Label(frm_in, text="Cost (rounds)").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.spn_rounds = ttk.Spinbox(frm_in, from_=4, to=15, width=6)
        self.spn_rounds.set(12)
        self.spn_rounds.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(8, 0))

        self.btn_gen = ttk.Button(frm_in, text="Generate", command=self.generate_hash)
        self.btn_gen.grid(row=1, column=2, sticky="w", padx=(12, 0), pady=(8, 0))

        self.btn_clear = ttk.Button(frm_in, text="Clear", command=self.clear_all)
        self.btn_clear.grid(row=1, column=3, sticky="w", padx=(12, 0), pady=(8, 0))

        self.btn_copy = ttk.Button(frm_in, text="Copy hash", command=self.copy_hash)
        self.btn_copy.grid(row=1, column=4, sticky="e", padx=(12, 0), pady=(8, 0))

        # Output
        frm_out = ttk.LabelFrame(self, text="password_hash", padding=12)
        frm_out.pack(fill="both", expand=True, pady=(12, 0))

        self.txt_hash = tk.Text(frm_out, height=4, wrap="none")
        self.txt_hash.pack(fill="both", expand=True)
        self._set_output_state(disabled=True)

        # Footer
        frm_foot = ttk.Frame(self)
        frm_foot.pack(fill="x", pady=(10, 0))
        ttk.Label(frm_foot, text="Paste this value in the password hash column of the mock Users table.").pack(anchor="w")

        italic = tkfont.nametofont("TkDefaultFont").copy()
        italic.configure(slant="italic")
        self.lbl_status = tk.Label(frm_foot, text="", font=italic, fg="gray25")
        self.lbl_status.pack(anchor="w", pady=(6, 0))

        if self._bcrypt is None:
            self.btn_gen.configure(state="disabled")
            self.set_status(
                "Hashing is unavailable (missing dependency: flask-bcrypt). "
                "Install: pip install flask-bcrypt bcrypt"
            )
            self._write_output("(Hashing unavailable)\nInstall: pip install flask-bcrypt bcrypt")

    def _set_output_state(self, disabled: bool):
        self.txt_hash.config(state=("disabled" if disabled else "normal"))

    def _write_output(self, text: str):
        self._set_output_state(False)
        self.txt_hash.delete("1.0", "end")
        if text:
            self.txt_hash.insert("1.0", text)
        self._set_output_state(True)

    def set_status(self, msg: str):
        self.lbl_status.config(text=msg)

    def generate_hash(self):
        if self._bcrypt is None:
            messagebox.showerror(
                APP_TITLE,
                "Missing dependency: flask-bcrypt (and bcrypt).\n\n"
                "Install: pip install flask-bcrypt bcrypt",
            )
            return

        pwd = self.ent_pwd.get()
        try:
            rounds = int(self.spn_rounds.get())
        except ValueError:
            messagebox.showerror(APP_TITLE, "Rounds must be an integer.")
            return

        if len(pwd) < 8:
            messagebox.showerror(APP_TITLE, "Password must be at least 8 characters.")
            return
        if not (4 <= rounds <= 15):
            messagebox.showerror(APP_TITLE, "Rounds must be between 4 and 15.")
            return

        try:
            h = self._bcrypt.generate_password_hash(pwd, rounds=rounds).decode("utf-8")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Hashing error: {e}")
            return

        self._write_output(h)
        self.set_status("")

    def copy_hash(self):
        self._set_output_state(False)
        val = self.txt_hash.get("1.0", "end").strip()
        self._set_output_state(True)
        if not val:
            self.set_status("No hash to copy. Generate first.")
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(val)
            self.update()
            self.set_status("Hashed password copied to clipboard.")
        except Exception as e:
            self.set_status(f"Clipboard error: {e}")

    def clear_all(self):
        self.ent_pwd.delete(0, "end")
        self.spn_rounds.set(12)
        self._write_output("")
        self.set_status("")


class HashApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("720x340")
        self.minsize(680, 320)

        if not HASHING_AVAILABLE:
            self.after(
                0,
                lambda: messagebox.showwarning(
                    APP_TITLE,
                    "Password hashing is unavailable because 'flask-bcrypt' (and 'bcrypt') is not installed.\n\n"
                    "Install: pip install flask-bcrypt bcrypt",
                ),
            )

        panel = HashPanel(self)
        panel.pack(fill="both", expand=True)

if __name__ == "__main__":
    try:
        app = HashApp()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)
