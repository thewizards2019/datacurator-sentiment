from flask import Flask
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
# create_app wraps the other functions to set up the project

CLEAN = re.compile("[^A-Z,a-z,\s]")

def create_app(config=None, testing=False, cli=True):
    """
    Application factory, used to create application
    """
    app = Flask(__name__, static_folder=None)
    
    
    analyser = SentimentIntensityAnalyzer()
    def sentiment_analyzer_scores(sentence):
        """
        recieves
        """
        try:
            clean_input = re.sub(CLEAN, "", sentence)
            score = analyser.polarity_scores(clean_input)
            return {"sentiment": score["compound"]}
        except:
            return False

    return app
