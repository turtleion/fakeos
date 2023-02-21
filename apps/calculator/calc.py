import os

def show_menu(title, items):
    menu_items = ""
    for item in items:
        menu_items += f"{item} '{items[item]}' "
    cmd = f"dialog --clear --stdout --nocancel --title '{title}' --menu 'Select a button:' 0 0 0 {menu_items}"
    return os.popen(cmd).read().strip()

def show_inputbox(title, prompt):
    cmd = f"dialog --clear --stdout --title '{title}' --inputbox '{prompt}' 0 0"
    return os.popen(cmd).read().strip()

def main():
    num1 = show_inputbox("Calculator", "Enter first number:")
    if num1 == False or len(num1) == 0:
        print("EXIT: calc")
        exit(3)
    num2 = show_inputbox("Calculator", "Enter second number:")
    if num1 == False or len(num1) == 0:
        print("EXIT: calc")
        exit(3)
    operations = {"add": "Addition", "sub": "Subtraction", "mul": "Multiplication", "div": "Division"}
    op = show_menu("Calculator", operations)
    result = 0
    if op == "add":
        result = num1 + num2
    elif op == "sub":
        result = num1 - num2
    elif op == "mul":
        result = num1 * num2
    elif op == "div":
        result = num1 / num2
    os.system(f"dialog --clear --msgbox 'The result is {result}' 0 0")

if __name__ == "__main__":
    while True:
        main()
