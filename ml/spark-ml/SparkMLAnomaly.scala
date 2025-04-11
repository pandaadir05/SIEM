package com.example.siem

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.streaming._
import org.apache.spark.streaming.kafka010._

object SparkMLAnomaly {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder
      .appName("Spark-ML-Anomaly")
      .getOrCreate()

    import spark.implicits._

    // read streaming from Kafka logs_raw
    val df = spark
      .readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", "localhost:9092")
      .option("subscribe", "logs_raw")
      .option("startingOffsets", "earliest")
      .load()

    // parse JSON
    val schema = new StructType()
      .add("timestamp", DoubleType)
      .add("user", StringType)
      .add("event_type", StringType)
      .add("ip", StringType)
      .add("CommandLine", StringType)
      .add("message", StringType)

    val logs = df.selectExpr("CAST(value AS STRING) as raw")
      .select(from_json($"raw", schema).alias("log"))
      .select("log.*")

    // For demonstration, let's do a rolling average hour approach
    // Convert timestamp -> hour
    val withHour = logs.withColumn("hour", hour((($"timestamp"/1000).cast(TimestampType))))

    // We'll do a simple groupBy window approach => detect outliers
    val windowed = withHour
      .groupBy(window($"timestamp".cast(TimestampType), "5 minutes"), $"hour")
      .count()

    // We won't implement real ML here, just demonstrate how you'd do streaming logic
    val query = windowed.writeStream
      .format("console")
      .outputMode("update")
      .option("truncate", false)
      .start()

    query.awaitTermination()
  }
}
