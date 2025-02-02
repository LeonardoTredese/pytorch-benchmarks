# *----------------------------------------------------------------------------*
# * Copyright (C) 2023 Politecnico di Torino, Italy                            *
# * SPDX-License-Identifier: Apache-2.0                                        *
# *                                                                            *
# * Licensed under the Apache License, Version 2.0 (the "License");            *
# * you may not use this file except in compliance with the License.           *
# * You may obtain a copy of the License at                                    *
# *                                                                            *
# * http://www.apache.org/licenses/LICENSE-2.0                                 *
# *                                                                            *
# * Unless required by applicable law or agreed to in writing, software        *
# * distributed under the License is distributed on an "AS IS" BASIS,          *
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   *
# * See the License for the specific language governing permissions and        *
# * limitations under the License.                                             *
# *                                                                            *
# * Author:  Matteo Risso <matteo.risso@polito.it>                             *
# *----------------------------------------------------------------------------*

from typing import Tuple
import os
import requests
import numpy as np
import torchvision
import torchvision.transforms as transforms
from pathlib import Path
from torch.utils.data import Dataset, DataLoader, Subset, random_split


def get_data(data_dir=None,
             val_split=0.2,
             perf_samples=False,
             url_tinyml='https://github.com/mlcommons/tiny/raw/master/benchmark/training/',
             file_idxs='image_classification/perf_samples_idxs.npy'
             ) -> Tuple[Dataset, ...]:
    if data_dir is None:
        data_dir = os.path.join(os.getcwd(), 'icl_data')

    transform = transforms.Compose([
        transforms.RandomRotation(15),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.RandomHorizontalFlip(0.5),
        transforms.ToTensor(),
    ])

    test_to_tensor = transforms.Compose([
        transforms.ToTensor()
    ])
    ds_train_val = torchvision.datasets.CIFAR10(root=data_dir, train=True,
                                                download=True, transform=transform)
    ds_test = torchvision.datasets.CIFAR10(root=data_dir, train=False,
                                           download=True, transform=test_to_tensor)

    if perf_samples:
        my_file = Path(data_dir+"/perf_samples_idxs.npy")
        if my_file.is_file():
            print("present")
        else:
            print("not present")
            response = requests.get(url_tinyml + file_idxs)
            response.raise_for_status()
            with open(data_dir+"/perf_samples_idxs.npy", "wb") as f:
                f.write(response.content)
        _idxs = np.load(data_dir+"/perf_samples_idxs.npy")
        ds_test = Subset(ds_test, _idxs)

    val_len = int(val_split * len(ds_train_val))
    train_len = len(ds_train_val) - val_len
    ds_train, ds_val = random_split(ds_train_val, [train_len, val_len])

    return ds_train, ds_val, ds_test


def build_dataloaders(datasets: Tuple[Dataset, ...],
                      batch_size=32,
                      num_workers=2
                      ) -> Tuple[DataLoader, DataLoader, DataLoader]:
    train_set, val_set, test_set = datasets
    train_loader = DataLoader(
        train_set,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
    )
    val_loader = DataLoader(
        val_set,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
    )
    test_loader = DataLoader(
        test_set,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
    )
    return train_loader, val_loader, test_loader
