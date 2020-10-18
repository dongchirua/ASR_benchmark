"""
    source: https://github.com/deepai-solutions/core_nlp
"""
from abc import ABC, abstractmethod
import re
import unicodedata as ud
import ast


def load_n_grams(file_path):
    """
    Load n grams from text files
    :param file_path: input to bi-gram or tri-gram file
    :return: n-gram words. E.g. bi-gram words or tri-gram words
    """
    with open(file_path, encoding="utf8") as fr:
        words = fr.read()
        words = ast.literal_eval(words)
    return words


class FacadeTokenization(ABC):

    @abstractmethod
    def tokenize(self, text):
        """
        Convert a sentence to an array of words
        :param text: input sentence (format: string)
        :return: array of words (format: array of strings)
        """
        raise NotImplementedError

    @staticmethod
    def syllablize(text):
        """
        Split a sentences into an array of syllables
        :param text: input sentence
        :return: list of syllables
        """
        # TODO: Fix bug on datetime, E.g. 2013/10/20 09:20:30
        text = ud.normalize('NFC', text)
        sign = [r"==>", r"->", r"\.\.\.", r">>"]
        digits = r"\d+([\.,_]\d+)+"
        email = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        web = r"^(http[s]?://)?(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$"
        datetime = [
            r"\d{1,2}\/\d{1,2}(\/\d+)?",
            r"\d{1,2}-\d{1,2}(-\d+)?",
        ]
        word = r"\w+"
        non_word = r"[^\w\s]"
        abbreviations = [
            r"[A-ZĐ]+\.",
            r"Tp\.",
            r"Mr\.", r"Mrs\.", r"Ms\.",
            r"Dr\.", r"ThS\."
        ]
        patterns = []
        patterns.extend(abbreviations)
        patterns.extend(sign)
        patterns.extend([web, email])
        patterns.extend(datetime)
        patterns.extend([digits, non_word, word])
        patterns = "(" + "|".join(patterns) + ")"

        tokens = re.findall(patterns, text, re.UNICODE)
        return [token[0] for token in tokens]


class LongMatchingTokenizer(FacadeTokenization):

    def __init__(self, bi_grams_path, tri_grams_path):
        """
        Initial config
        :param bi_grams_path: path to bi-grams set
        :param tri_grams_path: path to tri-grams set
        """
        self.bi_grams = load_n_grams(bi_grams_path)
        self.tri_grams = load_n_grams(tri_grams_path)

    def tokenize(self, text: str):
        """
        Tokenize text using long-matching algorithm
        :param text: input text
        :return: tokens
        """

        syllables = LongMatchingTokenizer.syllablize(text)
        syl_len = len(syllables)
        curr_id = 0
        word_list = []
        done = False
        while (curr_id < syl_len) and (not done):
            curr_word = syllables[curr_id]
            if curr_id >= (syl_len - 1):
                word_list.append(curr_word)
                done = True
            else:
                next_word = syllables[curr_id + 1]
                pair_word = ' '.join([curr_word.lower(), next_word.lower()])
                if curr_id >= (syl_len - 2):
                    if pair_word in self.bi_grams:
                        word_list.append('_'.join([curr_word, next_word]))
                        curr_id += 2
                    else:
                        word_list.append(curr_word)
                        curr_id += 1
                else:
                    next_next_word = syllables[curr_id + 2]
                    triple_word = ' '.join([pair_word, next_next_word.lower()])
                    if triple_word in self.tri_grams:
                        word_list.append('_'.join([curr_word, next_word, next_next_word]))
                        curr_id += 3
                    elif pair_word in self.bi_grams:
                        word_list.append('_'.join([curr_word, next_word]))
                        curr_id += 2
                    else:
                        word_list.append(curr_word)
                        curr_id += 1
        return word_list


def test():
    lm_tokenizer = LongMatchingTokenizer(bi_grams_path='./bi_grams.txt',
                                         tri_grams_path='./tri_grams.txt')
    tokens = lm_tokenizer.tokenize("ảnh x quang có xuất hiện nốt màng phổi ở vùng đỉnh phổi kích thước 3 mm")
    print(tokens)


if __name__ == '__main__':
    test()
