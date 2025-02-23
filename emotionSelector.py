from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox

class emotionSelector(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation='horizontal'
        self.size_hint=(None, None)
        self.size=(400, 100)
        self.pos_hint={'center_x': 0.5, 'center_y': 0.5}

    def build(self):
        box_layout = BoxLayout(
            
        )

        # Adding a label at the top center
        box_layout.add_widget(
            Label(
                text="Welcome to FloatLayout!",
            )
        )

        box_layout.add_widget(
            CheckBox(
                active=False
            )
        )

        return box_layout