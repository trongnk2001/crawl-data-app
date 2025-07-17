package com.example;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.KStream;
import org.json.JSONObject;

import java.util.Properties;
import java.util.concurrent.CountDownLatch;

public class StreamProcessor {
    private final String bootstrapServers;
    private final String inputTopic;
    private final String outputTopic;

    public StreamProcessor(String bootstrapServers, String inputTopic, String outputTopic) {
        this.bootstrapServers = bootstrapServers;
        this.inputTopic = inputTopic;
        this.outputTopic = outputTopic;
    }

    public void process() {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "streams-processor");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());

        StreamsBuilder builder = new StreamsBuilder();
        KStream<String, String> source = builder.stream(inputTopic);

        // Enhanced processing with error handling
        KStream<String, String> processed = source.mapValues(value -> {
            try {
                JSONObject json = new JSONObject(value);
                
                // Add processing metadata
                json.put("processed", true);
                json.put("processor", "java-streams");
                json.put("processing_timestamp", System.currentTimeMillis());
                
                // Example processing: double the value
                if (json.has("value")) {
                    json.put("original_value", json.get("value"));
                    json.put("value", json.getInt("value") * 2);
                }
                
                return json.toString();
            } catch (Exception e) {
                System.err.println("Error processing message: " + e.getMessage());
                // Return original message if processing fails
                return value;
            }
        });

        processed.to(outputTopic);

        final KafkaStreams streams = new KafkaStreams(builder.build(), props);
        final CountDownLatch latch = new CountDownLatch(1);

        // Add shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            streams.close();
            latch.countDown();
        }));

        try {
            streams.start();
            latch.await();
        } catch (Exception e) {
            System.exit(1);
        }
    }
}