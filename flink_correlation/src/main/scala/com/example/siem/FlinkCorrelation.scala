package com.example.siem

import org.apache.flink.api.common.serialization.SimpleStringSchema
import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer
import java.util.Properties
import org.apache.flink.streaming.api.windowing.time.Time
import scala.collection.mutable

case class LogEvent(timestamp: Double, user: String, event_type: String, ip: String, commandLine: String, message: String)

object FlinkCorrelation {
  def main(args: Array[String]): Unit = {
    val env = StreamExecutionEnvironment.getExecutionEnvironment

    val props = new Properties()
    props.setProperty("bootstrap.servers", "localhost:9092")
    props.setProperty("group.id", "flink-corr-group")

    val consumer = new FlinkKafkaConsumer[String]("logs_raw", new SimpleStringSchema(), props)
    val producer = new FlinkKafkaProducer[String]("alerts", new SimpleStringSchema(), props)

    val stream = env.addSource(consumer)

    // parse JSON
    import org.json4s._
    import org.json4s.jackson.JsonMethods._

    implicit val formats = DefaultFormats

    val parsed = stream
      .map { raw =>
        try {
          val jv = parse(raw)
          val t = (jv \ "timestamp").extractOpt[Double].getOrElse(System.currentTimeMillis().toDouble)
          val u = (jv \ "user").extractOpt[String].getOrElse("unknown")
          val et = (jv \ "event_type").extractOpt[String].getOrElse("INFO")
          val ip = (jv \ "ip").extractOpt[String].getOrElse("0.0.0.0")
          val cmd = (jv \ "CommandLine").extractOpt[String].getOrElse("")
          val msg = (jv \ "message").extractOpt[String].getOrElse("")
          LogEvent(t,u,et,ip,cmd,msg)
        } catch {
          case _:Throwable => LogEvent(System.currentTimeMillis().toDouble, "unknown","INFO","0.0.0.0","","")
        }
      }

    // Key by IP, process a rolling window for multi-step
    val keyed = parsed.keyBy(_.ip)

    // We'll do a naive rolling approach in RichFlatMap
    keyed.flatMap(new MultiStepRichFlatMap)
      .map(alertStr => alertStr)
      .addSink(producer)

    env.execute("Flink Correlation Job")
  }
}

// RichFlatMap that keeps state for multi-step detection in a MapState or ValueState
import org.apache.flink.api.common.state.{ListState, ListStateDescriptor}
import org.apache.flink.configuration.Configuration
import org.apache.flink.streaming.api.functions.RichFlatMapFunction
import org.apache.flink.util.Collector

class MultiStepRichFlatMap extends RichFlatMapFunction[LogEvent, String] {
  private var eventState: ListState[(Double, String)] = _

  override def open(parameters: Configuration): Unit = {
    val desc = new ListStateDescriptor[(Double, String)]("ipEvents", createTypeInformation[(Double, String)])
    eventState = getRuntimeContext.getListState(desc)
  }

  override def flatMap(value: LogEvent, out: Collector[String]): Unit = {
    val now = System.currentTimeMillis()/1000.0
    // remove old
    val newList = mutable.ListBuffer[(Double,String)]()
    import scala.collection.JavaConverters._
    for(e <- eventState.get().asScala) {
      if(now - e._1 < 300) {
        newList += e
      }
    }
    // add current
    newList += ((now, value.event_type))

    // store back
    eventState.update(newList.asJava)

    // if last 5: fail->fail->fail->success->priv
    if(newList.size >= 5) {
      val last5 = newList.takeRight(5).map(_._2)
      if(last5(0).matches("ERROR|WARN") &&
         last5(1).matches("ERROR|WARN") &&
         last5(2).matches("ERROR|WARN") &&
         last5(3) == "INFO" &&
         last5(4) == "PRIV") {
        // produce alert as JSON
        val alert = s"""{
          "timestamp": ${now},
          "alert_type": "Multi-step Attack (Flink)",
          "description": "fail->fail->fail->success->priv in 5m window",
          "level": "high",
          "ip": "${value.ip}",
          "user": "${value.user}"
        }"""
        out.collect(alert)
      }
    }
  }
}
