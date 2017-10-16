import markovify
import win32com.client as wincl

if __name__ == '__main__':
    text = open('data.txt', 'r', encoding='utf-8').read()
    text_model = markovify.Text(text)
    speak = wincl.Dispatch("SAPI.SpVoice")
    while True:
        input()
        output = text_model.make_sentence()
        speak.Speak(output)
        print(output)