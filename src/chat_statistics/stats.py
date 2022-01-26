import json
from pathlib import Path
from typing import Union

import arabic_reshaper
from bidi.algorithm import get_display
from hazm import Normalizer, word_tokenize
from loguru import logger
from src.data import DATA_DIR
from wordcloud import WordCloud


class ChatStatistics:
    """
    Generates char statistics  from a telegram chat json file
    """
    def __init__(self, chat_json: Union[str, Path]) -> None:
            """
            read chat json file
            :param chat_json: path to telegram export json file
            :type chat_json: Union[str,Path]
            """
            # load chat data
            logger.info(f" Loading char data from {chat_json}")
            with open(chat_json, encoding='utf8') as f:
                self.chat_data = json.load(f)

            self.normalizer = Normalizer()
            # load stopwords
            logger.info(f" loading stopwords from {DATA_DIR/ 'stopwords.txt'}")
            stop_words = open(DATA_DIR/'stopwords.txt', encoding='utf8').readlines() 
            stop_words = list(map(str.strip, stop_words))
            self.stop_words = list(map(self.normalizer.normalize, stop_words))

    def generate_word_cloud(
            self,
            outputdir: Union[str, Path],
            width: int = 800, height: int = 600,
            max_font_size: int = 200):
            """ 
                Generates a word cloud from the chat data
                :param outputdir: path to output directory for word cloud image
                :type outputdir: Union[str , Path]
            """
            logger.info('loading text content')
            text_content = ''
            for msg in self.chat_data['messages']:
                if type(msg['text']) is str:
                    tokens = word_tokenize(msg['text'])
                    tokens = list(filter(lambda item:item not in self.stop_words, tokens))
                    text_content += f"{' '.join(tokens)}"

            # normalize , reshape for final word cloud
            text_content = self.normalizer.normalize(text_content)
            text_content = arabic_reshaper.reshape(text_content)
            text_content = get_display(text_content)

            # generate word cloud
            logger.info('Generating word cloud')
            wordcloud = WordCloud(
                width=1200, height=1200,
                font_path=str(DATA_DIR/'./BHoma.ttf'),
                background_color='white',
                max_font_size=200
                ).generate(text_content)
            logger.info(f'Saving wprd cloud to {outputdir}')
            wordcloud.to_file(Path(outputdir)/'wordcolud.png')


if __name__ == "__main__":
    chat_stats = ChatStatistics(chat_json=DATA_DIR/'cs_stackoverflow.json')
    chat_stats.generate_word_cloud(outputdir=DATA_DIR)

    print('Done')
