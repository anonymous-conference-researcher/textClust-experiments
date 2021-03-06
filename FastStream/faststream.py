import os
from datetime import datetime

from general_util import readlistWholeJsonDataSet
from evaluation import Evaluate_old
from fast_read_pred_true_text import ReadPredTrueText
from fast_clustering_term_online import cluster_biterm
from word_vec_extractor import extractAllWordVecsPartialStemming

ignoreMinusOne=True

dataDir = "data/"
outputPath = "FastStream_Result/"

dataset='Tweets-T' # 'stackoverflow_javascript' 'stackoverflow_java' 'stackoverflow_python' 'stackoverflow_csharp' 'stackoverflow_php' 'stackoverflow_android' 'stackoverflow_jquery' 'stackoverflow_r' 'stackoverflow_java'  # 'stackoverflow_java'  'stackoverflow_cplus' 'stackoverflow_mysql' 'stackoverflow_large_tweets-T_news-T_suff' 'stackoverflow_large_tweets-T' #'News-T' 'NT-mstream-long1' #'Tweets-T' # 'stackoverflow_large' 'stackoverflow_large_tweets-T'
inputfile=dataDir+dataset

def run(inputfile, outputpath):
  resultFile=outputPath+'personal_cluster_biterm.txt'

  list_pred_true_words_index=readlistWholeJsonDataSet(inputfile) 


  print(len(list_pred_true_words_index))

  '''all_words=[]
  for item in list_pred_true_words_index:
    all_words.extend(item[2])
  all_words=list(set(all_words))'''

  gloveFile = "glove.6B.50d.txt"
  embedDim=50
  wordVectorsDic={}
  #wordVectorsDic=extractAllWordVecsPartialStemming(gloveFile, embedDim, all_words)

  if os.path.exists(resultFile):
    os.remove(resultFile)
    
  c_bitermsFreqs={} 
  c_totalBiterms={}
  c_wordsFreqs={}
  c_totalWords={}
  c_txtIds={}
  c_clusterVecs={}
  txtId_txt={}
  last_txtId=0  
  max_c_id=0
  dic_clus__id={}

  dic_biterm__clusterIds={}



  f = open(resultFile, 'w')

  t11=datetime.now()

  c_bitermsFreqs, c_totalBiterms, c_wordsFreqs, c_totalWords, c_txtIds, c_clusterVecs, txtId_txt, last_txtId, dic_clus__id, dic_biterm__clusterIds=cluster_biterm(f, list_pred_true_words_index, c_bitermsFreqs, c_totalBiterms, c_wordsFreqs, c_totalWords, c_txtIds, c_clusterVecs, txtId_txt, last_txtId, max_c_id, wordVectorsDic, dic_clus__id, dic_biterm__clusterIds)


  t12=datetime.now()	  
  t_diff = t12-t11
  print("total time diff secs=",t_diff.seconds)  

  f.close()
    
  listtuple_pred_true_text=ReadPredTrueText(resultFile, ignoreMinusOne)
  return listtuple_pred_true_text
  #print('result for', dataset)
  #Evaluate_old(listtuple_pred_true_text)  