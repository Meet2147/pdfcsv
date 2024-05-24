#!/bin/bash

# Update package list and install Java
apt-get update -y
apt-get install -y openjdk-11-jdk

# Set JAVA_HOME environment variable
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# Verify Java installation
java -version
