from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from emotionSelector import emotionSelector

class MemoryMate(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def build(self):
        
        float_layout = FloatLayout()
        box_layout = emotionSelector()

        float_layout.add_widget(
            box_layout
        )

        return float_layout

if __name__ == '__main__':
    MemoryMate().run()