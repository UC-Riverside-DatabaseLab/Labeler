import csv
import re
from hashlib import md5
from mysql import connector
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
from pathlib import Path
from random import sample, seed, shuffle
from scipy.stats import entropy
from simulated_api import SimulatedAPI
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from text_dataset_labeling_assistant import TextDatasetLabelingAssistant
from time import time


def clean_str(string, stemmer=None):
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    string = string.strip().lower()

    if stemmer is not None:
        string = " ".join([stemmer.stem(w) for w in word_tokenize(string)])

    return string


def evaluate(classifier, documents, labels, verbose=False):
    correct = 0
    confusion_matrix = {}
    column_width = {}
    results = classifier.predict(documents)

    for i in range(documents.shape[0]):
        if results[i] == labels[i]:
            correct += 1

        if labels[i] not in confusion_matrix:
            confusion_matrix[labels[i]] = {}

        if results[i] not in confusion_matrix[labels[i]]:
            confusion_matrix[labels[i]][results[i]] = 0

        confusion_matrix[labels[i]][results[i]] += 1

        if verbose and labels[i] not in column_width:
            column_width[labels[i]] = len(labels[i])

    accuracy = 100 * correct / documents.shape[0]

    if verbose:
        classes = list(confusion_matrix.keys())

        classes.sort()
        print(("Accuracy: %0.2f" % (accuracy)) + "%")
        print("Confusion Matrix:")

        for class_value, distribution in confusion_matrix.items():
            for prediction, count in distribution.items():
                if prediction not in column_width:
                    width = max(len(prediction), len(str(count)))
                    column_width[prediction] = width
                elif prediction in column_width:
                    if len(str(count)) > column_width[prediction]:
                        column_width[prediction] = len(str(count))

        row = ""

        for prediction in classes:
            width = column_width[prediction] - len(str(prediction)) + 1

            for i in range(0, width):
                row += " "

            row += prediction

        print(row + " <- Classified As")

        for class_value in classes:
            row = ""

            for prediction in classes:
                if prediction not in confusion_matrix[class_value]:
                    confusion_matrix[class_value][prediction] = 0

                str_val = str(confusion_matrix[class_value][prediction])
                width = column_width[prediction] - len(str_val) + 1

                for i in range(0, width):
                    row += " "

                row += str(confusion_matrix[class_value][prediction])

            print(row + " " + class_value)

    return {"accuracy": accuracy, "confusionmatrix": confusion_matrix}


def load_data(subreddit, test_data_length, test_data_pos_ratio=0.5,
              pos="Positive", neg="Negative", use_stemmer=False):
    sub = subreddit
    stem = SnowballStemmer("english") if use_stemmer else None
    c = connector.connect(host="dblab-rack20", database="HEALTHDATA",
                          user="rriva002", password="passwd")
    related = [clean_str(th, stem) for th in reddit_dataset(sub, connection=c)]
    non_related = [clean_str(th, stem) for th in reddit_dataset(sub, True, c)]

    c.close()
    shuffle(related)
    shuffle(non_related)

    test_data_pos_length = round(test_data_length * test_data_pos_ratio)
    test_data_neg_length = test_data_length - test_data_pos_length
    test_data = related[-test_data_pos_length:]
    test_data += non_related[-test_data_neg_length:]
    test_labels = [pos] * test_data_pos_length + [neg] * test_data_neg_length
    related = related[:-test_data_pos_length]
    non_related = non_related[:-test_data_neg_length]

    data = related + non_related
    labels = [pos] * len(related) + [neg] * len(non_related)
    return data, labels, test_data, test_labels


def print_results(budgets, data_lengths, accuracy, times, positive_ratio):
    result_names = ["Accuracy", "Time", "Percent Positive"]
    results = [accuracy, times, positive_ratio]

    for i in range(len(results)):
        print(result_names[i] + ":")

        for data_length in ["B"] + data_lengths:
            print(str(data_length) + "\t", end="")

        print("")

        for budget in budgets:
            print(str(budget) + "\t", end="")

            for data_length in data_lengths:
                print(results[i][budget][data_length] + "\t", end="")

            print("")

        print("")


def reddit_dataset(subreddit, negate=False, connection=None):
    filename = "reddit_" + ("non_" if negate else "")
    filename += subreddit.replace(" ", "_").lower() + "_posts.csv"

    if not Path(filename).is_file() and connection is not None:
        table = "ecigarette" if subreddit == "Electronic Cigarette" and \
            not negate else "healthforumposts"
        sql = "SELECT DISTINCT URL FROM " + table
        sql += " WHERE source = 'https://www.reddit.com'"

        if subreddit != "Electronic Cigarette" or negate:
            sql += " AND disorder " + ("!" if negate else "")
            sql += "= '" + subreddit + "'"

        urls = []
        cursor = connection.cursor()

        cursor.execute(sql)

        for row in cursor.fetchall():
            urls.append(row[0])

        with open(filename, "w") as file:
            writer = csv.writer(file, lineterminator="\n")

            for url in urls:
                sql = "SELECT body FROM " + table + " WHERE URL = '" + url
                sql += "' AND userid != 'AutoModerator'"
                sql += " AND body IS NOT NULL ORDER BY replyid"
                thread = ""

                cursor.execute(sql)

                for row in cursor.fetchall():
                    post = row[0].replace("\n", " ")
                    thread += (" " if len(thread) > 0 else "") + post

                writer.writerow([thread])

    with open(filename, "r") as file:
        return [line.rstrip("\n") for line in file]


def select_keywords(pos_data, neg_data, n, min_df=2, max_df=1.0,
                    filter_common_neg_words=False, use_pos_freq=False):
    filename = pos_data[0] + neg_data[0] + str(n) + str(min_df) + str(max_df)
    filename += str(filter_common_neg_words) + str(use_pos_freq)
    filename = md5(filename.encode()).hexdigest() + ".txt"

    if Path(filename).is_file():
        with open(filename, "r") as file:
            return [line.rstrip("\n") for line in file]

    pos_words = {}
    neg_words = {}
    stop_words = set(stopwords.words('english'))

    stop_words.add("http")
    stop_words.add("https")
    stop_words.add("www")
    stop_words.add("com")

    for document in pos_data:
        for word in set(word_tokenize(document)):
            if word not in stop_words and len(word) > 1:
                if word not in pos_words:
                    pos_words[word] = 0

                if word not in neg_words:
                    neg_words[word] = 0

                pos_words[word] += 1

    for document in neg_data:
        for word in set(word_tokenize(document)):
            if word not in stop_words and len(word) > 1:
                if word not in pos_words:
                    pos_words[word] = 0

                if word not in neg_words:
                    neg_words[word] = 0

                neg_words[word] += 1

    for word in set(pos_words.keys()):
        df = pos_words[word] + neg_words[word]
        normalized_df = df / (len(pos_data) + len(neg_data))
        pos_freq = pos_words[word] / len(pos_data)
        neg_freq = neg_words[word] / len(neg_data)

        if isinstance(min_df, int) and df < min_df or \
                isinstance(min_df, float) and normalized_df < min_df or \
                isinstance(max_df, int) and df > max_df or \
                isinstance(max_df, float) and normalized_df > max_df or \
                filter_common_neg_words and pos_freq <= neg_freq:
            del pos_words[word]
            del neg_words[word]

    keywords = top_information_gain_words(pos_words, neg_words, len(pos_data),
                                          len(neg_data))

    if use_pos_freq:
        reranked = []

        for word in keywords:
            pos_freq = pos_words[word[0]] / len(pos_data)
            reranked.append((word[0], word[1] * pos_freq))

        keywords = sorted(reranked, key=lambda word: word[1], reverse=True)

    keywords = [keyword[0] for keyword in keywords[:min(len(keywords), n)]]

    with open(filename, "w") as file:
        file.writelines([keyword + "\n" for keyword in keywords])

    return keywords


def test(classifier, vectorizer, X, y, test_data, test_labels):
    classifier.fit(vectorizer.fit_transform(X), y)

    res = evaluate(classifier, vectorizer.transform(test_data), test_labels)
    pos_count = sum([1 for label in y if label == positive])
    res["positive"] = 100 * pos_count / len(X)
    return res


def test_active_learning(data, labels, data_lengths, assist, vectorizer,
                         classifier, test_data, test_labels, batch_size=10,
                         budgets=None, random_state=10):
    accuracy = {}
    times = {}
    positive_ratio = {}

    if budgets is None or len(budgets) == 0:
        budgets = [len(data)]

    for budget in budgets:
        seed(random_state)

        accuracy[budget] = {}
        times[budget] = {}
        positive_ratio[budget] = {}
        samples = sample(range(len(data)), budget)
        merged_data = [(data[i], labels[i]) for i in samples]
        X = []
        y = []
        elapsed = 0

        for data_length in data_lengths:
            if budget < data_length:
                accuracy[budget][data_length] = "x"
                times[budget][data_length] = "x"
                positive_ratio[budget][data_length] = "x"
            else:
                start = time()
                batch_size = batch_size if batch_size > 0 else data_length
                X, y = assist.label_with_active_learning(merged_data,
                                                         classifier,
                                                         vectorizer,
                                                         data_length,
                                                         batch_size=batch_size,
                                                         X=X, y=y)
                elapsed += time() - start
                rs = test(classifier, vectorizer, X, y, test_data, test_labels)
                accuracy[budget][data_length] = "%0.2f" % rs["accuracy"]
                times[budget][data_length] = str(round(elapsed))
                positive_ratio[budget][data_length] = "%0.2f" % rs["positive"]

    print_results(budgets, data_lengths, accuracy, times, positive_ratio)


def test_hybrid_labeling(data, keywords, labels, data_lengths, assist,
                         vectorizer, classifier, test_data, test_labels,
                         batch_size=10, alpha="auto", budgets=None,
                         random_state=10):
    accuracy = {}
    times = {}
    positive_ratio = {}

    if budgets is None or len(budgets) == 0:
        budgets = [len(data)]

    seed(random_state)

    Xi, yi, Xq, yq = assist.query_with_keywords(data, keywords,
                                                budgets[len(budgets) - 1], 300,
                                                labels=labels)
    queried_data = [(Xq[i], yq[i]) for i in range(len(Xq))]

    for budget in budgets:
        accuracy[budget] = {}
        times[budget] = {}
        positive_ratio[budget] = {}
        X = list(Xi)
        y = list(yi)
        budgeted_data = list(queried_data[:budget])
        elapsed = 0

        for data_length in data_lengths:
            if budget < data_length:
                accuracy[budget][data_length] = "x"
                times[budget][data_length] = "x"
                positive_ratio[budget][data_length] = "x"
            else:
                assist.set_alpha(alpha)

                batch_size = batch_size if batch_size > 0 else data_length
                start = time()
                X, y = assist.label_with_active_learning(budgeted_data,
                                                         classifier,
                                                         vectorizer,
                                                         data_length,
                                                         batch_size=batch_size,
                                                         X=X, y=y)
                elapsed += time() - start
                rs = test(classifier, vectorizer, X, y, test_data, test_labels)
                accuracy[budget][data_length] = "%0.2f" % rs["accuracy"]
                times[budget][data_length] = str(round(elapsed))
                positive_ratio[budget][data_length] = "%0.2f" % rs["positive"]

    print_results(budgets, data_lengths, accuracy, times, positive_ratio)


def test_keyword_labeling(data, keywords, labels, data_lengths, assist,
                          vectorizer, classifier, test_data, test_labels,
                          mode="50_50", random_state=10):
    budget = len(data)
    accuracy = {}
    times = {}
    positive_ratio = {}
    accuracy[budget] = {}
    times[budget] = {}
    positive_ratio[budget] = {}

    for data_length in data_lengths:
        seed(random_state)

        start = time()

        if mode == "50_50":
            X, y = assist.label_with_50_50(keywords, data_length)
        elif mode == "top_k":
            X, y = assist.label_with_top_k(keywords, data_length)
        elif mode == "top_k_prop":
            X, y = assist.label_with_top_k_prop(keywords, data_length)

        assist.reset_test_api()

        elapsed = round(time() - start)
        rs = test(classifier, vectorizer, X, y, test_data, test_labels)
        accuracy[budget][data_length] = "%0.2f" % rs["accuracy"]
        times[budget][data_length] = str(elapsed)
        positive_ratio[budget][data_length] = "%0.2f" % rs["positive"]

    print_results([budget], data_lengths, accuracy, times, positive_ratio)


def test_random_labeling(data, labels, data_lengths, vectorizer, classifier,
                         test_data, test_labels, random_state=10):
    print("Random Labeling - Subreddit: " + subreddit)

    for data_length in data_lengths:
        seed(random_state)

        start = time()
        indices = sample(range(len(data)), data_length)
        X = [data[index] for index in indices]
        y = [labels[index] for index in indices]

        print("Time elapsed: " + str(round(time() - start)) + " seconds")
        test(classifier, vectorizer, X, y, test_data, test_labels)


def top_information_gain_words(pos_words, neg_words, pos_cnt, neg_cnt, top_k=0,
                               min_ig=0):
    total = pos_cnt + neg_cnt
    base_entropy = entropy([pos_cnt / total, neg_cnt / total], base=2)
    top_words = []

    for word in pos_words.keys():
        word_occurrences = pos_words[word] + neg_words[word]
        word_nonoccurrences = total - word_occurrences
        word_probability = word_occurrences / total
        dist = [pos_words[word] / word_occurrences,
                neg_words[word] / word_occurrences]
        subset_entropy = word_probability * entropy(dist, base=2)
        dist = [(pos_cnt - pos_words[word]) / word_nonoccurrences,
                (neg_cnt - neg_words[word]) / word_nonoccurrences]
        subset_entropy += (1 - word_probability) * entropy(dist, base=2)
        information_gain = base_entropy - subset_entropy

        if information_gain > min_ig:
            top_words.append((word, information_gain))

    top_words.sort(key=lambda word: word[1], reverse=True)

    limit = min(top_k, len(top_words)) if top_k > 0 else len(top_words)
    return top_words[:limit]


seed(10)

subreddit = "Suicide"
# subreddit = "Electronic Cigarette"
# subreddit = "Politics"
# subreddit = "Depression"
# subreddit = "Diabetes"
# subreddit = "Dentistry"
positive = "Positive"
negative = "Negative"
max_df = 1.0
data, labels, test_data, test_labels = load_data(subreddit, 1000, pos=positive,
                                                 neg=negative)
api = SimulatedAPI(data, labels)
assist = TextDatasetLabelingAssistant(api)
vectorizer = TfidfVectorizer(max_features=1000, min_df=0.03,
                             ngram_range=(1, 3), stop_words="english")
rf = RandomForestClassifier(n_estimators=2000, n_jobs=-1, random_state=10,
                            class_weight="balanced")
data_lengths = [250, 500, 1000, 2000, 3000, 4000, 5000]
budgets = data_lengths + [10000, 20000, 100000, 200000]
keywords = select_keywords([data[i] for i in range(len(data))
                            if labels[i] == positive],
                           [data[i] for i in range(len(data))
                            if labels[i] == negative], 10, max_df=max_df,
                           filter_common_neg_words=False)

print(keywords)
test_keyword_labeling(data, keywords, labels, data_lengths, assist,
                      vectorizer, rf, test_data, test_labels, mode="50_50")
# test_active_learning(data, labels, data_lengths, assist, vectorizer, rf,
#                      test_data, test_labels, batch_size=250, budgets=budgets)
# test_hybrid_labeling(data, keywords, labels, data_lengths, assist,
#                      vectorizer, rf, test_data, test_labels, batch_size=250,
#                      alpha="auto", budgets=budgets)
# test_random_labeling(data, labels, data_lengths, vectorizer, rf, test_data,
#                      test_labels)
