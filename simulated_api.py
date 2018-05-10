from nltk.tokenize import word_tokenize
from random import sample


class SimulatedAPI(object):
    def __init__(self, data, labels=None):
        self.__data = data
        self.__indices_added = set()
        self.__labels = labels
        self.__query_cache = {}
        self.__tokenized = [set(word_tokenize(document)) for document in data]

    def query(self, keywords, n=1):
        if keywords is None or len(keywords) == 0:
            sample_range = set(range(len(self.__data)))
            indices = sample(sample_range.difference(self.__indices_added), n)
            X = [self.__data[i] for i in indices]

            if self.__labels is not None:
                y = [self.__labels[i] for i in indices]
            else:
                y = [None] * len(X)

            self.__indices_added.update(indices)
            return X, y

        key = " ".join(keywords)

        if key not in self.__query_cache:
            self.__query_cache[key] = set()
            keywords = set(keywords)

            for i in range(len(self.__tokenized)):
                if len(keywords.intersection(self.__tokenized[i])) > 0:
                    self.__query_cache[key].add(i)

        sample_range = set(self.__query_cache[key])
        sample_range = sample_range.difference(self.__indices_added)

        if len(sample_range) > 0:
            n = min(n, len(sample_range))
            indices = sample(sample_range, n)
            X = [self.__data[i] for i in indices]

            if self.__labels is not None:
                y = [self.__labels[i] for i in indices]
            else:
                y = [None] * len(X)

            self.__indices_added.update(indices)
            return X, y

        return [], []

    def reset(self):
        self.__indices_added.clear()
