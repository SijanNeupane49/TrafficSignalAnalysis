#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('git clone https://bitbucket.org/jadslim/german-traffic-signs')


# In[2]:


get_ipython().system('ls german-traffic-signs')


# In[3]:


import numpy as np
import matplotlib.pyplot as plt
import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras.utils.np_utils import to_categorical
from keras.models import Model
from keras.layers import Flatten
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.layers import Dropout
import pickle
import random
import pandas as pd


# In[4]:


np.random.seed(0)


# In[5]:


with open('german-traffic-signs/train.p','rb')as f:
  train_data = pickle.load(f)
with open('german-traffic-signs/valid.p','rb')as f:
  val_data = pickle.load(f)
with open('german-traffic-signs/test.p','rb')as f:
  test_data = pickle.load(f)
print(type(train_data))

X_train, y_train = train_data['features'] , train_data['labels']
X_test, y_test = test_data['features'] , test_data['labels']
X_val, y_val = val_data['features'] , val_data['labels']

print(X_train.shape)


# In[6]:


assert(X_train.shape[0]== y_train.shape[0]), 'This number of images is not equal to the number of labels'
assert(X_test.shape[0]== y_test.shape[0]), 'This number of images is not equal to the number of labels'
assert(X_val.shape[0]== y_val.shape[0]), 'This number of images is not equal to the number of labels'
assert(X_train.shape[1:]== (32,32,3)), 'The dimensions of the images are not 32*32*3'
assert(X_test.shape[1:]== (32,32,3)), 'The dimensions of the images are not 32*32*3'
assert(X_val.shape[1:]== (32,32,3)), 'The dimensions of the images are not 32*32*3'

data = pd.read_csv('german-traffic-signs/signnames.csv')
print(data)


# In[7]:


num_of_samples = []
cols = 5
num_classes = 43
fig, axs = plt.subplots(nrows = num_classes, ncols= cols, figsize= (5,50))
fig.tight_layout()
for i in range(cols):
  for j,row in data.iterrows():
    x_selected = X_train[y_train == j]
    axs[j][i].imshow(x_selected[random.randint(0,len(x_selected -1)), :,:], cmap= plt.get_cmap('gray'))
    axs [j][i].axis('off')
    if i == 2:
      axs[j][i].set_title(str(j)+ '-'+ row['SignName'])
      num_of_samples.append(len(x_selected))


print(num_of_samples)
plt.figure(figsize = (12,4))
plt.bar(range(0, num_classes), num_of_samples)
plt.title('Distribution of the training dataset')
plt.xlabel('Class number')
plt.ylabel('Number of images')


# In[8]:


import cv2
plt.imshow(X_train[1000])
plt.axis('off')
print(X_train[1000].shape)
print(y_train[1000])


# In[9]:


def grayscale(img):
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  return img
img = grayscale(X_train[1000])
plt.imshow(img)
plt.axis('off')
print(img.shape)

def equalize(img):
  img = cv2.equalizeHist(img)
  return img

img = equalize(img)
plt.imshow(img)
plt.axis('off')
print(img.shape)

def preprocessing(img):
  img = grayscale(img)
  img = equalize(img)
  img = img/255
  return img


# In[10]:


X_train = np.array(list(map(preprocessing, X_train)))
X_val = np.array(list(map(preprocessing, X_val)))
X_test = np.array(list(map(preprocessing, X_test)))

plt.imshow(X_train[random.randint(0,len(X_train) -1)])
plt.axis('off')
print(X_train.shape)


# In[11]:


X_train = X_train.reshape(34799,32,32,1)
X_test = X_test.reshape(12630,32,32,1)
X_val = X_val.reshape(4410,32,32,1)


# In[12]:


from keras.preprocessing.image import ImageDataGenerator

datagen = ImageDataGenerator(width_shift_range= 0.1,
                   height_shift_range= 0.1,
                   zoom_range= 0.2,
                   shear_range= 0.1,
                   rotation_range = 10.)
datagen.fit(X_train)

batches = datagen.flow(X_train, y_train, batch_size= 20)
X_batch, y_batch = next(batches)
fig, axs = plt.subplots(1,15, figsize = (20, 5))
fig.tight_layout()

for i in range(15):
  axs[i].imshow(X_batch[i].reshape(32,32))
  axs[i].axis('off')

y_train = to_categorical(y_train, 43)
y_test = to_categorical(y_test, 43)
y_val = to_categorical(y_val, 43)


# In[13]:


def modified_model():
  model = Sequential()
  model.add(Conv2D(60, (5,5), input_shape = (32,32,1),activation = 'relu'))
  model.add(Conv2D(60, (5,5), activation = 'relu'))
  model.add(MaxPooling2D(pool_size = (2,2)))

  model.add(Conv2D(30, (3,3), activation = 'relu'))
  model.add(Conv2D(30, (3,3), activation = 'relu'))
  model.add(MaxPooling2D(pool_size = (2,2)))
  

  model.add(Flatten())
  model.add(Dense(500, activation= 'relu'))
  model.add(Dropout(0.5))
  model.add(Dense(43, activation = 'softmax'))
  # compile model
  model.compile(Adam(lr = 0.001),loss = 'categorical_crossentropy', metrics = ['accuracy'])
  return model


# In[ ]:


model = modified_model()
print(model.summary())

history = model.fit(datagen.flow(X_train, y_train,batch_size = 50),
                              steps_per_epoch =2000, 
                              epochs = 10, 
                              validation_data = (X_val, y_val), shuffle = 1)


# In[ ]:


plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.legend(['training','validation'])
plt.title('Loss')
plt.xlabel('epoch')


# In[ ]:


plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.legend(['training','validation'])
plt.title('Accuracy')
plt.xlabel('epoch')


# In[ ]:


score = model.evaluate(X_test, y_test, verbose = 0)
print('Test Score', score[0])
print('Test Accuracy', score[1])


# In[ ]:


import requests
from PIL import Image
url = 'https://previews.123rf.com/images/pejo/pejo0907/pejo090700003/5155701-german-traffic-sign-no-205-give-way.jpg'
r = requests.get(url, stream=True)
img = Image.open(r.raw)
plt.imshow(img, cmap=plt.get_cmap('gray'))

# Preprocess Image
img = np.asarray(img)
img = cv2.resize(img, (32, 32))
img = preprocessing(img)
plt.imshow(img, cmap = plt.get_cmap('gray'))
print(img.shape)

# Reshape image
img = img.reshape(1,32,32,1)


#Test image
print("predicted sign: "+ str(model.predict_classes(img)))


# In[ ]:




