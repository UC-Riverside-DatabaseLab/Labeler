import numpy as np
from keyword_ranking import KeywordRanking
from nltk.tokenize import word_tokenize
from scipy.stats import entropy
from sklearn.feature_extraction.text import TfidfVectorizer


class TextDatasetLabelingAssistant(object):
    def __init__(self, api, sample_size=30):
        self.__api = api
        self.__sample_size = sample_size
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

    def label(self, data, labels, num_docs_to_label,
              valid_labels=["Positive", "Negative"], X=[], y=[]):
        valid_input = [str(x + 1) for x in range(len(valid_labels))]

        for i in range(len(data)):
            label = None if labels is None else labels[i]
            label = self.__labeling_prompt((data[i], label), str(len(X) + 1),
                                           num_docs_to_label, valid_input,
                                           valid_labels)

            X.append(data[i])
            y.append(label)

        return X, y

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

    def label_with_50_50(self, keywords, num_docs_to_label,
                         valid_labels=["Positive", "Negative"]):
        pos_count = 0
        difference = 1
        selected_keywords = []
        X = []
        y = []

        while len(keywords) > 0 and len(X) < num_docs_to_label:
            X_k, y_k = self.__api.query([keywords[0]], self.__sample_size)
            X_k, y_k = self.label(X_k, y_k, num_docs_to_label,
                                  valid_labels=valid_labels)
            pos_count += sum([1 for label in y_k if label == valid_labels[0]])
            new_difference = abs(0.5 - pos_count / (len(X) + len(X_k)))

            if new_difference > difference:
                break

            selected_keywords.append(keywords[0])

            keywords = keywords[1:]
            difference = new_difference
            X += X_k
            y += y_k

        keywords = selected_keywords

        if len(X) == 0:
            X_q, y_q = self.__api.query(keywords, self.__sample_size)
            X_q, y_q = self.label(X_q, y_q, num_docs_to_label, X=X, y=y,
                                  valid_labels=valid_labels)
            X += X_q
            y += y_q

        pos_count = sum([1 for i in range(len(y)) if y[i] == valid_labels[0]])
        pos_ratio = pos_count / len(y) if len(y) > 0 else 0
        alpha = 1.0 if pos_ratio < 0.5 else 0.5 * pos_ratio
        x = round(alpha * num_docs_to_label) - len(X)
        X_q, y_q = self.__api.query(keywords, max(x, 0))
        X_q, y_q = self.label(X_q, y_q, num_docs_to_label, X=X, y=y,
                              valid_labels=valid_labels)
        X += X_q
        y += y_q
        X_q, y_q = self.__api.query(None, max(num_docs_to_label - len(X), 0))
        X_q, y_q = self.label(X_q, y_q, num_docs_to_label, X=X, y=y,
                              valid_labels=valid_labels)
        X += X_q
        y += y_q
        return X, y

    def label_with_top_k(self, keywords, num_docs_to_label,
                         valid_labels=["Positive", "Negative"]):
        positive = valid_labels[0]
        selected_keywords = []
        X = []
        y = []

        for keyword in keywords:
            X_k, y_k = self.__api.query([keyword], self.__sample_size)
            pos_count = sum([1 for i in range(len(y_k)) if y_k[i] == positive])

            if len(y_k) > 0 and pos_count / len(y_k) > 0.1:
                selected_keywords.append(keyword)

                X += X_k
                y += y_k

        k = len(selected_keywords)
        n = round((num_docs_to_label - len(X)) / k)

        if n > 0:
            for keyword in selected_keywords:
                X_k, y_k = self.__api.query([keyword], n)
                X += X_k
                y += y_k

            if len(X) < num_docs_to_label:
                X_q, y_q = self.__api.query(None, num_docs_to_label - len(X))
                X += X_q
                y += y_q

        return self.label(X, y, num_docs_to_label, valid_labels=valid_labels)

    def label_with_top_k_prop(self, keywords, num_docs_to_label,
                              valid_labels=["Positive", "Negative"]):
        positive = valid_labels[0]
        selected_keywords = []
        percent_positive = []
        X = []
        y = []

        for keyword in keywords:
            X_k, y_k = self.__api.query([keyword], self.__sample_size)
            pos_count = sum([1 for i in range(len(y_k)) if y_k[i] == positive])

            if len(y_k) > 0 and pos_count / len(y_k) > 0.1:
                selected_keywords.append(keyword)
                percent_positive.append(pos_count / len(y_k))

                X += X_k
                y += y_k

        for i in range(len(selected_keywords)):
            r = percent_positive[i] / sum(percent_positive)
            n = round(r * (num_docs_to_label - len(X)))

            if n > 0:
                X_k, y_k = self.__api.query([selected_keywords[i]], n)
                X += X_k
                y += y_k

        if len(X) < num_docs_to_label:
            X_q, y_q = self.__api.query(None, num_docs_to_label - len(X))
            X += X_q
            y += y_q

        return self.label(X, y, num_docs_to_label, valid_labels=valid_labels)

    def reset_test_api(self):
        self.__api.reset()

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
