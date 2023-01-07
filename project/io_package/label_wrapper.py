class LabelWrapper:
    def __init__(self):
        self.label_dict = dict()
        self.label_dict_copy = dict()

    def register(self, user_choice_name: str, label: str) -> bool:
        assert user_choice_name is not None
        assert label is not None
        if user_choice_name in self.label_dict_copy:
            return False
        self.label_dict[user_choice_name] = label
        self.label_dict_copy[user_choice_name] = label
        return True

    def unregister(self, user_choice_name: str) -> bool:
        assert user_choice_name is not None
        if user_choice_name not in self.label_dict.keys():
            return False
        self.label_dict.pop(user_choice_name, None)
        return True

    def update(self, user_choice_name: str, new_label: str) -> bool:
        assert user_choice_name is not None
        assert new_label is not None
        if user_choice_name in self.label_dict:
            return False
        self.label_dict[user_choice_name] = new_label
        return True