from flask import Flask, jsonify, request
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.svm import SVC
from text_classifiers import CNNClassifier, SKLearnTextClassifier
from utils import evaluate
import pickle
import os
app = Flask(__name__)
app.debug = True
classifier = None
trained = False


@app.route("/classify", methods=["POST"])
def classify():
    json = request.json
    errors = []
    data_key = "data"
    labels_key = "labels"
    path_key = "path"
    with open(os.path.join(json[path_key], 'classify.pkl'), 'rb') as f:
      classifier = pickle.load(f)

    if classifier is None:
        errors.append("no_classifier")

    if data_key not in json or len(json[data_key]) == 0:
        errors.append("no_data")
    elif labels_key in json and len(json[data_key]) != len(json[labels_key]):
        errors.append("label_count_mismatch")

    if len(errors) > 0:
        return jsonify(error=errors)

    if labels_key in json:
        results = evaluate(json[data_key], json[labels_key], classifier)
        return jsonify(accuracy=results["accuracy"],
                       confusion_matrix=results["confusionmatrix"])

    return jsonify(predictions=classifier.predict(json[data_key]))


@app.route("/train", methods=["POST"])
def train():
    json = request.json
    vectorizer_key = "vectorizer"
    classifier_key = "classifier"
    data_key = "data"
    labels_key = "labels"
    weight_key = "sample_weight"
    path_key = "path"
    errors = []
    sklearn_classifier = False
    classifier = None
    vectorizer = None
    
    if vectorizer_key in json:
        if json[vectorizer_key] == "count":
            encoding = "utf-8"
            decode_error = "strict"
            strip_accents = None
            lowercase = True
            preprocessor = None
            tokenizer = None
            stop_words = None
            token_pattern = "(?u)\b\w\w+\b"
            ngram_range = (1, 1)
            analyzer = "word",
            max_df = 1.0
            min_df = 1
            max_features = None
            vocabulary = None
            binary = False
            vectorizer = CountVectorizer()
        elif json[vectorizer_key] == "tfidf":
            vectorizer = TfidfVectorizer()
        elif classifier_key in json and json[classifier_key] != "cnn":
            errors.append("vectorizer_not_recognized")

    if classifier_key in json:
        if json[classifier_key] == "cnn":
            dsp = json["dev_sample_percentage"] \
                if "dev_sample_percentage" in json else 0.1
            embedding_dim = json["embedding_dim"] \
                if "embedding_dim" in json else 128
            filter_sizes = json["filter_sizes"] \
                if "filter_sizes" in json else "3,4,5"
            num_filters = json["num_filters"] if "num_filters" in json else 128
            dropout_keep_prob = json["dropout_keep_prob"] \
                if "dropout_keep_prob" in json else 0.5
            l2_reg_lambda = json["l2_reg_lambda"] \
                if "l2_reg_lambda" in json else 0.0
            batch_size = json["batch_size"] if "batch_size" in json else 64
            num_epochs = json["num_epochs"] if "num_epochs" in json else 200
            evaluate_every = json["evaluate_every"] \
                if "evaluate_every" in json else 100
            checkpoint_every = json["checkpoint_every"] \
                if "checkpoint_every" in json else 100
            num_checkpoints = json["num_checkpoints"] \
                if "num_checkpoints" in json else 5
            asp = json["allow_soft_placement"] \
                if "allow_soft_placement" in json else True
            ldp = json["log_device_placement"] \
                if "log_device_placement" in json else False
            random_state = json["random_state"] \
                if "random_state" in json else 10
            unlabeled_data = None
            classifier = CNNClassifier(dev_sample_percentage=dsp,
                                       embedding_dim=embedding_dim,
                                       filter_sizes=filter_sizes,
                                       num_filters=num_filters,
                                       dropout_keep_prob=dropout_keep_prob,
                                       l2_reg_lambda=l2_reg_lambda,
                                       batch_size=batch_size,
                                       num_epochs=num_epochs,
                                       evaluate_every=evaluate_every,
                                       checkpoint_every=checkpoint_every,
                                       num_checkpoints=num_checkpoints,
                                       allow_soft_placement=asp,
                                       log_device_placement=ldp,
                                       random_state=random_state,
                                       unlabeled_data=unlabeled_data,
                                       checkpoint_dir=json[path_key])
        elif json[classifier_key] == "rf":
            n_estimators = json["n_estimators"] \
                if "n_estimators" in json else 10
            criterion = json["criterion"] if "criterion" in json else "gini"
            max_depth = json["max_depth"] if "max_depth" in json else None
            mss = json["min_samples_split"] \
                if "min_samples_split" in json else 2
            msl = json["min_samples_leaf"] if "min_samples_leaf" in json else 1
            mwfl = json["min_weight_fraction_leaf"] \
                if "min_weight_fraction_leaf" in json else 0.0
            max_features = json["max_features"] \
                if "max_features" in json else "auto"
            max_leaf_nodes = json["max_leaf_nodes"] \
                if "max_leaf_nodes" in json else None
            mid = json["min_impurity_decrease"] \
                if "min_impurity_decrease" in json else 0.0
            mis = json["min_impurity_split"] \
                if "min_impurity_split" in json else None
            bootstrap = json["bootstrap"] if "bootstrap" in json else True
            oob_score = json["oob_score"] if "oob_score" in json else False
            random_state = json["random_state"] \
                if "random_state" in json else None
            warm_start = json["warm_start"] if "warm_start" in json else False
            class_weight = json["class_weight"] \
                if "class_weight" in json else None
            classifier = RandomForestClassifier(n_estimators=n_estimators,
                                                criterion=criterion,
                                                max_depth=max_depth,
                                                min_samples_split=mss,
                                                min_samples_leaf=msl,
                                                min_weight_fraction_leaf=mwfl,
                                                max_features=max_features,
                                                max_leaf_nodes=max_leaf_nodes,
                                                min_impurity_decrease=mid,
                                                min_impurity_split=mis,
                                                bootstrap=bootstrap,
                                                oob_score=oob_score, n_jobs=-1,
                                                random_state=random_state,
                                                warm_start=warm_start,
                                                class_weight=class_weight)
            sklearn_classifier = True
        elif json[classifier_key] == "svm":
            C = json["C"] if "C" in json else 1.0
            kernel = json["kernel"] if "kernel" in json else "rbf"
            degree = json["degree"] if "degree" in json else 3
            gamma = json["gamma"] if "gamma" in json else "auto"
            coef0 = json["coef0"] if "coef0" in json else 0.0
            shrinking = json["shrinking"] if "shrinking" in json else True
            tol = json["tol"] if "tol" in json else 0.001
            cache_size = json["cache_size"] if "cache_size" in json else 200
            class_weight = json["class_weight"] \
                if "class_weight" in json else None
            max_iter = json["max_iter"] if "max_iter" in json else -1
            decision_function_shape = json["decision_function_shape"] \
                if "decision_function_shape" in json else "ovr"
            random_state = json["random_state"] \
                if "random_state" in json else None
            classifier = SVC(C=C, kernel=kernel, degree=degree, gamma=gamma,
                             coef0=coef0, shrinking=shrinking, tol=tol,
                             cache_size=cache_size, class_weight=class_weight,
                             max_iter=max_iter,
                             decision_function_shape=decision_function_shape,
                             random_state=random_state)
            print(classifier)
            sklearn_classifier = True
        else:
            errors.append("classifier_not_recognized")

        if sklearn_classifier:
            if vectorizer is not None:
                classifier = SKLearnTextClassifier(classifier, vectorizer)
            else:
                errors.append("no_vectorizer_specified")
    else:
        errors.append("no_classifier_specified")
    if classifier is None:
        errors.append("no_classifier")
    if path_key not in json:
        errors.append("no_path")
    if data_key not in json or len(json[data_key]) == 0:
        errors.append("no_data")

    if labels_key not in json or len(json[labels_key]) == 0:
        errors.append("no_labels")
    elif data_key in json and len(json[data_key]) != len(json[labels_key]):
        errors.append("label_count_mismatch")
    if weight_key in json:
      weight = json[weight_key]
    else:
      weight = None
    if data_key in json and weight_key in json \
            and len(json[data_key]) != len(json[weight_key]):
        errors.append("weight_count_mismatch")

    if len(errors) > 0:
        return jsonify(error=errors)

    classifier.fit(json[data_key], json[labels_key], weight)
    if json[classifier_key] != 'cnn':
      with open(os.path.join(json[path_key], 'classify.pkl'), 'wb') as f:
        pickle.dump(classifier, f, protocol=pickle.HIGHEST_PROTOCOL)
    return jsonify(error=errors) if len(errors) > 0 else jsonify(result=True)



@app.route("/")
def hello():
    return "Hello World!"


@app.route("/test", methods=["GET"])
def test():
    return jsonify(a="a", b="b", c="c")


if __name__ == "__main__":
    app.run(host='localhost', port=6666, debug=True)
