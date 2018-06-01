# -*- coding: utf-8 -*-
# @System: Ubuntu16
# @Author: Alan Lau
# @Date:   2017-09-13 14:43:03

import json
import keras
from datetime import datetime as dt
import numpy as np
from keras.utils import np_utils
from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Embedding, LSTM, Dropout, Bidirectional, Input, Masking, TimeDistributed
from keras_contrib.layers.crf import CRF


def load(datapath):
    f = open(datapath, 'r')
    data = json.load(f)
    return data['dataset'], data['labels'], dict(data['word_index'])


class revivification:
    def __init__(self, dataset, word_index):
        self.dataset = dataset
        self.word_index = word_index
        self.corpus = []

    def reStore(self):
        for datum in self.dataset:
            sentence = ''.join(list(map(lambda wordindex: next((k for k, v in self.word_index.items(
            ) if v == wordindex), None), list(filter(lambda wordindex: wordindex != 0, datum)))))
            self.corpus.append(sentence)
        return self.corpus


class nn:
    def __init__(self, dataset, labels, wordvocab):
        self.dataset = np.array([np.array(ele) for ele in dataset])
        self.labels = np.array([np.array(ele) for ele in labels])
        self.wordvocab = wordvocab

    def trainingModel(self):
        vocabSize = len(self.wordvocab)
        embeddingDim = 100  # the vector size a word need to be converted
        maxlen = 100  # the size of a sentence vector
        outputDims = 4 + 1
        # embeddingWeights = np.zeros((len(word_index) + 1, EMBEDDING_DIM))
        hiddenDims = 100
        batchSize = 32
        # NUM_CLASS = 4

        train_X = self.dataset
        Y_train = np.array(
            [np_utils.to_categorical(ele, outputDims) for ele in self.labels])

        print(train_X.shape)
        print(Y_train.shape)
        max_features = vocabSize + 1

        word_input = Input(
            shape=(maxlen, ), dtype='float32', name='word_input')
        mask = Masking(mask_value=0.)(word_input)
        word_emb = Embedding(
            max_features, embeddingDim, input_length=maxlen,
            name='word_emb')(mask)
        bilstm1 = Bidirectional(LSTM(hiddenDims,
                                     return_sequences=True))(word_emb)
        #bilstm2 = Bidirectional(LSTM(hiddenDims, return_sequences=True))(bilstm1)
        bilstm_d = Dropout(0.5)(bilstm1)
        dense = TimeDistributed(Dense(outputDims,
                                      activation='softmax'))(bilstm_d)

        crf_layer = CRF(outputDims, sparse_target=False)
        crf = crf_layer(dense)
        model = Model(inputs=[word_input], outputs=[crf])
        model.summary()

        model.compile(
            optimizer='adam',
            loss=crf_layer.loss_function,
            metrics=[crf_layer.accuracy])

        result = model.fit(train_X, Y_train, batch_size=batchSize, epochs=150)

        model.save(
            'PDmodel-crf_epoch_150_batchsize_32_embeddingDim_100_new.h5')

    def save2json(self, json_string, savepath):
        with open(savepath, 'w', encoding='utf8') as f:
            f.write(json_string)
        return "save done."


def main():
    dataset, labels, wordvocab = load(r'PDdata.json')
    # corpus = revivification(dataset, wordvocab).reStore()
    # p(corpus)
    trainLSTM = nn(dataset, labels, wordvocab).trainingModel()


if __name__ == '__main__':
    ts = dt.now()
    main()
    te = dt.now()
    spent = te - ts
    print('[Finished in %s]' % spent)
