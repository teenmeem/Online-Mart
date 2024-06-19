Project Assignment: Online Imtiaz Mart API Using Event-Driven Microservices Architecture
Project Overview
This project aims to develop an online mart API using an event-driven microservices architecture. The API will leverage various technologies such as FastAPI, Docker, DevContainers, Docker Compose, PostgreSQL, Kafka, Protocol Buffers (Protobuf), and Kong for API gateway management. The goal is to create a scalable, maintainable, and efficient system that handles high volumes of transactions and data in a distributed manner.

Additionally, Test-Driven Development (TDD) and Behavior-Driven Development (BDD) practices will be incorporated to ensure high code quality and alignment with business requirements.

Objectives
Develop a scalable and efficient API for an online mart using microservices.
Implement an event-driven architecture to handle asynchronous communication between services.
Utilize modern technologies such as FastAPI for API development, Docker for containerization, and Kafka for event streaming.
Ensure smooth development and deployment using DevContainers and Docker Compose.
Manage and route API requests through Kong API Gateway.
Use Protocol Buffers (Protobuf) for efficient data serialization.
Persist data using PostgreSQL.
Incorporate TDD and BDD to enhance code quality and ensure the application meets business requirements.
Technologies
FastAPI: A modern, fast (high-performance) web framework for building APIs with Python.
Docker: For containerizing the microservices, ensuring consistency across different environments.
DevContainers: To provide a consistent development environment.
Docker Compose: For orchestrating multi-container Docker applications.
PostgreSQL: A powerful, open-source relational database system.
SQLModel: For interacting with the PostgreSQL database using Python.
Kafka: A distributed event streaming platform for building real-time data pipelines and streaming applications.
Protocol Buffers (Protobuf): A method developed by Google for serializing structured data, similar to XML or JSON but smaller, faster, and simpler.
Kong: An open-source API Gateway and Microservices Management Layer.
Github Actions: For CI/CD pipeline.
Pytest: For unit testing and TDD.
Behave: For BDD.
Architecture
Microservices
User Service: Manages user authentication, registration, and profiles.
Product Service: Manages product catalog, including CRUD operations for products.
Order Service: Handles order creation, updating, and tracking.
Inventory Service: Manages stock levels and inventory updates.
Notification Service: Sends notifications (email, SMS) to users about order statuses and other updates.
Payment Service: Processes payments and manages transaction records.
Event-Driven Communication
Kafka: Acts as the event bus, facilitating communication between microservices. Each service can produce and consume messages (events) such as user registration, order placement, and inventory updates.
Protobuf: Used for defining the structure of messages exchanged between services, ensuring efficient and compact serialization.
Data Storage
PostgreSQL: Each microservice with data persistence needs will have its own PostgreSQL database instance, following the database-per-service pattern.
API Gateway
Kong: Manages API request routing, authentication, rate limiting, and other cross-cutting concerns.
