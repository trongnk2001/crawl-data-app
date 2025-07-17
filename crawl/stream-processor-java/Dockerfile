FROM maven:3.8.4-openjdk-11 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package assembly:single

FROM openjdk:11-jre-slim
WORKDIR /app
COPY --from=build /app/target/kafka-stream-processor-1.0-SNAPSHOT-jar-with-dependencies.jar .
CMD ["java", "-jar", "kafka-stream-processor-1.0-SNAPSHOT-jar-with-dependencies.jar"]