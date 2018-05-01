import numpy as np
from keyword_ranking import KeywordRanking
from nltk.tokenize import word_tokenize
from random import sample
from scipy.stats import entropy
from sklearn.feature_extraction.text import TfidfVectorizer


class TextDatasetLabelingAssistant(object):
    def __init__(self, alpha="auto"):
        self.__alpha = alpha
        self.__query_cache = {}

    def expand_keywords(self, data, keywords, mode="liu", min_freq=0.05,
                        max_new_keywords=5, a=1.0, b=0.8, c=0.1,
                        threshold=1/30, use_relative_threshold=True):
        print(keywords)

        if mode == "liu":
            keyword_ranking = KeywordRanking(min_freq, max_new_keywords)
            keywords = keyword_ranking.expand_keywords(data, keywords)
        elif mode == "rocchio":
            keywords = self.__rocchio(data, keywords, a, b, c, threshold,
                                      use_relative_threshold)

        print(keywords)
        return keywords

    def get_alpha(self):
        return self.__alpha

    def label_with_active_learning(self, data, classifier, vectorizer,
                                   num_docs_to_label, batch_size=1,
                                   valid_labels=["Positive", "Negative"],
                                   X=[], y=[]):
        valid_input = [str(x + 1) for x in range(len(valid_labels))]
        i = 0

        while len(y) < len(valid_labels):
            label = self.__labeling_prompt(data[i], str(len(y) + 1),
                                           len(valid_labels), valid_input,
                                           valid_labels)

            if label not in y:
                X.append(data[i][0])
                y.append(label)
                del data[i]
            else:
                i += 1

        num_docs_labeled = len(y)

        while len(data) > 0 and num_docs_labeled < num_docs_to_label:
            classifier.fit(vectorizer.fit_transform(X), y)

            vectors = vectorizer.transform([doc[0] for doc in data])
            probs = classifier.predict_proba(vectors)
            r = range(probs.shape[0])
            scores = [entropy(np.transpose(probs[i, :]), base=2) for i in r]

            del probs

            mappings = dict(zip([doc[0] for doc in data], scores))

            del scores
            data.sort(key=lambda doc: mappings[doc[0]], reverse=True)
            del mappings

            batch_size = min(batch_size, num_docs_to_label - num_docs_labeled,
                             len(data))

            for i in range(batch_size):
                num_docs_labeled += 1

                X.append(data[i][0])
                y.append(self.__labeling_prompt(data[i], str(num_docs_labeled),
                                                num_docs_to_label, valid_input,
                                                valid_labels))

            del data[:batch_size]

        return X, y

    def label_with_keywords(self, data, keywords, num_docs_to_label=0,
                            valid_labels=["Positive", "Negative"],
                            labels=None, return_query_data=False, X=[], y=[]):
        valid_input = [str(x + 1) for x in range(len(valid_labels))]
        kw_set = set(keywords)
        sample_range = set(range(len(data)))
        indices_added = set()

        if self.__alpha == "auto":
            positive = valid_labels[0]

            if len(X) == 0:
                sample_size = max(30, round(num_docs_to_label * 0.1))
                sample_size = min(sample_size, len(data))

                while len(X) < sample_size and len(sample_range) > 0:
                    i = sample(sample_range, 1)[0]

                    sample_range.remove(i)

                    if data[i] not in self.__query_cache:
                        self.__query_cache[data[i]] = set()
                        tokenized = set(word_tokenize(data[i]))

                        for keyword in keywords:
                            if keyword in tokenized:
                                self.__query_cache[data[i]].add(keyword)

                    contained_keywords = self.__query_cache[data[i]]

                    if len(kw_set.intersection(contained_keywords)) > 0:
                        label = None if labels is None else labels[i]
                        label = self.__labeling_prompt((data[i], label),
                                                    str(len(X) + 1),
                                                    num_docs_to_label,
                                                    valid_input, valid_labels)

                        X.append(data[i])
                        y.append(label)
                        indices_added.add(i)

            pos_count = sum([1 for i in range(len(y)) if y[i] == positive])
            pos_ratio = pos_count / len(y) if len(y) > 0 else 0
            self.__alpha = 1.0 if pos_ratio < 0.5 else 0.5 * pos_ratio

        num_labeled = len(X)
        num_with_keywords = round(self.__alpha * num_docs_to_label)
        sample_range = set(range(len(data))).difference(indices_added)

        if return_query_data:
            X = []
            y = []

        while num_labeled < num_with_keywords and len(sample_range) > 0:
            i = sample(sample_range, 1)[0]

            if data[i] not in self.__query_cache:
                self.__query_cache[data[i]] = set()
                tokenized = set(word_tokenize(data[i]))

                for keyword in keywords:
                    if keyword in tokenized:
                        self.__query_cache[data[i]].add(keyword)

            sample_range.remove(i)

            if len(kw_set.intersection(self.__query_cache[data[i]])) > 0:
                num_labeled += 1
                label = None if labels is None else labels[i]

                if not return_query_data:
                    label = self.__labeling_prompt((data[i], label),
                                                   str(num_labeled),
                                                   num_docs_to_label,
                                                   valid_input, valid_labels)

                indices_added.add(i)
                X.append(data[i])
                y.append(label)

        if num_labeled < num_docs_to_label:
            sample_range = set(range(len(data))).difference(indices_added)

            while num_labeled < num_docs_to_label and len(sample_range) > 0:
                i = sample(sample_range, 1)[0]
                num_labeled += 1
                label = None if labels is None else labels[i]

                if not return_query_data:
                    label = self.__labeling_prompt((data[i], label),
                                                   str(num_labeled),
                                                   num_docs_to_label,
                                                   valid_input, valid_labels)

                sample_range.remove(i)
                X.append(data[i])
                y.append(label)

        return X, y

    def label_with_selected_keywords(self, data, keywords, num_docs_to_label,
                                     valid_labels=["Positive", "Negative"],
                                     labels=None):
        keywords, X, y, indices_added = self.select_keywords(data, keywords,
                                                             num_docs_to_label,
                                                             valid_labels,
                                                             labels)
        sample_range = set(range(len(data))).difference(indices_added)
        data = [data[i] for i in sample_range]
        labels = None if labels is None else [labels[i] for i in sample_range]
        return self.label_with_keywords(data, keywords, num_docs_to_label,
                                        valid_labels, labels, X=X, y=y)

    def __labeling_prompt(self, document, doc_num, num_docs_to_label,
                          valid_input, labels):
        if document[1] is not None:
            return document[1]

        label = None

        print("Document " + doc_num + " of " + str(num_docs_to_label) + ":")
        print(document[0] + "\n\nSelect a class label:")

        for j in range(len(labels)):
            print(valid_input[j] + ": " + labels[j])

        while label is None or label not in valid_input:
            selection = input("\n> ")

            if selection in valid_input:
                label = labels[int(selection) - 1]

        return label

    def query_with_keywords(self, data, keywords, budget, num_docs_to_label,
                            labels=None,
                            valid_labels=["Positive", "Negative"]):
        keywords, X, y, indices_added = self.select_keywords(data, keywords,
                                                             num_docs_to_label,
                                                             valid_labels,
                                                             labels)
        sample_range = set(range(len(data))).difference(indices_added)
        data = [data[i] for i in sample_range]
        labels = None if labels is None else [labels[i] for i in sample_range]
        X_queried, y_queried = self.label_with_keywords(data, keywords, budget,
                                                        labels=labels,
                                                        return_query_data=True,
                                                        X=X, y=y)
        return X, y, X_queried, y_queried

    def __rocchio(self, data, keywords, a=1.0, b=0.8, c=0.1, threshold=1/30,
                  use_relative_threshold=True):
        vectorizer = TfidfVectorizer(stop_words="english")
        keyword_set = set(keywords)
        related = []
        nonrelated = []

        for document in data:
            doc = document[0]

            if len(keyword_set.intersection(set(word_tokenize(doc)))) > 0:
                related.append(doc)
            else:
                nonrelated.append(doc)

        query = ""

        for keyword in keywords:
            query += (" " if len(query) > 0 else "") + keyword

        vectorizer.fit(related + nonrelated)

        num_related = len(related)
        num_nonrelated = len(nonrelated)
        related = vectorizer.transform(related)
        nonrelated = vectorizer.transform(nonrelated)
        query = vectorizer.transform([query])
        modified_query = a * query
        modified_query += b / num_related * related.sum(axis=0)
        modified_query -= c / num_nonrelated * nonrelated.sum(axis=0)
        words = vectorizer.get_feature_names()
        expanded_keywords = []

        if use_relative_threshold:
            max_keyword_tfidf = 1

            for i in range(len(words)):
                if words[i] in keywords and query[0, i] < max_keyword_tfidf:
                    max_keyword_tfidf = query[0, i]

            threshold *= max_keyword_tfidf

        for i in range(modified_query.shape[1]):
            if not (modified_query[0, i] <= threshold):
                expanded_keywords.append(words[i])

        return expanded_keywords

    def select_keywords(self, data, keywords, num_docs_to_label,
                        valid_labels=["Positive", "Negative"], labels=None):
        valid_input = [str(x + 1) for x in range(len(valid_labels))]
        pos_cnt = 0
        difference = 1
        selected_keywords = set()
        sample_range = set(range(len(data)))
        indices_added = set()
        X = []
        y = []

        while len(keywords) > 0 and len(X) < num_docs_to_label:
            sample_size = max(30, round(num_docs_to_label * 0.1))
            sample_size = min(sample_size, len(sample_range))
            X_new = []
            y_new = []

            while len(X_new) < sample_size and len(sample_range) > 0:
                subsample_sz = min(sample_size - len(X_new), len(sample_range))

                for i in sample(sample_range, subsample_sz):
                    sample_range.remove(i)

                    if data[i] not in self.__query_cache:
                        self.__query_cache[data[i]] = set()

                        if keywords[0] in word_tokenize(data[i]):
                            self.__query_cache[data[i]].add(keywords[0])

                    if keywords[0] in self.__query_cache[data[i]]:
                        label = None if labels is None else labels[i]
                        num_labeled = len(X) + len(X_new) + 1

                        indices_added.add(i)
                        X_new.append(data[i])
                        y_new.append(self.__labeling_prompt((data[i], label),
                                                            str(num_labeled),
                                                            num_docs_to_label,
                                                            valid_input,
                                                            valid_labels))

            pos_cnt += sum([1 for label in y_new if label == valid_labels[0]])
            new_difference = abs(0.5 - pos_cnt / (len(X) + len(X_new)))

            if new_difference > difference:
                break

            selected_keywords.add(keywords[0])

            keywords = keywords[1:]
            difference = new_difference
            X += X_new
            y += y_new

        return list(selected_keywords), X, y, indices_added

    def set_alpha(self, alpha):
        self.__alpha = alpha
