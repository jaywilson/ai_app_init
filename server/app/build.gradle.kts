/*
 * This file was generated by the Gradle 'init' task.
 *
 * This generated file contains a sample Kotlin application project to get you started.
 * For more details take a look at the 'Building Java & JVM projects' chapter in the Gradle
 * User Manual available at https://docs.gradle.org/7.2/userguide/building_java_projects.html
 */

plugins {
    // Apply the org.jetbrains.kotlin.jvm Plugin to add support for Kotlin.
    id("org.jetbrains.kotlin.jvm") version "2.1.10"

    // Apply the application plugin to add support for building a CLI application in Java.
    application
    kotlin("plugin.serialization") version "2.0.0"
}

repositories {
    // Use Maven Central for resolving dependencies.
    mavenCentral()
}

dependencies {
    // Align versions of all Kotlin components
    implementation(platform("org.jetbrains.kotlin:kotlin-bom"))

    // Use the Kotlin JDK 8 standard library.
    implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8")

    // This dependency is used by the application.
    implementation("com.google.guava:guava:30.1.1-jre")

    // Ktor Client Core and CIO Engine
    implementation("io.ktor:ktor-client-core:2.3.5") // Core HTTP client library
    implementation("io.ktor:ktor-client-cio:2.3.5")  // CIO engine for the HTTP client

    implementation("io.ktor:ktor-client-content-negotiation:2.3.5")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.5")

    // Ktor Server Core and Netty Engine
    implementation("io.ktor:ktor-server-core:2.3.5")
    implementation("io.ktor:ktor-server-netty:2.3.5")

    // JSON Content Negotiation for Ktor Server
    implementation("io.ktor:ktor-server-content-negotiation:2.3.5")

    // Azure Storage Blob dependencies
    implementation("com.azure:azure-storage-blob:12.24.1")
    implementation("com.azure:azure-identity:1.11.1")

    // Use the Kotlin test library.
    testImplementation("org.jetbrains.kotlin:kotlin-test")

    // Use the Kotlin JUnit integration.
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit")
}

application {
    // Define the main class for the application.
    mainClass.set("server.MainApp")
}
