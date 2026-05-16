import customtkinter

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1280x720")

        self.button = customtkinter.CTkButton(self, text="ze button", command=self.button_callbck)
        self.button.pack(padx=20, pady=20)

    def button_callbck(self):
        print("it clicked")

app = App()
app.mainloop()