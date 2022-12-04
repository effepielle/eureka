from telebot import types

# Takes a Telegram Keyboard object and a list of labels and creates buttons, three for each keyboard's row
def create_keyboard(keyboard, labels):
    button_list = []
    counter = 0
    for i in labels:
        button_list.append(types.KeyboardButton(i))
        counter += 1
        if counter == 3:
            keyboard.row(button_list[0],button_list[1],button_list[2])
            button_list = []
            counter = 0
        elif labels.index(i) == len(labels)-1:
            if counter == 2:
                keyboard.row(button_list[0], button_list[1])
                button_list = []
                counter = 0
            elif counter == 1:
                keyboard.row(button_list[0])
                button_list = []
                counter = 0
    # keyboard.add(types.KeyboardButton("Parks"), types.KeyboardButton("Public Garden"), types.KeyboardButton("City Walls"))
    # keyboard.add(types.KeyboardButton("Churches"))

def convert_to_label(user_choice):
    #TODO: return user choice in the form of KB label (e.g. if users choices Churches the function should return church_building)
    pass