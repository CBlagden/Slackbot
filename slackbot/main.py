from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from requests import Session
from slackbot.slackcrawler import SlackCrawler


class MainApp(App):
    def build(self):

        layout = BoxLayout(orientation='vertical')

        inputKeyLabel = Label(text='Enter api key: ', size_hint_y=None)
        inputKeyLabel.height = 30
        inputKeyField = TextInput(text='xoxp-3278486248-78952291655-256623167682-8311d81d495b53995888c2a3d8c1e52f',
                                  multiline=False, size_hint_y=None)
        inputKeyField.height = 30

        inputNameLabel = Label(text='Enter bot name: ', size_hint_y=None)
        inputNameLabel.height = 30
        inputNameField = TextInput(text='Default Bot Name', multiline=False, size_hint_y=None)
        inputNameField.height = 30

        inputChannelLabel = Label(text='Enter chanel name: ', size_hint_y=None)
        inputChannelLabel.height = 30
        inputChannelField = TextInput(text='test', multiline=False, size_hint_y=None)
        inputChannelField.height = 30

        inputMessLabel = Label(text='Enter message: ', size_hint_y=None)
        inputMessLabel.height = 30
        inputMessField = TextInput(text='', size_hint_y=None, multiline=False)
        inputMessField.height = 30

        botStatusLabel = Label(text='Bot Status: ', size_hint_y=None)
        botStatusLabel.height = 30

        botStatus = Label(text='')
        botStatus.color = (1, 0, 0)

        runButton = Button(text='Run Slackbot')
        runButton.height = 30

        def start_bot(instance):
                with Session() as session:
                    s = SlackCrawler(inputKeyField.text, session, inputNameField.text)
                    s.start()

        runButton.bind(on_press=start_bot)
        layout.add_widget(inputKeyLabel)
        layout.add_widget(inputKeyField)
        layout.add_widget(inputNameLabel)
        layout.add_widget(inputNameField)
        layout.add_widget(inputChannelLabel)
        layout.add_widget(inputChannelField)
        layout.add_widget(inputMessLabel)
        layout.add_widget(inputMessField)
        layout.add_widget(botStatusLabel)
        layout.add_widget(botStatus)
        layout.add_widget(runButton)
        return layout


if __name__ == '__main__':
    MainApp().run()
