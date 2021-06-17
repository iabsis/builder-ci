FROM debian:9

## Install Basics
RUN apt update && apt -y install curl openjdk-8-jdk-headless unzip build-essential zipalign

## Install NodeJS
RUN curl --silent --location https://deb.nodesource.com/setup_14.x | bash -
RUN apt -y install nodejs

## Install Ionic and Cordova
RUN npm i -g ionic cordova
RUN ionic --no-interactive config set -g daemon.updates false

COPY build-ionic.sh /build.sh
RUN chmod +x /build.sh

## Install Android SDK
ARG ANDROID_PLATFORMS_VERSION
ENV ANDROID_PLATFORMS_VERSION ${ANDROID_PLATFORMS_VERSION:-30}
ARG ANDROID_BUILD_TOOLS_VERSION
ENV ANDROID_BUILD_TOOLS_VERSION ${ANDROID_BUILD_TOOLS_VERSION:-30.0.2}

ENV ANDROID_SDK /opt/android-sdk-linux
ENV PATH ${PATH}:${ANDROID_SDK}/tools/bin
RUN mkdir ${ANDROID_SDK} && \
    cd ${ANDROID_SDK} && \
    curl -SLo sdk-tools-linux.zip https://dl.google.com/android/repository/sdk-tools-linux-3859397.zip && \
    unzip sdk-tools-linux.zip && \
    rm -f sdk-tools-linux.zip

RUN yes | sdkmanager --licenses
RUN sdkmanager "tools" && \  
  sdkmanager "platform-tools" && \
  sdkmanager "platforms;android-${ANDROID_PLATFORMS_VERSION}" && \
  sdkmanager "build-tools;${ANDROID_BUILD_TOOLS_VERSION}"

## Install Gradle
ENV GRADLE_HOME=/opt/gradle/gradle-6.5
ENV PATH ${PATH}:${GRADLE_HOME}/bin
RUN curl -SLo gradle-bin.zip https://services.gradle.org/distributions/gradle-6.5-bin.zip && \
    unzip -d /opt/gradle/ gradle-bin.zip && \
    rm -f gradle-bin.zip

## Builder command
WORKDIR /build/sources
ENTRYPOINT ["/build.sh"]
