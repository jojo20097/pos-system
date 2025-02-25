from api import DatabaseAPI
from gui import App, CustomMultiInputDialog

if __name__ == "__main__":
    dbAPI = DatabaseAPI()
    app = App()

    x_position = (app.winfo_screenwidth() - 300)
    y_position = (app.winfo_screenheight() - 300)

    username = ""

    while True:
        dialog = CustomMultiInputDialog(app, "Sign In", ["Username:", "Password:"])
        dialog.geometry(f"300x200+{x_position}+{y_position}")
        app.wait_window(dialog)

        user_log = dbAPI.login(dialog.input_values[0], dialog.input_values[1])
        if user_log:
            username = user_log.username
            break
    
    app.init_frames(username)
    app.navigation_frame.grid(row=0, column=0, sticky="nsew")
    app.navigation_frame.select_frame_by_name("home")
    app.mainloop()
