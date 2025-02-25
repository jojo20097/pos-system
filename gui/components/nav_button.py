import customtkinter

def nav_button(self, text: str, command) -> customtkinter.CTkButton:
    return customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text=text,
                                    fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                    anchor="w", command=command)
