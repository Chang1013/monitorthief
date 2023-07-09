import numpy as np,numpy
import csv
import glob
import os
from sklearn.utils import shuffle
window_size = 100
threshold = 50
slide_size = 10 #less than window_size!!!

def dataimport(path1, path2):

	xx = np.empty([0,window_size,2004],float)
	yy = np.empty([0,3],float)

	###Input data###
	#data import from csv
	input_csv_files = sorted(glob.glob(path1))
	for f in input_csv_files:
		print("input_file_name=",f)
		data = [[ float(elm) for elm in v] for v in csv.reader(open(f, "r"))]
		tmp1 = np.array(data)
		x2 =np.empty([0,window_size,2004],float)

		#data import by slide window
		k = 0
		while k <= (len(tmp1) + 1 - 2 * window_size):
			x = np.dstack(np.array(tmp1[k:k+window_size, 0:2004]).T)
			x2 = np.concatenate((x2, x),axis=0)
			k += slide_size

		xx = np.concatenate((xx,x2),axis=0)
	xx = xx.reshape(len(xx),-1)

	###Annotation data###
	#data import from csv
	annotation_csv_files = sorted(glob.glob(path2))
	for ff in annotation_csv_files:
		print("annotation_file_name=",ff)
		ano_data = [[ str(elm) for elm in v] for v in csv.reader(open(ff,"r"))]
		tmp2 = np.array(ano_data)

		#data import by slide window
		y = np.zeros(((len(tmp2) + 1 - 2 * window_size)//slide_size+1,3))
		k = 0
		while k <= (len(tmp2) + 1 - 2 * window_size):
			y_pre = np.stack(np.array(tmp2[k:k+window_size]))
			RT = 0
			TR = 0
			noactivity = 0
			for j in range(window_size):
				if y_pre[j] == "RT":
					RT += 1
				elif y_pre[j] == "TR":
					TR += 1
				else:
					noactivity += 1

			if RT > window_size * threshold / 100:
				y[int(k/slide_size),:] = np.array([0,1,0])
			elif TR > window_size * threshold / 100:
				y[int(k/slide_size),:] = np.array([0,0,1])
			else:
				y[int(k/slide_size),:] = np.array([2,0,0])
			k += slide_size

		yy = np.concatenate((yy, y),axis=0)
	print(xx.shape,yy.shape)
	return (xx, yy)


#### Main ####
if not os.path.exists("input_files2/"):
        os.makedirs("input_files2/")

for i, label in enumerate (["RT", "TR"]):
	filepath1 = "./trainingset/walk_*" + str(label) + "*.csv"
	filepath2 = "./trainingset/annotation_walk_*" + str(label) + "*.csv"
	outputfilename1 = "./input_files2/xx_" + str(window_size) + "_" + str(threshold) + "_" + label + ".csv"
	outputfilename2 = "./input_files2/yy_" + str(window_size) + "_" + str(threshold) + "_" + label + ".csv"

	x, y = dataimport(filepath1, filepath2)
	with open(outputfilename1, "w") as f:
		writer = csv.writer(f, lineterminator="\n")
		writer.writerows(x)
	with open(outputfilename2, "w") as f:
		writer = csv.writer(f, lineterminator="\n")
		writer.writerows(y)
	print(label + "finish!")
