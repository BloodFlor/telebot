#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
import ssl
import nltk
import json
import urllib
import random
import asyncio
import aiohttp
import requests
import sys, time
from aiohttp import web
from lib.daemon import Daemon
from sklearn.svm import LinearSVC
from lib.bot_config import BOT_CONFIG
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer

class NLU:
    """NLU class."""

    def __init__(self):
        self.dataset = {}
        self.clf_proba = LogisticRegression()
        self.clf = LinearSVC()
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))

    def clear_question(self, question):
        question = question.lower().strip()
        alphabet = ' -1234567890йцукенгшщзхъфывапролджэёячсмитьбю'
        question = ''.join(c for c in question if c in alphabet)
        return question

    def get_dataset(self):
        corpus = []
        y = []
        for intent, intent_data in BOT_CONFIG['intents'].items():
            for example in intent_data['examples']:
                corpus.append(example)
                y.append(intent)

        X = self.vectorizer.fit_transform(corpus)
        self.clf_proba.fit(X, y)
        self.clf.fit(X, y)

        questions = set()

        with open('dataset_nlp/dialogues.txt') as f:
            content = f.read()
        dialogues = content.split('\n\n')

        for dialogue in dialogues:
            replicas = dialogue.split('\n')[:2]
            if len(replicas) == 2:
                question, answer = replicas
                question = self.clear_question(question[2:])
                answer = answer[2:]
                if question and question not in questions:
                    questions.add(question)
                    words = question.split(' ')
                    for word in words:
                        if word not in self.dataset:
                            self.dataset[word] = []
                        self.dataset[word].append([question, answer])

        # dialogues = []
        # dialogues.append([])
        # i = 0
        # j = 0
        # with open('dataset_nlp/subtitle.txt') as f:
        #     content = f.read()
        # for dialogue in content.split('\n'):
        #     if re.match('[a-zA-Z ]', dialogue):
        #         continue
        #     if i == 2:
        #         i = 0
        #         j = j + 1
        #         dialogues.append([])
        #     dialogues[j].append(dialogue)
        #     i = i + 1
        # for dialogue in dialogues:
        #     if len(dialogue) == 2:
        #         question, answer = dialogue
        #         question = self.clear_question(question)
        #         answer = answer
        #         if question and question not in questions:
        #             questions.add(question)
        #             words = question.split(' ')
        #             for word in words:
        #                 if word not in self.dataset:
        #                     self.dataset[word] = []
        #                 self.dataset[word].append([question, answer])

        too_popular = set()
        for word in self.dataset:
            if len(self.dataset[word]) > 30000:
                too_popular.add(word)

        for word in too_popular:
            self.dataset.pop(word)

    def get_intent(self, question):
        best_intent = self.clf.predict(self.vectorizer.transform([question]))[0]
        index_of_best_intent = list(self.clf_proba.classes_).index(best_intent)
        probabilities = self.clf_proba.predict_proba(self.vectorizer.transform([question]))[0]
        best_intent_proba = probabilities[index_of_best_intent]
        return best_intent, best_intent_proba

    def get_answer_by_intent(self, intent):
        phrases = BOT_CONFIG['intents'][intent]['responses']
        return random.choice(phrases)

    def get_generative_answer(self, replica):
            replica = self.clear_question(replica)
            words = replica.split(' ')
            mini_dataset = []
            for word in words:
                if word in self.dataset:
                    mini_dataset += self.dataset[word]
            candidates = []
            for question, answer in mini_dataset:
                if abs(len(question) - len(replica)) / len(question) < 0.4:
                    d = nltk.edit_distance(question, replica)
                    diff = d / len(question)
                    if diff < 0.5:
                        candidates.append([question, answer, diff])
            if candidates:
                winner = min(candidates, key=lambda candidate: candidate[2])
                return winner[1], 1 - diff
            else:
                return None, 0

    def get_failure_phrase(self):
        phrases = BOT_CONFIG['failure_phrases']
        return random.choice(phrases)

    def get_answer(self, question):
        # NLU
        intent, matching = self.get_intent(question)
        if matching > 0.5:
            return self.get_answer_by_intent(intent) + "\n Процент совпадения с nlu:\n" + str(matching)

        # Применяем генеративную модель
        answer, matching = self.get_generative_answer(question)
        if answer and matching > 0.5:
            return answer + "\n Процент совпадения со словарем:\n" + str(matching)

        # Ответ-заглушка
        return self.get_failure_phrase()
