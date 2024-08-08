import pickle
from os import system
from kivy.core.window import Window

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

class MyApp(App):
    def build(self):
        box = BoxLayout(orientation='vertical')

        self.input_field = TextInput(hint_text='Type SQL query...', size_hint=(1, 1), multiline=False)
        self.input_field.bind(on_text_validate=self.on_enter)
        self.input_field.bind(text=self.on_text_change)
        box.add_widget(self.input_field)
        
        self.suggestion_label = Label(size_hint=(1, None), height=30, color=(1, 1, 1, 1))  # White color
        box.add_widget(self.suggestion_label)
        
        self.input_field.focus = True

        self.suggestions = []
        self.current_suggestion_index = 0

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
            self.current_suggestion_index = 0
            self.show_suggestion()
        else:
            self.suggestion_label.text = ''
        
        words = (i.upper() for i in text.split()[:-1])
        for i in words:
            if i not in keywords:
                keywords = (i,) + keywords
                print(i)
    
    def show_suggestion(self):
        if self.suggestions:
            suggestion_text = self.suggestions[self.current_suggestion_index]
            self.suggestion_label.text = suggestion_text

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        print(f"Keycode: {keycode}")
        if not self.suggestions: return
        if keycode in (80, 81):  # Down/Left arrow
            self.current_suggestion_index = (self.current_suggestion_index - 1) % len(self.suggestions)
            self.show_suggestion()
        elif keycode in (79, 82):  # Up/Right arrow
            self.current_suggestion_index = (self.current_suggestion_index + 1) % len(self.suggestions)
            self.show_suggestion()
        elif keycode == 43:  # Tab key
            self.insert_suggestion(self.input_field)

    def insert_suggestion(self, instance):
        suggestion = self.suggestions[self.current_suggestion_index]
        global keywords
        keywords_list = list(keywords)
        print("here")
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
            self.suggestion_label.text = '^.^'
        
        # Schedule refocusing the input field
        from kivy.clock import Clock
        Clock.schedule_once(self.refocus_input, 0)

    def refocus_input(self, dt):
        self.input_field.focus = True

    def copy_to_clipboard(self, text):
        Clipboard.copy(text)

if __name__ == "__main__":
    MyApp().run()

    with open("keywords.dat", 'wb') as f:
        pickle.dump(keywords, f)
        print(keywords)