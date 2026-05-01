import customtkinter as ctk

class Calculator(ctk.CTk):
    def __init__(self):
        super().__init__() #создаем окно
        
        self.title('Калькулятор') #заголовок
        self.geometry('400x300') #размер окна
        
if __name__ == "__main__":
    app = Calculator()
    app.mainloop()