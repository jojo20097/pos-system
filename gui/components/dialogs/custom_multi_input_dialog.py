import customtkinter


class CustomMultiInputDialog(customtkinter.CTkToplevel):
    def __init__(self, parent, title, prompts):
        super().__init__()
        self.title(title)
        self.input_values = []

        self.grid_columnconfigure(1, weight=1)
        # self.grid_rowconfigure(2, weight=1)

        # Create input fields
        self.input_entries = []
        for i, prompt in enumerate(prompts):
            label = customtkinter.CTkLabel(self, text=prompt)
            label.grid(row=i*2, column=0, padx=20, pady=0, columnspan=2)
            if prompt == "Password":
                entry = customtkinter.CTkEntry(self, show="*")
            entry = customtkinter.CTkEntry(self)
            entry.grid(row=i*2+1, column=0, padx=20,
                       pady=0, sticky="we", columnspan=2)
            self.input_entries.append(entry)

        # Add OK button
        ok_button = customtkinter.CTkButton(
            self, text="OK", command=self.get_input_values)
        ok_button.grid(row=len(prompts)+2, column=0,
                       columnspan=2, padx=20, pady=20, sticky="we")

        password_entry: customtkinter.CTkEntry = self.input_entries[1]
        password_entry.bind("<Return>", self.get_input_values)

    def get_input_values(self, sequence=None):
        self.input_values = [entry.get() for entry in self.input_entries]
        print(self.input_values)
        self.destroy()
