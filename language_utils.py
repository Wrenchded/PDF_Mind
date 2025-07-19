from langdetect import detect
from googletrans import Translator

translator = Translator()

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"
    
def translate_to_english(text, src_lang):
    if src_lang == "en":
        return text 
    translation = translator.translate(text, src=src_lang, dest='en')
    return translation.text