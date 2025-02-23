from transformers import pipeline
import string
import logging

emotion_label_to_name = {
    "LABEL_0" : "sadness",
    "LABEL_1" : "joy",
    "LABEL_2" : "love",
    "LABEL_3" : "anger",
    "LABEL_4" : "fear",
    "LABEL_5" : "surprise"
}

class TriggerDetectionSettings(object):
    trigger_phrases = []
    emotion_thresholds = {
        "sadness" : 0.8,
        "joy" : 100,
        "love" : 100,
        "anger" : 0.8,
        "fear" : 0.8,
        "surprise" : 0.8,
    }

    def __init__(self, trigger_phrases = None, emotion_thresholds=None):
        if trigger_phrases is not None:
            self.trigger_phrases = trigger_phrases
        if emotion_thresholds is not None:
            self.emotion_thresholds = emotion_thresholds

class TriggerDetector(object):
    settings = None
    classifier = None

    def __init__(self, settings = TriggerDetectionSettings()):
        self.settings = settings
        self.classifier = pipeline("text-classification", model="Panda0116/emotion-classification-model")

    def detect(self, sentence):
        no_punct_sentence = sentence.translate(str.maketrans('', '', string.punctuation))
        words = no_punct_sentence.split(' ')

        for trigger_phrase in self.settings.trigger_phrases:
            if trigger_phrase in words:
                logging.info(f"Detection triggered: phrase {trigger_phrase} was used.")
                return True

        emotions = self.classifier(no_punct_sentence)
        for emotion in emotions:
            name = emotion_label_to_name[emotion['label']]
            magnitude = emotion['score']
            threshold = self.settings.emotion_thresholds[name]

            if magnitude >= threshold:
                logging.info(f"Detection triggered: emotion {name} magnitude {magnitude} exceeded threshold {threshold}.")
                return True
            else:
                logging.info(f"Emotion {name} detected, magnitude {magnitude} was insuffucient")

        return False
