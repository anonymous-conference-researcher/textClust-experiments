from textClustPy import textclust
from textClustPy import Preprocessor
from textClustPy import TwitterInput

def clust_callback(textclust):
        #textclust.showclusters(5, 10, "micro")
        print("yeah")

def save_callback(status):
        return
        #print("save to db")

## create textclust instance
clust = textclust(callback = clust_callback,radius=0.5,_lambda=0.01,tgap=10, auto_r= False, model="skipgram", embedding_verification= True, macro_distance="embedding_cosine_distance")
preprocessor = Preprocessor(max_grams=2)

## create input
TwitterInput("###", "###", 
"###", "###",  
["trump"], ["en"], textclust=clust, preprocessor=preprocessor,callback=save_callback)

