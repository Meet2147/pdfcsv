#!/bin/bash

# Update package list and install Java
apt-get update -y
apt-get install -y openjdk-11-jdk

# Verify Java installation
java -version
