import pickle
from os import system
from kivy.core.window import Window

query = ''
with open("keywords.dat", 'rb') as f:
    keywords: tuple = pickle.load(f)
    print(keywords)

try:
    from kivy.config import Config
except ModuleNotFoundError:
    print("Module Kivy not installed.")
    if input("Consent to install necessary module (Kivy)? [y/n]: ") == 'y':
        system('pip install kivy')
    else:
        print("Exiting execution.")
        exit()

Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '100')
Config.write()

from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.clipboard import Clipboard

class MySQL_SwiftApp(App):
    def build(self):
        box = BoxLayout(orientation='vertical')

        self.input_field: TextInput = TextInput(hint_text='Type SQL query...', size_hint=(1, 1), multiline=False)
        self.input_field.bind(on_text_validate=self.on_enter)
        self.input_field.bind(text=self.on_text_change)
        box.add_widget(self.input_field)
        
        self.suggestion_label = Label(size_hint=(1, None), height=30, markup=True)
        box.add_widget(self.suggestion_label)
        
        self.refocus_action(0)

        self.suggestions = []
        self.cur_sug_index = 0
        self.user_queries = []
        self.cur_query_index = -1

        # Bind the key down event to the Window
        Window.bind(on_key_down=self.on_key_down)

        return box

    def on_text_change(self, instance: TextInput, text: str):
        global keywords
        if ' ' in text:
            word = text.split()[-1].upper()
        else:
            word = text.upper()
        self.suggestions = [keyword for keyword in keywords if keyword.startswith(word)]

        if self.suggestions:
            self.cur_sug_index = 0
            self.show_suggestion()
        else:
            self.suggestion_label.text = ''
    
    def show_suggestion(self):
        self.suggestion_label.text = ''
        if self.suggestions:
            for i, suggestion in enumerate(self.suggestions):
                if self.cur_sug_index == i:
                    self.suggestion_label.text += f'[color=FFFF00]{suggestion}[/color]  '
                else:
                    self.suggestion_label.text += f'[color=FFFFFF]{suggestion}[/color]  '
            

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        print(f'keycode: {keycode}')
        if not self.suggestions and self.user_queries == tuple(''): return
        if keycode == 80:  # Left arrow
            self.cur_sug_index = (self.cur_sug_index - 1) % len(self.suggestions)
            self.show_suggestion()
        elif keycode == 79:  # Right arrow
            self.cur_sug_index = (self.cur_sug_index + 1) % len(self.suggestions)
            self.show_suggestion()
        elif keycode == 43:  # Tab key
            self.input_field.text = ([''] + self.user_queries).pop()
        elif keycode == 41 and self.suggestions:  # ESC
            self.suggestions = []
            self.cur_sug_index = 0
            self.show_suggestion()
            self.refocus()

    def insert_suggestion(self, instance):
        suggestion = self.suggestions[self.cur_sug_index]
        global keywords
        keywords_list = list(keywords)
        if suggestion in keywords_list:
            keywords_list.remove(suggestion)
        keywords = (suggestion,) + tuple(keywords_list)
        current_text = instance.text
        words = current_text.split()
        words[-1] = suggestion  # Replace the last word with the suggestion
        instance.text = ' '.join(words) + ' '
        instance.cursor = (len(instance.text), 0)  # Move cursor to end of text

    def on_enter(self, instance):
        if self.suggestions:
            self.insert_suggestion(instance)
        else:
            self.copy_to_clipboard(instance.text)
            global query
            query = instance.text
            self.user_queries += [query]
            print(self.user_queries)
            if query[-1] == ';': query = query[:-1]
            self.input_field.text = ''
            self.suggestion_label.text = '^.^'
        
        self.refocus()
    
    def refocus(self):
        # Schedule refocusing the input field
        from kivy.clock import Clock
        Clock.schedule_once(self.refocus_action, 0)

    def refocus_action(self, dt):
        self.input_field.focus = True

    def copy_to_clipboard(self, text):
        Clipboard.copy(text)

if __name__ == "__main__":
    MySQL_SwiftApp().run()
    
    words = [i.upper() for i in query.split()]
    for i in words:
        if i not in keywords:
            keywords = (i,) + keywords
            print(i)

    with open("keywords.dat", 'wb') as f:
        pickle.dump(keywords, f)
        print(keywords)