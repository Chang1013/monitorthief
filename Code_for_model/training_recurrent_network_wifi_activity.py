from __future__ import print_function
import sklearn as sk
from sklearn.metrics import confusion_matrix
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tensorflow as tf
import tensorflow.compat.v1 as tf 
tf.disable_v2_behavior() 
import numpy as np
import sys
from tensorflow.python.ops import rnn,rnn_cell  
from sklearn.model_selection import KFold, cross_val_score
import csv
from sklearn.utils import shuffle
import os
from sklearn.metrics import classification_report
from cross_vali_input_data_3 import csv_import, DataSet

window_size = 50  
threshold = 20    

# Parameters
learning_rate = 0.0001   
training_iters = 400   
batch_size = 20   
display_step = 10  

# Network Parameters
n_input = 1 
n_steps = window_size 
n_hidden = 100 
n_classes = 3 

#n_steps = window_size 
# Output folder
OUTPUT_FOLDER_PATTERN = "LR{0}_BATCHSIZE{1}_NHIDDEN{2}/"
output_folder = OUTPUT_FOLDER_PATTERN.format(learning_rate, batch_size, n_hidden)
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# tf Graph input
x = tf.placeholder("float", [None, n_steps, n_input])
y = tf.placeholder("float", [None, n_classes])

# Define weights
weights = {
    'out': tf.Variable(tf.random_normal([n_hidden, n_classes]))
}
biases = {
    'out': tf.Variable(tf.random_normal([n_classes]))
}

def RNN(x, weights, biases):

    x = tf.transpose(x, [1, 0, 2])
    x = tf.reshape(x, [-1, n_input])
    x = tf.split(x, n_steps, 0)

    lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(n_hidden, forget_bias=1.0)

    outputs, states = rnn.static_rnn(lstm_cell, x, dtype=tf.float32)
    return tf.matmul(outputs[-1], weights['out']) + biases['out']

##### main #####
pred = RNN(x, weights, biases)

cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits = pred, labels = y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

# Evaluate model
correct_pred = tf.equal(tf.argmax(pred,1), tf.argmax(y,1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

# Initializing the variables
init = tf.global_variables_initializer()
cvscores = []
confusion_sum = [[0 for i in range(3)] for j in range(3)]

#data import
x_TR,x_RT,x_nobody,y_TR,y_RT,y_nobody = csv_import()

print("x_TR=", len(x_TR), " x_RT=", len(x_RT), " x_nobody=", len(x_nobody))

#data shuffle
x_TR,y_TR = shuffle(x_TR, y_TR, random_state=0)
x_RT,y_RT = shuffle(x_RT, y_RT, random_state=0)
x_nobody,y_nobody = shuffle(x_nobody, y_nobody, random_state=0)
#k_fold
kk = 8
# Launch the graph
with tf.Session() as sess:
    for i in range(kk):

        #Initialization
        train_loss = []
        train_acc = []
        validation_loss = []
        validation_acc = []

        #Roll the data
        x_TR = np.roll(x_TR, int(len(x_TR) / kk), axis=0)
        y_TR = np.roll(y_TR, int(len(y_TR) / kk), axis=0)
        x_RT = np.roll(x_RT, int(len(x_RT) / kk), axis=0)
        y_RT = np.roll(y_RT, int(len(y_RT) / kk), axis=0)
        x_nobody = np.roll(x_nobody, int(len(x_nobody) / kk), axis=0)
        y_nobody = np.roll(y_nobody, int(len(y_nobody) / kk), axis=0)
        #data separation
        wifi_x_train = np.r_[ x_TR[int(len(x_TR) / kk):], x_RT[int(len(x_RT) / kk):], x_nobody[int(len(x_nobody) / kk):]]

        wifi_y_train = np.r_[ y_TR[int(len(y_TR) / kk):], y_RT[int(len(y_RT) / kk):], y_nobody[int(len(y_nobody) / kk):]]

        wifi_y_train = wifi_y_train[:,1:]

        wifi_x_validation = np.r_[ x_TR[:int(len(x_TR) / kk)], x_RT[:int(len(x_RT) / kk)], x_nobody[:int(len(x_nobody) / kk)]]

        wifi_y_validation = np.r_[ y_TR[:int(len(y_TR) / kk)], y_RT[:int(len(y_RT) / kk)], y_nobody[:int(len(y_nobody) / kk)]]

        wifi_y_validation = wifi_y_validation[:,1:]

        #data set
        wifi_train = DataSet(wifi_x_train, wifi_y_train)
        wifi_validation = DataSet(wifi_x_validation, wifi_y_validation)
        print(wifi_x_train.shape, wifi_y_train.shape, wifi_x_validation.shape, wifi_y_validation.shape)
        saver = tf.train.Saver()
        sess.run(init)
        step = 1

        # Keep training until reach max iterations
        while step < training_iters:
            batch_x, batch_y = wifi_train.next_batch(batch_size)
            x_vali = wifi_validation.images[:]
            y_vali = wifi_validation.labels[:]
            # Reshape data to get 28 seq of 28 elements
            batch_x = batch_x.reshape((batch_size, n_steps, n_input))
            x_vali = x_vali.reshape((-1, n_steps, n_input))
            # Run optimization op (backprop)
            sess.run(optimizer, feed_dict={x: batch_x, y: batch_y})

            # Calculate batch accuracy
            acc = sess.run(accuracy, feed_dict={x: batch_x, y: batch_y})
            acc_vali = sess.run(accuracy, feed_dict={x: x_vali, y: y_vali})
            # Calculate batch loss
            loss = sess.run(cost, feed_dict={x: batch_x, y: batch_y})
            loss_vali = sess.run(cost, feed_dict={x: x_vali, y: y_vali})

            # Store the accuracy and loss
            train_acc.append(acc)
            train_loss.append(loss)
            validation_acc.append(acc_vali)
            validation_loss.append(loss_vali)

            if step % display_step == 0:
                print("Iter " + str(step) + ", Minibatch Training  Loss= " + \
                    "{:.6f}".format(loss) + ", Training Accuracy= " + \
                    "{:.5f}".format(acc) + ", Minibatch Validation  Loss= " + \
                    "{:.6f}".format(loss_vali) + ", Validation Accuracy= " + \
                    "{:.5f}".format(acc_vali) )
            step += 1

        #Calculate the confusion_matrix
        cvscores.append(acc_vali * 100)
        y_p = tf.argmax(pred, 1)
        val_accuracy, y_pred = sess.run([accuracy, y_p], feed_dict={x: x_vali, y: y_vali})
        y_true = np.argmax(y_vali,1)
        print(sk.metrics.confusion_matrix(y_true, y_pred))
        confusion = sk.metrics.confusion_matrix(y_true, y_pred)
        confusion_sum = confusion_sum + confusion

        #Save the Accuracy curve
        fig = plt.figure(2 * i - 1)
        plt.plot(train_acc)
        plt.plot(validation_acc)
        plt.xlabel("n_epoch")
        plt.ylabel("Accuracy")
        plt.legend(["train_acc","validation_acc"],loc=4)
        plt.ylim([0,1])
        plt.savefig((output_folder + "Accuracy_" + str(i) + ".png"), dpi=150)

        #Save the Loss curve
        fig = plt.figure(2 * i)
        plt.plot(train_loss)
        plt.plot(validation_loss)
        plt.xlabel("n_epoch")
        plt.ylabel("Loss")
        plt.legend(["train_loss","validation_loss"],loc=1)
        plt.ylim([0,2])
        plt.savefig((output_folder + "Loss_" + str(i) + ".png"), dpi=150)

    print("Optimization Finished!")
    print("%.1f%% (+/- %.1f%%)" % (np.mean(cvscores), np.std(cvscores)))
    saver.save(sess, output_folder + "model.ckpt")

    print(classification_report(y_true,y_pred)) #### 
    
    #Save the confusion_matrix
    np.savetxt(output_folder + "confusion_matrix.txt", confusion_sum, delimiter=",", fmt='%d')
    np.savetxt(output_folder + "accuracy.txt", (np.mean(cvscores), np.std(cvscores)), delimiter=".", fmt='%.1f')
