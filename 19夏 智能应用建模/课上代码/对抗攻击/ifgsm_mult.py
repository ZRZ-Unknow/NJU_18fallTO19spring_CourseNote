import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from keras.applications.imagenet_utils import decode_predictions
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Conv2D, MaxPool2D, Flatten, Dropout, Dense
import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"       # 使用第二块GPU（从0开始）

mnist = keras.datasets.mnist

(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
train_images=train_images.reshape(-1,28,28,1)/255.0
test_images=test_images.reshape(-1,28,28,1)/255.0

model = Sequential()
model.add(Conv2D(32, (5,5), activation='relu', input_shape=[28, 28, 1]))
model.add(MaxPool2D(pool_size=(2,2)))
model.add(Conv2D(64, (5,5), activation='relu'))
model.add(MaxPool2D(pool_size=(2,2)))
model.add(Flatten())
model.add(Dropout(0.5))
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(10, activation='softmax'))



model.compile(optimizer=tf.train.AdamOptimizer(),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(train_images, train_labels, epochs=1)
test_loss, test_acc = model.evaluate(test_images, test_labels)
print('Test accuracy:', test_acc)

loss_object = tf.keras.losses.CategoricalCrossentropy()

def create(input_image,input_label,target=False):
    temp=np.zeros((1,10))
    temp[0,input_label]=1
    prediction=model(input_image)
    if target==False:
        with tf.GradientTape() as tape:
            tape.watch(input_image)
            loss = loss_object(prediction, temp)
  # Get the gradients of the loss w.r.t to the input image.
        gradient = tf.gradients(loss, input_image)
        signed_grad = tf.sign(gradient)
        return tf.reshape(signed_grad,[1,28,28,1])
    else:
        with tf.GradientTape() as tape:
            tape.watch(input_image)
            loss = loss_object(prediction, temp)
  # Get the gradients of the loss w.r.t to the input image.
        gradient = tf.gradients(-loss, input_image)
        signed_grad = tf.sign(gradient)
        return tf.reshape(signed_grad,[1,28,28,1])

def ifgsm(eps,alpha,image,image_label,n,target=False):
    if n==0:
        return image
    perturbations=create(image,image_label,target)
    adv_x = image + alpha*perturbations
    adv_x = tf.clip_by_value(adv_x, 0, 1)
    return ifgsm(eps,alpha,adv_x,image_label,n-1,target)

epsilons = [0.2]#,0.3,0.1]
alpha=[0.05]#,0.02,0.001]

for (eps,a) in zip(epsilons,alpha):
    test=test_images[0:7,:,:,:]
    for i in range(test.shape[0]):
        image = tf.cast(test[i], tf.float32)
        image = tf.image.resize(image, (28,28))
        image = tf.reshape(image, [28,28,1])
        image = image[None, ...]      #tensor, 1,28,28,1
        adv_x=ifgsm(eps,a,image,test_labels[i],eps//a,target=False)           
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            array=adv_x.eval()
        test[i]=array[0]
    test_acc=model.predict(test, steps=1)
    print(test_acc.argmax(axis=1))
