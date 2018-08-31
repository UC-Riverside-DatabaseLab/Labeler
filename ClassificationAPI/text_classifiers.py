import numpy as np
import os
import tensorflow as tf
import time
from abc import ABC, abstractmethod
from gensim.models.word2vec import Word2Vec, LineSentence
from nltk.tokenize import word_tokenize
from pathlib import Path
from re import sub
from sklearn.base import ClassifierMixin
from tensorflow.contrib.learn import preprocessing


class TextClassifier(ABC, ClassifierMixin):
    def _clean_str(self, string):
        string = sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
        string = sub(r"\'s", " \'s", string)
        string = sub(r"\'ve", " \'ve", string)
        string = sub(r"n\'t", " n\'t", string)
        string = sub(r"\'re", " \'re", string)
        string = sub(r"\'d", " \'d", string)
        string = sub(r"\'ll", " \'ll", string)
        string = sub(r",", " , ", string)
        string = sub(r"!", " ! ", string)
        string = sub(r"\(", " \( ", string)
        string = sub(r"\)", " \) ", string)
        string = sub(r"\?", " \? ", string)
        string = sub(r"\s{2,}", " ", string)
        string = string.strip().lower()
        return string

    @abstractmethod
    def fit(self, X, y, sample_weight=None):
        """Train the classifier on the given training set.

        Parameters:
        X - A list of documents
        y - A list of class labels
        sample_weight - Optional sample weights

        Returns:
        self
        """
        pass

    @abstractmethod
    def predict(self, X):
        """Predict class for X.

        Parameters:
        X - A list of documents

        Returns:
        array of shape = [n_samples, n_classes]
        """
        pass

    @abstractmethod
    def predict_proba(self, X):
        """Predict class probabilities for X.

        Parameters:
        X - A list of documents

        Returns:
        array of shape = [n_samples, n_classes]
        """
        pass


class CNNClassifier(TextClassifier):
    def __init__(self, dev_sample_percentage=0.1, embedding_dim=128,
                 filter_sizes="3,4,5", num_filters=128, dropout_keep_prob=0.5,
                 l2_reg_lambda=0.0, batch_size=64, num_epochs=200,
                 evaluate_every=100, checkpoint_every=100, num_checkpoints=5,
                 allow_soft_placement=True, log_device_placement=False,
                 random_state=10, unlabeled_data=None, checkpoint_dir=None):
        self.__dev_sample_percentage = dev_sample_percentage
        self.__embedding_dim = embedding_dim
        self.__filter_sizes = filter_sizes
        self.__num_filters = num_filters
        self.__dropout_keep_prob = dropout_keep_prob
        self.__l2_reg_lambda = l2_reg_lambda
        self.__batch_size = batch_size
        self.__num_epochs = num_epochs
        self.__evaluate_every = evaluate_every
        self.__checkpoint_every = checkpoint_every
        self.__num_checkpoints = num_checkpoints
        self.__allow_soft_placement = allow_soft_placement
        self.__log_device_placement = log_device_placement
        self.__random_state = random_state
        self.__class_labels = {}
        self.__flags = None
        self.__vocab_proc = None
        self.__checkpoint_dir = checkpoint_dir
        self.__graph = None
        self.__sess = None

        if unlabeled_data is None:
            self.__w2v = None
        else:
            self.__w2v = {}
            path = "./models/w2v_" + unlabeled_data[unlabeled_data.rfind("/") +
                                                    1:] + ".model"

            if Path(path).is_file():
                word2vec = Word2Vec.load(path)
            else:
                word2vec = Word2Vec(LineSentence(unlabeled_data))

                word2vec.save(path)

            for word in word2vec.wv.vocab:
                self.__w2v[word] = word2vec[word]

    def __batch_iter(self, data, batch_size, num_epochs, shuffle=True):
        data = np.array(data)
        data_size = len(data)

        for epoch in range(num_epochs):
            shuffled_data = data[np.random.permutation(np.arange(data_size))] \
                if shuffle else data

            for batch_num in range(int((data_size - 1) / batch_size) + 1):
                start_index = batch_num * batch_size
                end_index = min((batch_num + 1) * batch_size, data_size)
                yield shuffled_data[start_index:end_index]

    def fit(self, X, y, sample_weights=None):
        self.__class_labels.clear()
        self.__define_flags()

        self.classes_ = sorted(list(set(y)))
        x_text, y = self.__transform_data(X, y, sample_weights)
        max_doc_length = max([len(x.split(" ")) for x in x_text])
        self.__vocab_proc = preprocessing.VocabularyProcessor(max_doc_length)
        x = np.array(list(self.__vocab_proc.fit_transform(x_text)))

        np.random.seed(self.__random_state)

        shuffle_indices = np.random.permutation(np.arange(len(y)))
        x_shuffled = x[shuffle_indices]
        y_shuffled = y[shuffle_indices]
        dev_sample_index = -1 * int(self.__flags.dev_sample_percentage *
                                    float(len(y)))
        x_train = x_shuffled[:dev_sample_index]
        x_dev = x_shuffled[dev_sample_index:]
        y_train = y_shuffled[:dev_sample_index]
        y_dev = y_shuffled[dev_sample_index:]

        with tf.Graph().as_default():
            asp = self.__flags.allow_soft_placement
            ldp = self.__flags.log_device_placement
            session_conf = tf.ConfigProto(allow_soft_placement=asp,
                                          log_device_placement=ldp)
            sess = tf.Session(config=session_conf)

            with sess.as_default():
                vocab_size = len(self.__vocab_proc.vocabulary_)
                embedding_size = self.__flags.embedding_dim
                filter_sizes = self.__flags.filter_sizes.split(",")
                filter_sizes = list(map(int, filter_sizes))
                cnn = self.__TextCNN(sequence_length=x_train.shape[1],
                                     num_classes=y_train.shape[1],
                                     vocab_size=vocab_size,
                                     embedding_size=embedding_size,
                                     filter_sizes=filter_sizes,
                                     num_filters=self.__flags.num_filters,
                                     l2_reg_lambda=self.__flags.l2_reg_lambda,
                                     word2vec=self.__w2v)
                global_step = tf.Variable(0, name="global_step",
                                          trainable=False)
                optimizer = tf.train.AdamOptimizer(1e-3)
                grads_and_vars = optimizer.compute_gradients(cnn.loss)
                train_op = optimizer.apply_gradients(grads_and_vars,
                                                     global_step=global_step)
                grad_summaries = []

                for g, v in grads_and_vars:
                    if g is not None:
                        name = v.name.replace(":", "_")
                        histogram = "{}/grad/hist".format(name)
                        grad_hist_summary = tf.summary.histogram(histogram, g)
                        sparsity = "{}/grad/sparsity".format(name)
                        frac = tf.nn.zero_fraction(g)
                        sparsity_summary = tf.summary.scalar(sparsity, frac)

                        grad_summaries.append(grad_hist_summary)
                        grad_summaries.append(sparsity_summary)

                grad_summaries_merged = tf.summary.merge(grad_summaries)
                timestamp = str(int(time.time()))
                out_dir = os.path.abspath(os.path.join(os.path.curdir, "runs",
                                                       timestamp))
                loss_summary = tf.summary.scalar("loss", cnn.loss)
                acc_summary = tf.summary.scalar("accuracy", cnn.accuracy)
                train_summary_op = tf.summary.merge([loss_summary, acc_summary,
                                                     grad_summaries_merged])
                train_summary_dir = os.path.join(out_dir, "summaries", "train")
                train_summary_writer = tf.summary.FileWriter(train_summary_dir,
                                                             sess.graph)
                dev_summary_op = tf.summary.merge([loss_summary, acc_summary])
                dev_summary_dir = os.path.join(out_dir, "summaries", "dev")
                dev_summary_writer = tf.summary.FileWriter(dev_summary_dir,
                                                           sess.graph)
                path = os.path.join(out_dir, "checkpoints")
                self.__checkpoint_dir = os.path.abspath(path)
                checkpoint_prefix = os.path.join(self.__checkpoint_dir,
                                                 "model")

                if not os.path.exists(self.__checkpoint_dir):
                    os.makedirs(self.__checkpoint_dir)

                max_to_keep = self.__flags.num_checkpoints
                saver = tf.train.Saver(tf.global_variables(),
                                       max_to_keep=max_to_keep)

                sess.run(tf.global_variables_initializer())

                batches = self.__batch_iter(list(zip(x_train, y_train)),
                                            self.__flags.batch_size,
                                            self.__flags.num_epochs)

                for batch in batches:
                    x_batch, y_batch = zip(*batch)

                    self.__train_step(x_batch, y_batch, cnn, sess,
                                      self.__flags.dropout_keep_prob, train_op,
                                      global_step, train_summary_op,
                                      train_summary_writer)

                    current_step = tf.train.global_step(sess, global_step)

                    if current_step % self.__flags.evaluate_every == 0:
                        self.__dev_step(x_dev, y_dev, cnn, sess, global_step,
                                        dev_summary_op,
                                        writer=dev_summary_writer)

                    if current_step % self.__flags.checkpoint_every == 0:
                        saver.save(sess, checkpoint_prefix,
                                   global_step=current_step)

        self.__complete_training()
        return self

    def __complete_training(self):
        checkpoint_file = tf.train.latest_checkpoint(self.__checkpoint_dir)
        self.__graph = tf.Graph()

        with self.__graph.as_default():
            asp = self.__flags.allow_soft_placement
            ldp = self.__flags.log_device_placement
            session_conf = tf.ConfigProto(allow_soft_placement=asp,
                                          log_device_placement=ldp)
            self.__sess = tf.Session(config=session_conf)

            with self.__sess.as_default():
                meta_graph = "{}.meta".format(checkpoint_file)
                saver = tf.train.import_meta_graph(meta_graph)

                saver.restore(self.__sess, checkpoint_file)

    def __dev_step(self, x_batch, y_batch, cnn, sess, global_step,
                   dev_summary_op, writer=None):
        feed_dict = {cnn.input_x: x_batch, cnn.input_y: y_batch,
                     cnn.dropout_keep_prob: 1.0}
        step, summaries, loss, accuracy = sess.run([global_step,
                                                    dev_summary_op, cnn.loss,
                                                    cnn.accuracy], feed_dict)

        if writer:
            writer.add_summary(summaries, step)

    def __define_flags(self):
        tf.flags._global_parser = tf.flags._argparse.ArgumentParser()
        tf.flags.DEFINE_float("dev_sample_percentage",
                              self.__dev_sample_percentage,
                              "Percentage of the data to use for validation")
        tf.flags.DEFINE_integer("embedding_dim", self.__embedding_dim,
                                "Dimensionality of character embedding")
        tf.flags.DEFINE_string("filter_sizes", self.__filter_sizes,
                               "Comma-separated filter sizes")
        tf.flags.DEFINE_integer("num_filters", self.__num_filters,
                                "Number of filters per filter size")
        tf.flags.DEFINE_float("dropout_keep_prob", self.__dropout_keep_prob,
                              "Dropout keep probability")
        tf.flags.DEFINE_float("l2_reg_lambda", self.__l2_reg_lambda,
                              "L2 regularization lambda")
        tf.flags.DEFINE_integer("batch_size", self.__batch_size, "Batch Size")
        tf.flags.DEFINE_integer("num_epochs", self.__num_epochs,
                                "Number of training epochs")
        tf.flags.DEFINE_integer("evaluate_every", self.__evaluate_every,
                                "Evaluate on dev set after this many steps")
        tf.flags.DEFINE_integer("checkpoint_every", self.__checkpoint_every,
                                "Save model after this many steps")
        tf.flags.DEFINE_integer("num_checkpoints", self.__num_checkpoints,
                                "Number of checkpoints to store")
        tf.flags.DEFINE_boolean("allow_soft_placement",
                                self.__allow_soft_placement,
                                "Allow device soft device placement")
        tf.flags.DEFINE_boolean("log_device_placement",
                                self.__log_device_placement,
                                "Log placement of ops on devices")
        tf.flags.DEFINE_string("checkpoint_dir", "",
                               "Checkpoint directory from training run")
        tf.flags.DEFINE_boolean("eval_train", False,
                                "Evaluate on all training data")
        tf.flags.FLAGS._parse_flags()

        self.__flags = tf.flags.FLAGS

    def predict(self, X):
        X = self.__transform_data(X)
        x_test = np.array(list(self.__vocab_proc.transform(X)))
        input_x = self.__graph.get_operation_by_name("input_x").outputs[0]
        name = "dropout_keep_prob"
        dkp = self.__graph.get_operation_by_name(name).outputs[0]
        name = "output/predictions"
        predictions = self.__graph.get_operation_by_name(name).outputs[0]
        batches = self.__batch_iter(list(x_test), self.__flags.batch_size, 1,
                                    shuffle=False)
        all_predictions = []

        for x_test_batch in batches:
            batch_predictions = self.__sess.run(predictions,
                                                {input_x: x_test_batch,
                                                 dkp: 1.0})
            all_predictions = np.concatenate([all_predictions,
                                              batch_predictions])

        return [self.__class_labels[pred] for pred in all_predictions]

    def predict_proba(self, X):
        probabilities = []
        class_range = range(len(self.classes_))

        for pred in self.predict(X):
            dist = [1 if self.classes_[i] == pred else 0 for i in class_range]

            probabilities.append(dist)

        return probabilities

    def __train_step(self, x_batch, y_batch, cnn, sess, dropout_keep_prob,
                     train_op, global_step, train_summary_op,
                     train_summary_writer):
        feed_dict = {cnn.input_x: x_batch, cnn.input_y: y_batch,
                     cnn.dropout_keep_prob: dropout_keep_prob}
        _, step, summaries, loss, accuracy = sess.run([train_op, global_step,
                                                       train_summary_op,
                                                       cnn.loss, cnn.accuracy],
                                                      feed_dict)

        train_summary_writer.add_summary(summaries, step)

    def __transform_data(self, X, y=None, sample_weight=None):
        x_text = []

        if y is not None:
            class_labels = {}
            y_cnn = []

            for i in range(len(self.classes_)):
                cnn_label = []

                for j in range(len(self.classes_)):
                    cnn_label.append(1 if i == j else 0)

                class_labels[self.classes_[i]] = cnn_label

        for i in range(len(X)):
            document = self._clean_str(X[i])

            if self.__w2v is not None:
                tokenized = word_tokenize(document)
                outstring = [w for w in tokenized if w in self.__w2v.keys()]
                document = " ".join(outstring)

            n_copies = 1 if sample_weight is None else round(sample_weight[i])
            x_text += [document] * n_copies

            if y is not None:
                y_cnn += [class_labels[y[i]]] * n_copies

        if y is not None:
            for class_label, cnn_label in class_labels.items():
                self.__class_labels[np.argmax(cnn_label)] = class_label

            return x_text, np.array(y_cnn)

        return x_text

    class __TextCNN(object):
        def __init__(self, sequence_length, num_classes, vocab_size,
                     embedding_size, filter_sizes, num_filters,
                     l2_reg_lambda=0.0, word2vec=None):
            self.input_x = tf.placeholder(tf.int32, [None, sequence_length],
                                          name="input_x")
            self.input_y = tf.placeholder(tf.float32, [None, num_classes],
                                          name="input_y")
            self.dropout_keep_prob = tf.placeholder(tf.float32,
                                                    name="dropout_keep_prob")
            l2_loss = tf.constant(0.0)

            with tf.device('/cpu:0'), tf.name_scope("embedding"):
                if word2vec is None:
                    shape = [vocab_size, embedding_size]
                    initial_value = tf.random_uniform(shape, -1.0, 1.0)
                    self.W = tf.Variable(initial_value, name="W")
                else:
                    values = []

                    for value in word2vec.values():
                        values.append(value)

                    embedding_size = len(values[0])
                    stack_values = np.array([embedding_size * [0]] + values,
                                            dtype=np.float32)
                    initial_value = tf.stack(stack_values)
                    self.W = tf.Variable(initial_value, name="W")

                embedded_chars = tf.nn.embedding_lookup(self.W, self.input_x)
                self.__embedded_chars_expanded = tf.expand_dims(embedded_chars,
                                                                -1)

            pooled_outputs = []

            for i, filter_size in enumerate(filter_sizes):
                with tf.name_scope("conv-maxpool-%s" % filter_size):
                    W = tf.Variable(tf.truncated_normal([filter_size,
                                                         embedding_size, 1,
                                                         num_filters],
                                    stddev=0.1), name="W")
                    b = tf.Variable(tf.constant(0.1, shape=[num_filters]),
                                    name="b")
                    conv = tf.nn.conv2d(self.__embedded_chars_expanded, W,
                                        strides=[1, 1, 1, 1], padding="VALID",
                                        name="conv")
                    h = tf.nn.relu(tf.nn.bias_add(conv, b), name="relu")
                    ksize = [1, sequence_length - filter_size + 1, 1, 1]
                    pooled = tf.nn.max_pool(h, ksize=ksize,
                                            strides=[1, 1, 1, 1],
                                            padding='VALID', name="pool")

                    pooled_outputs.append(pooled)

            num_filters_total = num_filters * len(filter_sizes)
            self.h_pool = tf.concat(pooled_outputs, 3)
            self.h_pool_flat = tf.reshape(self.h_pool, [-1, num_filters_total])

            with tf.name_scope("dropout"):
                self.h_drop = tf.nn.dropout(self.h_pool_flat,
                                            self.dropout_keep_prob)

            with tf.name_scope("output"):
                initializer = tf.contrib.layers.xavier_initializer()
                W = tf.get_variable("W", shape=[num_filters_total,
                                                num_classes],
                                    initializer=initializer)
                b = tf.Variable(tf.constant(0.1, shape=[num_classes]),
                                name="b")
                l2_loss += tf.nn.l2_loss(W)
                l2_loss += tf.nn.l2_loss(b)
                self.scores = tf.nn.xw_plus_b(self.h_drop, W, b, name="scores")
                self.predictions = tf.argmax(self.scores, 1,
                                             name="predictions")

            with tf.name_scope("loss"):
                logits = self.scores
                labels = self.input_y
                losses = tf.nn.softmax_cross_entropy_with_logits(logits=logits,
                                                                 labels=labels)
                self.loss = tf.reduce_mean(losses) + l2_reg_lambda * l2_loss

            with tf.name_scope("accuracy"):
                correct_predictions = tf.equal(self.predictions,
                                               tf.argmax(self.input_y, 1))
                self.accuracy = tf.reduce_mean(tf.cast(correct_predictions,
                                                       "float"),
                                               name="accuracy")


class EnsembleTextClassifier(TextClassifier):
    """Combines output of multiple text classifiers based on a user-selected
    combination method.

    Constructor parameters:
    voting_method (default majority) - The combination method to use
    weight_penalty (default 4) - If > 0, apply a weight to each classifier's
    output based on its accuracy. Higher numbers increase the penalty for lower
    accuracy.
    """
    def __init__(self, voting_method="average", weight_penalty=4):
        self.__classifiers = []
        self.__classifier_weights = []
        self.__voting_method = voting_method
        self.__weight_penalty = weight_penalty

    def add_classifier(self, classifier):
        self.__classifiers.append(classifier)
        self.__classifier_weights.append(1)

    def fit(self, X, y, sample_weight=None):
        self.classes_ = sorted(list(set(y)))

        if self.__weight_penalty > 0:
            training_set_size = round(0.9 * len(X))
            validation_set = X[training_set_size:]
            X = X[:training_set_size]
            y = y[:training_set_size]

            if sample_weight is not None:
                sample_weight = sample_weight[:training_set_size]

        for classifier in self.__classifiers:
            classifier.fit(X, y, sample_weight)

        if self.__weight_penalty > 0:
            for i in range(len(self.__classifiers)):
                key = "weightedaccuracy"
                acc = self.__classifiers[i].evaluate(validation_set)[key]
                self.__classifier_weights[i] = pow(acc, self.__weight_penalty)

        return self

    def predict(self, X):
        dist = self.predict_proba(X)
        return [self.classes_[np.argmax(dist[i, :])] for i in range(len(X))]

    def predict_proba(self, X):
        if self.voting_method == "average":
            return self.__average(X)
        elif self.voting_method == "majority":
            return self.__majority(X)
        elif self.voting_method == "maximum":
            return self.__maximum(X)
        elif self.voting_method == "median":
            return self.__median(X)
        elif self.voting_method == "product":
            return self.__product(X)

    def __average(self, X):
        distributions = np.zeros((len(X), len(self.classes_)))

        for i in range(len(self.__classifiers)):
            classifier = self.__classifiers[i]
            predictions = classifier.predict_proba(X)
            predictions = predictions * self.__classifier_weights[i]
            predictions = self.__rearrange(predictions, classifier.classes_)
            distributions = distributions + predictions

        return distributions / sum(self.__classifier_weights)

    def __majority(self, X):
        sum_votes = np.zeros((len(X), len(self.classes_)))

        for i in range(len(self.__classifiers)):
            pred = self.__classifiers[i].predict(X)

            for j in range(len(pred)):
                for k in range(len(self.classes_)):
                    if self.classes_[k] == pred[j]:
                        sum_votes[j, k] = self.__classifier_weights[i]
                    else:
                        sum_votes[j, k] = 0

        return sum_votes / sum(self.__classifier_weights)

    def __maximum(self, X):
        distributions = np.zeros((len(X), len(self.classes_)))

        for i in range(len(self.__classifiers)):
            classifier = self.__classifiers[i]
            predictions = classifier.predict_proba(X)
            predictions = self.__rearrange(predictions, classifier.classes_)
            distributions = np.maximum(distributions, predictions)

        sum_dists = np.sum(distributions, axis=1)

        for i in range(distributions.shape[1]):
            distributions[:, i] = np.divide(distributions[:, i], sum_dists)

        return distributions

    def __median(self, X):
        distributions = np.zeros((len(X), len(self.classes_)))
        cl_dist = []

        for i in range(len(self.__classifiers)):
            classifier = self.__classifiers[i]
            predictions = classifier.predict_proba(X)
            predictions = predictions * self.__classifier_weights[i]
            predictions = self.__rearrange(predictions, classifier.classes_)

            cl_dist.append(predictions)

        for i in range(distributions.shape[0]):
            for j in range(distributions.shape[1]):
                probs = sorted([cl_dist[k][i, j] for k in range(len(cl_dist))])
                mid = int(len(probs) / 2)

                if len(probs) % 2 == 0:
                    distributions[i, j] = np.average(probs[mid:mid + 2])
                else:
                    distributions[i, j] = probs[mid]

        sum_dists = np.sum(distributions, axis=1)

        for i in range(distributions.shape[1]):
            distributions[:, i] = np.divide(distributions[:, i], sum_dists)

        return distributions

    def __product(self, X):
        distributions = np.ones((len(X), len(self.classes_)))

        for i in range(len(self.__classifiers)):
            classifier = self.__classifiers[i]
            predictions = classifier.predict_proba(X)
            predictions = predictions * self.__classifier_weights[i]
            predictions = self.__rearrange(predictions, classifier.classes_)
            distributions = distributions * predictions

        sum_dists = np.sum(distributions, axis=1)

        for i in range(distributions.shape[1]):
            distributions[:, i] = np.divide(distributions[:, i], sum_dists)

        return distributions

    def __rearrange(self, matrix, classes):
        if self.classes_ != classes:
            indexes = []

            for class_value in range(len(self.classes_)):
                for j in range(len(classes)):
                    if classes[j] == class_value:
                        indexes.append(j)
                        break

            matrix[:, list(range(len(self.classes_)))] = matrix[:, indexes]

        return matrix


class SKLearnTextClassifier(TextClassifier):
    """Wrapper class for sklearn vectorizers and classifiers."""
    def __init__(self, classifier, vectorizer):
        self.__classifier = classifier
        self.__vectorizer = vectorizer

    def fit(self, X, y, sample_weight=None):
        X = self.__vectorizer.fit_transform([self._clean_str(x) for x in X])

        self.__classifier.fit(X, y, sample_weight)

        self.classes_ = self.__classifier.classes_
        return self

    def predict(self, X):
        X = self.__vectorizer.transform([self._clean_str(x) for x in X])
        return self.__classifier.predict(X)

    def predict_log_proba(self, X):
        """Predict class log-probabilities for X.

        Parameters:
        X - A list of documents

        Returns:
        array of shape = [n_samples, n_classes]
        """
        X = self.__vectorizer.transform([self._clean_str(x) for x in X])
        return self.__classifier.predict_log_proba(X)

    def predict_proba(self, X):
        X = self.__vectorizer.transform([self._clean_str(x) for x in X])
        return self.__classifier.predict_proba(X)
