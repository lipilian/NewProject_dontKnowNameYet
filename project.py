#%% import package
import torch as t
from torch.utils import data
import os
from PIL import Image
import numpy as np

# %% define data loader
class DogCat(data.Dataset):
    def __init__(self, path):
        imgs = os.listdir(path)
        self.imgs = [os.path.join(path, img) for img in imgs]
    def __getitem__(self, index): 
        img_path = self.imgs[index]
        label = 1 if 'dog' in img_path.split('/')[-1] else 0
        img_pil = Image.open(img_path)
        img_array = np.asarray(img_pil)
        img_tensor = t.from_numpy(img_array)
        return img_tensor, label
    def __len__(self):
        return len(self.imgs)
#%% test dataloader
dataset = DogCat('./data/dogcat/')
img, label = dataset[0]
for img, label in dataset:
    print(img.size(), img.float().mean(), label)
# %% torchvision transform 
from torchvision import transforms as T 
transform = T.Compose([
    T.Resize(224),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[.5,.5,.5], std=[.5,.5,.5])
])
# %% update the dog cat class model
class DogCat(data.Dataset):
    def __init__(self, root, transforms = None):
        imgs = os.listdir(root)
        self.imgs = [os.path.join(root, img) for img in imgs]
        self.transforms = transforms
    def __getitem__(self, index):
        img_path = self.imgs[index]
        label = 0 if 'dog' in img_path.split('/')[-1] else 1
        img_pil = Image.open(img_path)
        data = self.transforms(img_pil) if self.transforms else img_pil
        return data, label
    def __len__(self):
        return len(self.imgs)
dataset = DogCat('./data/dogcat/', transforms=transform)
for img,label in dataset:
    print(img.size(), label)


# %% use folder name to seperate the dataset
from torchvision.datasets import ImageFolder 
dataset = ImageFolder('./data/dogcat_2/')
dataset.class_to_idx

# %%
dataset.imgs
# %% add transform to ImageFolder loader 
transform = T.Compose([
    T.RandomResizedCrop(224),
    T.RandomHorizontalFlip(),
    T.ToTensor(),
    T.Normalize(mean=[0.4,0.4,0.4], std=[0.2,0.2,0.2])
])
dataset = ImageFolder('./data/dogcat_2/', transform = transform)

# %% test new ImageFolder loader
dataset[0][0].size()

# %% 每张图都会不一样， 因为transform的原因
to_pil = T.ToPILImage()
to_pil(dataset[0][0]*0.2 + 0.4)

# %% dataLoader 作用于 dataset
from torch.utils.data import DataLoader
dataloader = DataLoader(dataset, batch_size = 3, 
shuffle=True, num_workers = 0, drop_last=False)

#%% iterate 
dataiter = iter(dataloader)
img, label = next(dataiter)
img.size()

# %% 如果有一张图片损坏的情况
# 继承以前的class
class NewDogCat(DogCat):
    def __getitem__(self, index):
        try:
            return super().__getitem__(index)
        except:
            return None, None
from torch.utils.data.dataloader import default_collate
def my_collate_fn(batch):
    batch = list(filter(lambda x:x[0] is not None, batch))
    if len(batch) == 0: return t.Tensor()
    return default_collate(batch)
dataset = NewDogCat('./data/dogcat_wrong/', transforms = transform)
dataset[0]    
# %%
dataloader = DataLoader(dataset, 2, collate_fn = my_collate_fn,num_workers = 0, shuffle = True)
# %%
for batch_data, batch_label in dataloader:
    print(batch_data.size(),batch_label.size())

# %% torchvision 
from torchvision import models
from torch import nn 
resnet34 = models.squeezenet1_1(pretrained=True, num_classes=1000)
resnet34.fc = nn.Linear(512,10)
# %%
from torchvision import datasets
dataset = datasets.MNIST('data/', download=True,
train=False, transform=transform)
# %%
