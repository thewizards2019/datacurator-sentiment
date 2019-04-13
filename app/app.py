from flask import Flask
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import json
from confluent_kafka import Consumer
from confluent_kafka import Producer

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
        except Exception as exp:
            return False

    c = Consumer(
        {
            "bootstrap.servers": "localhost:9092",
            "group.id": "content_curator_twitter_group_19",
            "auto.offset.reset": "earliest",
        }
    )

    p = Producer({"bootstrap.servers": "localhost:9092"})

    c.subscribe(["content_curator_twitter"])

    while True:
        msg = c.poll()

        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        # print('Received message: {}'.format(msg.value().decode('utf-8')))
        try:
            m = json.loads(msg.value().decode("utf-8"))
            if "content" in m.keys():
                sentiment_value = json.dumps(sentiment_analyzer_scores(m["content"]))
                msg_key = msg.key().decode("utf-8")
                print("sentiment_value", sentiment_value)
                if msg_key is not None:
                    p.produce(
                        topic="content_curator_twitter",
                        key=msg_key,
                        value=sentiment_value,
                    )
                    p.flush()
                    print("ADDED:", {"key": msg_key, "value": sentiment_value})
        except Exception as e:
            print("ERROR:", e)

    c.close()

    return app
