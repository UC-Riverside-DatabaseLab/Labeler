import csv
from numpy import unique
from scipy.stats import entropy
from sklearn.feature_extraction.text import CountVectorizer


def evaluate(X, y, classifier, verbose=False):
    """Evaluate the classifier's performance on the given test set.

    Parameters:
    X - A list of documents
    y - A list of class labels
    classifier - A classifier (of type TextClassifier)
    verbose (default False) - If True, print the results of the evaluation

    Returns:
    A dictionary with the following key-value pairs:
        accuracy - The ratio of correctly classified instances
        weightedaccuracy - The ratio of weights of correctly classified
        instances
        confusionmatrix - A "two-dimensional dictionary" where matrix[A][B]
        yields the number of instances of class A that were classified
        as class B by the classifier
    """
    confusion_matrix = {}
    column_width = {}
    results = classifier.predict(X)
    correct = sum([1 if results[i] == y[i] else 0 for i in range(len(y))])
    accuracy = correct / len(y)

    for c1 in classifier.classes_:
        confusion_matrix[c1] = {}

        for c2 in classifier.classes_:
            confusion_matrix[c1][c2] = 0

    for i in range(len(results)):
        if results[i] == y[i]:
            correct += 1

        confusion_matrix[y[i]][results[i]] += 1

        if verbose and y[i] not in column_width:
            column_width[y[i]] = len(y[i])

    sum_accuracies = 0.0
    adjustment = 0.0

    for c1 in confusion_matrix:
        TC = confusion_matrix[c1][c1]
        C = 0.0

        for c2 in confusion_matrix[c1]:
            C += confusion_matrix[c1][c2]

        if C > 0.0:
            sum_accuracies += TC / C
        else:
            adjustment += 1

    weighted_acc = sum_accuracies / (len(confusion_matrix) - adjustment)

    if verbose:
        classes = sorted(list(classifier.classes_))

        print(("Accuracy: %0.2f" % (100 * accuracy)) + "%")
        print(("Weighted Accuracy: %0.2f" % (100 * weighted_acc)) + "%")
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
                str_val = str(confusion_matrix[class_value][prediction])
                width = column_width[prediction] - len(str_val) + 1

                for i in range(0, width):
                    row += " "

                row += str(confusion_matrix[class_value][prediction])

            print(row + " " + class_value)

    return {"accuracy": accuracy, "weightedaccuracy": weighted_acc,
            "confusionmatrix": confusion_matrix}


def parse_arff_file(filename):
    X = []
    y = []
    sample_weight = []

    with open(filename, newline="", errors="ignore") as file:
        parsing_data = False
        attr = []

        for line in file:
            line = line.strip()

            if len(line) == 0:
                continue
            elif not parsing_data and \
                    line.upper().startswith("@ATTRIBUTE"):
                if line.find("{") >= 0:
                    data_type = "NOMINAL"
                else:
                    data_type = line[line.rfind(" ") + 1:].upper()

                attr.append(data_type)
            elif not parsing_data and line.upper() == "@DATA":
                parsing_data = True
            elif parsing_data:
                curr = 0
                value = ""
                features = []
                weight = 1
                in_quotes = False

                if line.endswith("}"):
                    index = line.rfind(",{")

                    if index >= 0:
                        weight = float(line[index + 2:len(line) - 1])
                        line = line[:index]

                index = line.rfind(",")
                label = line[index + 1:]
                line = line[:index]

                for i in range(0, len(line)):
                    if line[i] == "'" and (i == 0 or line[i - 1] != "\\"):
                        in_quotes = not in_quotes
                    elif not in_quotes and line[i] == ",":
                        if attr[curr] == "STRING" or attr[curr] == "NOMINAL":
                            features.append(value)
                        else:
                            features.append(float(value))

                        value = ""
                        curr += 1
                    elif line[i] != "\\":
                        value += line[i]

                if attr[curr] == "STRING" or attr[curr] == "NOMINAL":
                    features.append(value)
                else:
                    features.append(float(value))

                X.append(features)
                y.append(label)
                sample_weight.append(weight)

    if len(X[0]) == 1 and isinstance(X[0][0], str):
        X = [features[0] for features in X]

    if len(y) == 0:
        return X

    if len(sample_weight) == 0:
        return X, y

    return X, y, sample_weight


def parse_csv_file(filename, delimiter=",", quotechar='"'):
    X = []
    y = []
    sample_weight = []

    with open(filename, newline="", errors="ignore") as file:
        for row in csv.reader(file, delimiter=delimiter, quotechar=quotechar):
            X.append(row[0])

            if len(row) > 1:
                y.append(row[1])

            if len(row) > 2:
                sample_weight.append(float(row[2]))

    if len(y) == 0:
        return X

    if len(sample_weight) == 0:
        return X, y

    return X, y, sample_weight


def top_information_gain_words(X, y, top_k=0, min_ig=0):
    vectorizer = CountVectorizer(min_df=2, stop_words="english")
    X = vectorizer.fit_transform(X)
    words = vectorizer.get_feature_names()
    prob = [sum([1 for l2 in y if l1 == l2]) / len(y) for l1 in set(y)]
    base_entropy = entropy(prob, base=2)
    top_words = []

    for column in range(X.shape[1]):
        values, counts = unique(list(X[:, column].data), return_counts=True)
        dictionary = dict(zip(values, counts))
        dictionary[0] = X[:, column].shape[0] - len(X[:, column].data)
        sum_counts = sum(dictionary.values())
        subset_entropy = 0

        for value in dictionary.keys():
            value_probability = dictionary[value] / sum_counts
            s = [y[i] for i in range(X.shape[0]) if X[i, column] == value]
            prob = [sum([1 for l2 in s if l1 == l2]) / len(s) for l1 in set(s)]
            subset_entropy += value_probability * entropy(prob, base=2)

        information_gain = base_entropy - subset_entropy

        if information_gain > min_ig:
            top_words.append((words[column], information_gain))

    top_words.sort(key=lambda word: word[1], reverse=True)

    limit = min(top_k, len(top_words)) if top_k > 0 else len(top_words)
    return top_words[:limit]
