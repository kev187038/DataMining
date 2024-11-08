from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.ml.feature import RegexTokenizer, StopWordsRemover, VectorAssembler, StringIndexer
from pyspark.ml.linalg import Vectors
from pyspark.sql import functions
from pyspark.sql.types import ArrayType, FloatType, StringType
import re
import numpy as np
def create_vector(indices, values, size): #create vector with Spark / needs to be registered as user defined function otherwise spark can't use it 
    vector = [0.0] * size
   
    for idx, value in zip(indices, values):
        vector[int(idx)] = value
    
    return vector

def cosine_similarity(v1, v2):
	dot_product = sum([a * b for a, b in zip(v1, v2)])
	norm_1 = sum([a ** 2 for a in v1]) ** 0.5
	norm_2 = sum([b ** 2 for b in v2]) ** 0.5
	return dot_product / (norm_1 * norm_2)
   
spark = SparkSession.builder \
    .master("local[*]") \
    .config("spark.hadoop.fs.defaultFS", "file:///") \
    .getOrCreate()
    
tf_idf = spark.read.option("header", "true").option("inferSchema", "true").csv("./tf_idf.csv")#|term|Id|tf-idf
df = spark.read.option("delimiter", "\t").csv("products.tsv", header=True, inferSchema=True)
inv_idx = spark.read.json("./inverted_index.json") #|desc_list|terms
N_ = df.count()

print("Loading search engine...")
#Create the description vectors
indexer = StringIndexer(inputCol='terms',outputCol='vector_index')
description_vectors = indexer.fit(tf_idf).transform(tf_idf)
#description_vectors.show(n=description_vectors.count())
description_vectors = description_vectors.groupBy("Id").agg(functions.collect_list("vector_index").alias("vector_indices"),functions.collect_list("tf_idf").alias("tf_idf_values"))

#Same as problem 1, but using spark dataframes
create_vector_udf = functions.udf(create_vector, ArrayType(FloatType()))
N = tf_idf.select('terms').distinct().count()
description_vectors = description_vectors.withColumn("vector", create_vector_udf("vector_indices", "tf_idf_values", functions.lit(N))) #create the vectors with spark inside the dataframe
description_vectors = description_vectors.drop("vector_indices").drop("tf_idf_values")
print("Search engine loaded successfully!")

query = input("Insert your query(to exit press enter without insering anything): ")

while query != "":
	#Tokenize and process query to get query vector
	regex = r'[\w]+(?:\.[\w-]+)*'
	query_df = spark.createDataFrame([(query,)], ["query"])
	print("Query is:\n")
	query_df.show()
	regex_tokenizer = RegexTokenizer(inputCol="query", outputCol="tokens", pattern=regex, toLowercase=True, gaps=False)
	query_df = regex_tokenizer.transform(query_df)
	stopwords = StopWordsRemover.loadDefaultStopWords("italian")
	remover = StopWordsRemover(inputCol="tokens", outputCol="query_tokens", stopWords=stopwords)
	query_df = remover.transform(query_df)
	
	#Get tdf-idf of query terms
	tf_query = query_df.select(functions.explode("query_tokens").alias("terms"), "query").groupBy("query","terms").count().withColumnRenamed("count", "term_freq")
	idf_query = tf_query.join(inv_idx, on="terms", how="inner")
	idf_query = idf_query.withColumn('num_desc', functions.size('desc_list'))
	idf_query = idf_query.withColumn("idf", functions.log(functions.lit(N_) / functions.col("num_desc")))
	tf_idf_query = idf_query.withColumn("tf_idf", functions.col("term_freq") * functions.col("idf"))
	tf_idf_query = tf_idf_query.drop("idf").drop("term_freq").drop("desc_list").drop("num_desc")
	tf_idf_query = indexer.fit(tf_idf).transform(tf_idf_query) #fit the same indexing as the one for the description vectors
	
	#Build query vector
	query_vector = tf_idf_query.groupBy("query").agg(functions.collect_list("vector_index").alias("vector_indices"),functions.collect_list("tf_idf").alias("tf_idf_values"))
	query_vector = query_vector.withColumn("query_vector", create_vector_udf("vector_indices", "tf_idf_values", functions.lit(N)))
	query_vector = query_vector.drop("vector_indices").drop("tf_idf_values").drop("query")
	
	#Compare query vector to all description vectors
	cosine_similarity_udf = functions.udf(cosine_similarity, FloatType())
	result = description_vectors.crossJoin(query_vector)
	result = result.withColumn("cosine_similarity", cosine_similarity_udf("vector", "query_vector"))
	
	#Return result
	result = result.join(df, on="Id", how="inner")
	result = result.orderBy(functions.col("cosine_similarity").desc()).drop("Id").drop("vector").drop("query_vector")
	result.show(truncate=False)
	
	query = input("Insert your query(to exit press enter without insering anything): ")





spark.stop()    
