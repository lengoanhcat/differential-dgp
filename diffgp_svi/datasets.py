# Credits to: https://github.com/ICL-SML/Doubly-Stochastic-DGP/

# Copyright 2017 Hugh Salimbeni
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import os
import pandas

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import gzip

import csv


class Dataset(object):
    def __init__(self, name, N, D, type, data_path='/data/'):
        self.data_path = data_path
        self.name, self.N, self.D = name, N, D
        assert type in ['regression', 'classification', 'multiclass']
        self.type = type

    def csv_file_path(self, name):
        subdir = os.getcwd()+'/'+self.data_path+name+"/"
        if not os.path.exists(subdir):
            os.makedirs(subdir)

        return '{}{}.csv'.format(subdir, name)

    def read_data(self):
        data = pandas.read_csv(self.csv_file_path(self.name),
                               header=None, delimiter=',').values
        return {'X':data[:, :-1], 'Y':data[:, -1, None]}

    def download_data(self):
        NotImplementedError

    def get_data(self, seed=0, split=0, prop=0.9):
        path = self.csv_file_path(self.name)
        if not os.path.isfile(path):
            self.download_data()

        full_data = self.read_data()
        split_data = self.split(full_data, seed, split, prop)
        split_data = self.normalize(split_data, 'X')

        if self.type is 'regression':
            split_data = self.normalize(split_data, 'Y')

        return split_data

    def split(self, full_data, seed, split, prop):
        ind = np.arange(self.N)

        np.random.seed(seed + split)
        np.random.shuffle(ind)

        n = int(self.N * prop)

        X = full_data['X'][ind[:n], :]
        Xs = full_data['X'][ind[n:], :]

        Y = full_data['Y'][ind[:n], :]
        Ys = full_data['Y'][ind[n:], :]

        return {'X': X, 'Xs': Xs, 'Y': Y, 'Ys': Ys}

    def normalize(self, split_data, X_or_Y):
        m = np.average(split_data[X_or_Y], 0)[None, :]
        s = np.std(split_data[X_or_Y + 's'], 0)[None, :] + 1e-6

        split_data[X_or_Y] = (split_data[X_or_Y] - m) / s
        split_data[X_or_Y + 's'] = (split_data[X_or_Y + 's'] - m) / s

        split_data.update({X_or_Y + '_mean': m.flatten()})
        split_data.update({X_or_Y + '_std': s.flatten()})
        return split_data


datasets = []
uci_base = 'https://archive.ics.uci.edu/ml/machine-learning-databases/'

class Higgs(Dataset):
    def __init__(self,data_path = "data/"):
        super().__init__('higgs', 11000000, 28, 'classification', data_path)

    def download_data(self):
        url = '{}{}'.format(uci_base, '00280/HIGGS.csv.gz')

        with urlopen(url) as gzipresp:
            with gzip.open(gzipresp,'rb') as f:
                data = pandas.read_csv(f, delimiter=',',header=None)

        cols = data.columns.tolist()
        cols = cols[1:]+[cols[0]]
        data = data[cols].values

        with open(self.csv_file_path(self.name), 'w') as f:
            csv.writer(f).writerows(data)

class Susy(Dataset):
    def __init__(self,data_path = "data/"):
        super().__init__('susy', 5000000, 18, 'classification', data_path)

    def download_data(self):
        url = '{}{}'.format(uci_base, '00279/SUSY.csv.gz')

        with urlopen(url) as gzipresp:
            with gzip.open(gzipresp,'rb') as f:
                data = pandas.read_csv(f, delimiter=',',header=None)

        cols = data.columns.tolist()
        cols = cols[1:]+[cols[0]]
        data = data[cols].values

        with open(self.csv_file_path(self.name), 'w') as f:
            csv.writer(f).writerows(data)


class Boston(Dataset):
    def __init__(self,data_path = "data/"):
        super().__init__('boston', 506, 12, 'regression', data_path)

    def download_data(self):
        url = '{}{}'.format(uci_base, 'housing/housing.data')

        data = pandas.read_fwf(url, header=None).values
        with open(self.csv_file_path(self.name), 'w') as f:
            csv.writer(f).writerows(data)


class Concrete(Dataset):
    def __init__(self,data_path = "data/"):
        super().__init__('concrete', 1030, 8, 'regression', data_path)

    def download_data(self):
        url = '{}{}'.format(uci_base, 'concrete/compressive/Concrete_Data.xls')

        data = pandas.read_excel(url).values
        with open(self.csv_file_path(self.name), 'w') as f:
            csv.writer(f).writerows(data)


class Energy(Dataset):
    def __init__(self,data_path = "data/"):
        super().__init__('energy', 768, 8, 'regression', data_path)

    def download_data(self):
        url = '{}{}'.format(uci_base, '00242/ENB2012_data.xlsx')

        data = pandas.read_excel(url).values

        with open(self.csv_file_path(self.name), 'w') as f:
            csv.writer(f).writerows(data)


class Kin8nm(Dataset):
    def __init__(self,data_path = "data/"):
        super().__init__('kin8nm', 8192, 8, 'regression', data_path)

    def download_data(self):

        url = 'http://mldata.org/repository/data/download/csv/uci-20070111-kin8nm'

        data = pandas.read_csv(url, header=None).values

        with open(self.csv_file_path(self.name), 'w') as f:
            csv.writer(f).writerows(data)


class Naval(Dataset):
    def __init__(self,data_path = "data/"):
        super().__init__('naval', 11934, 12, 'regression', data_path)

    def download_data(self):

        url = '{}{}'.format(uci_base, '00316/UCI%20CBM%20Dataset.zip')

        with urlopen(url) as zipresp:
            with ZipFile(BytesIO(zipresp.read())) as zfile:
                zfile.extractall('/tmp/')

        data = pandas.read_fwf('/tmp/UCI CBM Dataset/data.txt', header=None).values
        data = data[:, :-1]

        with open(self.csv_file_path(self.name), 'w') as f:
            csv.writer(f).writerows(data)


class Power(Dataset):
    def __init__(self,data_path = "data/"):
        super().__init__('power', 9568, 4, 'regression', data_path)

    def download_data(self):
        url = '{}{}'.format(uci_base, '00294/CCPP.zip')
        with urlopen(url) as zipresp:
            with ZipFile(BytesIO(zipresp.read())) as zfile:
                zfile.extractall('/tmp/')

        data = pandas.read_excel('/tmp/CCPP//Folds5x2_pp.xlsx').values

        with open(self.csv_file_path(self.name), 'w') as f:
            csv.writer(f).writerows(data)


class Protein(Dataset):
    def __init__(self,data_path = "data/"):
        super().__init__('protein', 45730, 9, 'regression', data_path)

    def download_data(self):

        url = '{}{}'.format(uci_base, '00265/CASP.csv')

        data = pandas.read_csv(url).values
        data = np.concatenate([data[:, 1:], data[:, 0, None]], 1)

        with open(self.csv_file_path(self.name), 'w') as f:
            csv.writer(f).writerows(data)


class WineRed(Dataset):
    def __init__(self,data_path = "data/"):
        super().__init__('wine_red', 1599, 11, 'regression', data_path)

    def download_data(self):

        url = '{}{}'.format(uci_base, 'wine-quality/winequality-red.csv')

        data = pandas.read_csv(url, delimiter=';').values

        with open(self.csv_file_path(self.name), 'w') as f:
            csv.writer(f).writerows(data)


class WineWhite(Dataset):
    def __init__(self,data_path = "data/"):
        super().__init__('wine_white', 4898, 12, 'regression', data_path)

    def download_data(self):

        url = '{}{}'.format(uci_base, 'wine-quality/winequality-white.csv')

        data = pandas.read_csv(url, delimiter=';').values

        with open(self.csv_file_path(self.name), 'w') as f:
            csv.writer(f).writerows(data)


class Year(Dataset):
    def __init__(self,data_path = "data/"):
        super().__init__('year',  463810, 90, 'regression', data_path)


    def download_data(self):

        url = '{}{}'.format(uci_base, '00203/YearPredictionMSD.txt.zip')

        with urlopen(url) as zipresp:
            with ZipFile(BytesIO(zipresp.read())) as zfile:
                zfile.extractall('/tmp/')

        data = pandas.read_csv('/tmp/YearPredictionMSD.txt', delimiter=',',header=None)
        cols = data.columns.tolist()
        cols = cols[1:]+[cols[0]]
        data = data[cols].values
        data = data[:self.N,]

        with open(self.csv_file_path(self.name), 'w') as f:
            csv.writer(f).writerows(data)

class Datasets(object):
    def __init__(self, data_path='data/'):
        if not os.path.isdir(data_path):
            os.mkdir(data_path)

        datasets = []

        datasets.append(Boston(data_path))
        datasets.append(Concrete(data_path))
        datasets.append(Energy(data_path))
        datasets.append(Kin8nm(data_path))
        datasets.append(Naval(data_path))
        datasets.append(Power(data_path))
        datasets.append(Protein(data_path))
        datasets.append(WineRed(data_path))
        datasets.append(WineWhite(data_path))
        datasets.append(Higgs(data_path))
        datasets.append(Susy(data_path))
        datasets.append(Year(data_path))

        self.all_datasets = {}
        for d in datasets:
            d.data_path = data_path
            self.all_datasets.update({d.name : d})
