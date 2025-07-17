package com.example;

public class Main { 
    public static void main(String[] args) {
        String bootstrapServers = System.getenv("KAFKA_BROKER");
        String inputTopic = System.getenv("INPUT_TOPIC");
        String outputTopic = System.getenv("OUTPUT_TOPIC");

        if (bootstrapServers == null || inputTopic == null || outputTopic == null) {
            System.err.println("Required environment variables: KAFKA_BROKER, INPUT_TOPIC, OUTPUT_TOPIC");
            System.exit(1);
        }

        StreamProcessor processor = new StreamProcessor(bootstrapServers, inputTopic, outputTopic);
        processor.process();
    }
}