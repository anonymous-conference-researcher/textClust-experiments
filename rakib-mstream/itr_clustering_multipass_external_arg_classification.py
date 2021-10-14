#from read_clust_label import readClustLabel
from combine_predtruetext import combinePredTrueText
from groupTxt_ByClass import groupTxtByClass
#from word_vec_extractor import populateTermVecs
from nltk.tokenize import word_tokenize
from sent_vecgenerator import generate_sent_vecs_toktextdata
from generate_TrainTestTxtsTfIdf import comPrehensive_GenerateTrainTestTxtsByOutliersTfIDf
from generate_TrainTestVectorsTfIdf import generateTrainTestVectorsTfIDf
from sklearn.linear_model import LogisticRegression
from time import time
from sklearn import metrics
from nltk.corpus import stopwords
from txt_process_util import processTxtRemoveStopWordTokenized
import re
import numpy as np
import random
import sys
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from outlier_detection_sd import detect_outlier_sd_vec
from compute_util import MultiplyTwoSetsOneToOne
import os
from read_pred_true_text import ReadPredTrueText
from print_cluster_evaluation import printClusterEvaluation_file
from write_pred_true_texts import writePredTrueTexts

def WriteTrainTest(listtuple_pred_true_text, outFileName):
 file2=open(outFileName,"w")
 for i in range(len(listtuple_pred_true_text)):
  file2.write(listtuple_pred_true_text[i][0]+"\t"+listtuple_pred_true_text[i][1]+"\t"+listtuple_pred_true_text[i][2]+"\n")

 file2.close()
 
#def MergeAndWriteTrainTest():
# print(extClustFile)
# clustlabels=readClustLabel(extClustFile)
# listtuple_pred_true_text, uniqueTerms=combinePredTrueText(clustlabels, dataFileTxtTrue)
# writePredTrueTexts(traintestFile, listtuple_pred_true_text)
# return listtuple_pred_true_text 


def WriteTextsOfEachGroup(labelDir, dic_tupple_class):
 labelNames=[]
 for label, value in dic_tupple_class.items():
  labelFile = labelDir+label
  labelNames.append(label)  
  file1=open(labelFile,"w")
  for pred_true_txt in value:
    file1.write(pred_true_txt[0]+"\t"+pred_true_txt[1]+"\t"+pred_true_txt[2]+"\n")
  file1.close()
 return labelNames 

def Gen_WriteOutliersEachGroup(labelDir, numberOfClusters, labelNames):
 dic_label_outliers = {}
 
 #get files in labelDir
 #end 
 
 for labelName in labelNames:
  fileId = labelName #labelID +1  
  labelFile = labelDir+fileId
  file1=open(labelFile,"r")
  lines = file1.readlines()
  file1.close()
  
  train_data = []
  train_labels = []
  train_trueLabels = []

  for line in lines:
   line=line.lower().strip() 
   arr = re.split("\t", line)
   train_data.append(arr[2])
   train_labels.append(arr[0])
   train_trueLabels.append(arr[1])

  vectorizer = TfidfVectorizer( max_df=1.0, min_df=1, stop_words='english', use_idf=True, smooth_idf=True, norm='l2')
  x_train = vectorizer.fit_transform(train_data)

  contratio = 0.1
  isf = IsolationForest(n_estimators=100, max_samples='auto', contamination=contratio, max_features=1.0, bootstrap=True, verbose=0, random_state=0, behaviour='new')
  #isf=IsolationForest(n_estimators=100, max_samples='auto', contamination=contratio, max_features=1.0, bootstrap=True, verbose=0, random_state=0)
  outlierPreds = isf.fit(x_train).predict(x_train)
  dic_label_outliers[str(fileId)] = outlierPreds  #real
  
  #dense_x_train = x_train.toarray()
  #outlierPreds_sd = detect_outlier_sd_vec(dense_x_train, 0.1)
  #outlierPredsMult = MultiplyTwoSetsOneToOne(outlierPreds, outlierPreds_sd)
  #outlierPreds=outlierPreds_sd
  #dic_label_outliers[str(fileId)] = outlierPreds #outlierPreds_sd #outlierPredsMult

  file1=open(labelDir+str(fileId)+"_outlierpred","w")
  for pred in outlierPreds:
   file1.write(str(pred)+"\n") 
 
  file1.close()
 
 return dic_label_outliers
 
def GenerateTrainTest2_Percentage(percentTrainData, traintestFile, numberOfClusters, textsperlabelDir, trainFile, testFile):
 trainDataRatio = 1.0
		
 listtuple_pred_true_text = ReadPredTrueText(traintestFile)
 perct_tdata = percentTrainData/100
 goodAmount_txts = int(perct_tdata*(len(listtuple_pred_true_text)/numberOfClusters))			
 dic_tupple_class=groupTxtByClass(listtuple_pred_true_text, False)		
 #write texts of each group in  
 labelNames=WriteTextsOfEachGroup(textsperlabelDir,dic_tupple_class)
 dic_label_outliers = Gen_WriteOutliersEachGroup(textsperlabelDir, numberOfClusters, labelNames)

 train_pred_true_txts = []
 test_pred_true_txts = []

 for label, pred_true_txt in dic_tupple_class.items():
  outlierpreds = dic_label_outliers[str(label)]
  pred_true_txts = dic_tupple_class[str(label)]

  if len(outlierpreds)!= len(pred_true_txts):
   print("Size not match for="+str(label))
  
  outLiers_pred_true_txt = []
  count = -1
  for outPred in outlierpreds:
   outPred = str(outPred)
   count=count+1
   if outPred=="-1":
    outLiers_pred_true_txt.append(pred_true_txts[count])

  test_pred_true_txts.extend(outLiers_pred_true_txt)
  #remove outlierts insts from pred_true_txts
  pred_true_txts_good = [e for e in pred_true_txts if e not in outLiers_pred_true_txt]
  dic_tupple_class[str(label)]=pred_true_txts_good

  
 for label, pred_true_txt in dic_tupple_class.items():
  pred_true_txts = dic_tupple_class[str(label)] 
  pred_true_txt_subs= []
  numTrainGoodTexts=int(perct_tdata*len(pred_true_txts))
  if len(pred_true_txts) > goodAmount_txts:
   pred_true_txt_subs.extend(pred_true_txts[0:goodAmount_txts])
   test_pred_true_txts.extend(pred_true_txts[goodAmount_txts:len(pred_true_txts)]) 
  else:
   pred_true_txt_subs.extend(pred_true_txts)
  train_pred_true_txts.extend(pred_true_txt_subs)
 
 trainDataRatio = float(len(train_pred_true_txts))/float(len(train_pred_true_txts+test_pred_true_txts))
 print("trainDataRatio="+str(trainDataRatio))
 #if trainDataRatio<=maxTrainRatio:
 writePredTrueTexts(trainFile,train_pred_true_txts)
 writePredTrueTexts(testFile,test_pred_true_txts) 
   		
 return trainDataRatio
 
def PerformClassification(trainFile, testFile, traintestFile):
 file=open(trainFile,"r")
 lines = file.readlines()
 #np.random.seed(0)
 np.random.shuffle(lines)
 file.close()

 train_data = []
 train_labels = []
 train_trueLabels = []

 for line in lines:
  line=line.strip().lower() 
  arr = re.split("\t", line)
  train_data.append(arr[2])
  train_labels.append(arr[0]) #train_labels.append(arr[0])
  train_trueLabels.append(arr[1])
 
 file=open(testFile,"r")
 lines = file.readlines()
 file.close()

 test_data = []
 test_labels = []

 for line in lines:
  line=line.strip().lower() 
  arr = re.split("\t", line)
  test_data.append(arr[2])
  test_labels.append(arr[1])

 vectorizer = TfidfVectorizer( max_df=1.0, min_df=1, stop_words='english', use_idf=True, smooth_idf=True, norm='l2')
 X_train = vectorizer.fit_transform(train_data)
 X_test = vectorizer.transform(test_data)
 
 clf = LogisticRegression(solver='lbfgs', multi_class='auto') #52
 #clf = LogisticRegression() #52
 #t0 = time()
 clf.fit(X_train, train_labels)
 #train_time = time() - t0
 #print ("train time: %0.3fs" % train_time)

 #t0 = time()
 pred = clf.predict(X_test)
 #test_time = time() - t0
 #print ("test time:  %0.3fs" % test_time)

 y_test = [int(i) for i in test_labels]
 pred_test = [int(i) for i in pred]
 #score = metrics.homogeneity_score(y_test, pred_test)
 #print ("homogeneity_score-test-data:   %0.4f" % score)
 #score = metrics.normalized_mutual_info_score(y_test, pred_test)  
 #print ("nmi_score-test-data:   %0.4f" % score) 
 
 file=open(traintestFile,"w")
 for i in range(len(train_labels)):
  file.write(train_labels[i]+"\t"+train_trueLabels[i]+"\t"+train_data[i]+"\n")

 for i in range(len(test_labels)):
  file.write(pred[i]+"\t"+test_labels[i]+"\t"+test_data[i]+"\n")
 
 file.close() 

def GenerateTrainTest2List(listtuple_pred_true_text, minPercent, maxPercent, percentIncr, maxIterations, traintestFile, numberOfClusters, textsperlabelDir,
trainFile, testFile):
  print("Initial---------")
  printClusterEvaluation_file(traintestFile)

  if percentIncr==-1:
    for itr in range(maxIterations):
      randPercent=random.uniform(minPercent,maxPercent)
      trainDataRatio = GenerateTrainTest2_Percentage(randPercent, traintestFile, numberOfClusters, textsperlabelDir, trainFile, testFile);
      print(str(itr)+","+str(randPercent))
      PerformClassification(trainFile, testFile, traintestFile)
      printClusterEvaluation_file(traintestFile) 
  else:
    prevPercent=minPercent
    for itr in range(maxIterations):
      randPercent=random.randint(minPercent,maxPercent)
      absPercentDiff = abs(randPercent-prevPercent)
      if absPercentDiff<percentIncr:
        if randPercent >= prevPercent:
          randPercent = min(randPercent+percentIncr, maxPercent)
        elif randPercent < prevPercent:
          randPercent = max(randPercent-percentIncr, minPercent)
      prevPercent=randPercent
      trainDataRatio = GenerateTrainTest2_Percentage(randPercent, traintestFile, numberOfClusters, textsperlabelDir, trainFile, testFile);
      print(str(itr)+","+str(randPercent))
      PerformClassification(trainFile, testFile, traintestFile)
      printClusterEvaluation_file(traintestFile)
   
 
def ObtainNumberOfClusters(isByTrueLabel, listtuple_pred_true_text) :
  dic_tupple_class=groupTxtByClass(listtuple_pred_true_text, isByTrueLabel)
  num_clusters= len(dic_tupple_class)
  return num_clusters
  
def enhanceClustersByIterativeClassification(listtuple_pred_true_text, minPercent, maxPercent, percentIncr, job_folder):
  maxIterations=30
  numberOfClusters=ObtainNumberOfClusters(False, listtuple_pred_true_text)
  maxTrainRatio =maxPercent/100.0  
  print("\nenhanceClustersByIterativeClassification starts.....="+str(len(listtuple_pred_true_text))+", numberOfClusters="+str(numberOfClusters))
  print("minPercent="+str(minPercent)+", maxPercent="+str(maxPercent)+", percentIncr="+str(percentIncr)+", job_folder="+job_folder) 

  textsperlabelDir="semisupervised/textsperlabel/"+job_folder+"/"
  if not os.path.exists(textsperlabelDir):
    os.makedirs(textsperlabelDir)
 
  trainFile = textsperlabelDir+"train" #output
  testFile = textsperlabelDir+"test" #output
  traintestFile = textsperlabelDir+"traintest" #output 

  writePredTrueTexts(traintestFile, listtuple_pred_true_text) #one time
  GenerateTrainTest2List(listtuple_pred_true_text, minPercent, maxPercent, percentIncr, maxIterations, traintestFile, numberOfClusters, textsperlabelDir,
  trainFile, testFile)  
    