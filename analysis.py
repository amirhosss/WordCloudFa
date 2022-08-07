import os
import re
import json
import codecs

import numpy as np
import arabic_reshaper
from wordcloud import WordCloud, STOPWORDS
from bidi.algorithm import get_display
from dotenv import load_dotenv

import main


class WordCloudFa():
    def __init__(self, wc: WordCloud, stopwords_file: str, mask_pixel: int) -> None:
        self.wc = wc
        self.stopwords_file = stopwords_file
        self.mask_pixel = mask_pixel

    def rewrite_stopwords(self) -> set:
        stopwords = set()

        stop = codecs.open(self.stopwords_file, 'r', 'utf-8')
        lines = stop.readlines()
        for i in range(len(lines)):
            lines[i] = lines[i].replace('ي', 'ی')
        stop = codecs.open(self.stopwords_file, 'w', 'utf-8').write(''.join(lines))
        stop = codecs.open(self.stopwords_file, 'r', 'utf-8')

        for line in stop:
            line = line.rstrip()
            stopword = arabic_reshaper.reshape(line)
            stopword = get_display(stopword)
            stopwords.add(stopword)

        return stopwords

    def preprocessing_text(self, text: str) -> str:
        weridPatterns = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u'\U00010000-\U0010ffff'
            u"\u200d"
            u"\u2640-\u2642"
            u"\u2600-\u2B55"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\u3030"
            u"\ufe0f"
            u"\u2069"
            u"\u2066"
            u"\u200c"
            u"\u2068"
            u"\u2067"
            "]+", flags=re.UNICODE
        )
        replies_filter = re.compile(r'(@\S+)|(https://\S+)|([^0-9a-zA-Z\u0621-\u06CC\n ]+)')

        clean_text = re.sub('\n ', '\n', weridPatterns.sub('', text))
        clean_text = replies_filter.sub('', clean_text)
        final_preprocessing = clean_text.replace('ي', 'ی')
        codecs.open('text.txt', 'w', 'utf-8').write(final_preprocessing)

        return clean_text

    def generate(self, text: str, save_file_name: str) -> None:
        text = get_display(arabic_reshaper.reshape(text))

        persian_stopwords = self.rewrite_stopwords()
        self.wc.stopwords.update(persian_stopwords)

        x, y = np.ogrid[:self.mask_pixel, :self.mask_pixel]

        mask = ((x-self.mask_pixel/2) ** 2 + (y-self.mask_pixel/2) ** 2 > 
        (.45*self.mask_pixel) ** 2)
        mask = 255 * mask.astype(int)
        self.wc.mask = mask

        self.wc.generate(text)
        image = self.wc.to_image()
        image.show()
        image.save(save_file_name)


if __name__ == '__main__':
    load_dotenv()
    file_name = os.environ['USERNAME_FILE']

    with open(f'../Data/{file_name}.json', 'r', encoding='utf-8') as file:
        tweets = json.loads(file.read())

    all_tweets = []
    for tweet in tweets:
        all_tweets.append(tweet['text'])

    text = '\n'.join(all_tweets)

    wc = WordCloud(
        font_path='fonts/Shabnam/Shabnam.ttf',
        background_color='white',
        stopwords=STOPWORDS,
        collocations=False,
        max_words=100
    )
    wcfa = WordCloudFa(wc=wc, stopwords_file='stop.txt', mask_pixel=1000)
    text = wcfa.preprocessing_text(text)
    wcfa.generate(text=text, save_file_name=f'../Data/{file_name}.png')