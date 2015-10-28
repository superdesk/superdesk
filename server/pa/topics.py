
import os.path


TOPICS_FILE = os.path.join(os.path.dirname(__file__), 'topics.txt')


def get_topics(filepath=None):
    """Read topics from given txt file.

    There should be single topic name per line.

    :param filepath: path to topics file
    """
    topics = {}
    if filepath is None:
        filepath = TOPICS_FILE
    with open(filepath, 'r') as f:
        for topic_name in f:
            topic_name = topic_name.strip()
            topic_code = 'patopic:%s' % topic_name.upper()
            if len(topic_name):
                topics[topic_code] = topic_name
    return topics


def init_app(app):
    filepath = app.config.get('PA_TOPICS_FILE')
    app.subjects.register(get_topics(filepath))
