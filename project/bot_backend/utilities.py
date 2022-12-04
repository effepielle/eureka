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

#convert user choice in the form of KB label (e.g. if users choices Churches the function should return church_building)
def convert_to_label(user_choice): 
    dict = {
        "Churches": "church_building",
        "Parks": "park", 
        "Public Gardens": "public_garden", 
        "City Walls": "city_walls",
        "Squares": "square", 
        "Museums": "museum",
        "Monuments": "monument"
        #TODO: add more items
    }
    return dict[user_choice]

def generate_search_improvement_choices(dict):
    string = "Current choices: \n"
    if dict["accessibility"] != "":
        if dict["accessibility"] == "wheelchair accessible":
            string += "Accessibility: wheelchair friendly\n"
        else:
            string += "Accessibility: wheelchair friendly & unfriendly\n"
    else:
        string += "Accessibility: N/A\n"
    
    #TODO: prices

    if dict["stars"] != "":
        string += "Rating: {} star(s) \n".format(dict["stars"])
    else:
        string += "Rating: all ratings\n"
    
    return string
