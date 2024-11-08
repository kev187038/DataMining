from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.ml.feature import RegexTokenizer, StopWordsRemover
from pyspark.sql import functions
import pyspark
import re

#Open spark and create a dataframe with the tsv file
spark = SparkSession.builder \
    .master("local[*]") \
    .config("spark.hadoop.fs.defaultFS", "file:///") \
    .getOrCreate()
df = spark.read.option("delimiter", "\t").csv("products.tsv", header=True, inferSchema=True)

#Preprocessing with spark
regex = r'[\w]+(?:\.[\w-]+)*'
regex_tokenizer = RegexTokenizer(inputCol="Description", outputCol="tokens", pattern=regex, toLowercase=True, gaps=False)
df = regex_tokenizer.transform(df)
stopwords = StopWordsRemover.loadDefaultStopWords("italian")
remover = StopWordsRemover(inputCol="tokens", outputCol="filtered_tokens", stopWords=stopwords)
df = remover.transform(df)
df.show()
print("Building Index...")

#Build inverted index 
inverted_index = df.select(functions.explode("filtered_tokens").alias("terms"), "Id") #create df grouping single terms with all of the ids of the descriptions they're found in 
inverted_index = inverted_index.groupBy("terms").agg(functions.collect_list("Id").alias('desc_list')) #create inverted index lists with single ters
inverted_index.write.json("./inverted_index.json", mode="overwrite")
inverted_index.show()
print("Index built!")
print("Building tf-ifd...")

#Build tf
tf = df.select(functions.explode("filtered_tokens").alias("terms"), "Id").groupBy("Id", "terms").count().withColumnRenamed("count", "term_freq")
tf.show()
#Id|term|frequency of term in description Id

#Build IDF  log(N/df(t))
N = df.count()
idf = inverted_index.withColumn('num_desc', functions.size('desc_list')) #get number of docs in which term i appears
idf = idf.withColumn("idf", functions.log(functions.lit(N) / functions.col("num_desc")))#use lit for literal value otherwise it doesn't work
#term|documents the term appears in|number of documents the term appears in|idf
idf.show()

#Build tf-idf
tf_idf = tf.join(idf, on="terms", how="inner")
tf_idf = tf_idf.withColumn("tf_idf", functions.col("term_freq") * functions.col("idf"))

#Save tf-idf
tf_idf = tf_idf.drop('desc_list').drop('idf').drop('term_freq').drop('num_desc') #cannot write that to csv and don't need it
tf_idf.show()
tf_idf.write.option("header", "true").mode("overwrite").csv("./tf_idf.csv")
print("Tf-idf built!")

spark.stop()
