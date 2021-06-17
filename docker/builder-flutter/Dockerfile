FROM debian:9

## Install Basics
RUN apt update && apt -y install curl openjdk-8-jdk-headless unzip build-essential zipalign git chromium

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

## Install Flutter
ARG FLUTTER_PATH=/opt/flutter
RUN cd /opt && \
    curl -SLo flutter_linux.tar.xz https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_2.2.1-stable.tar.xz && \
    tar xf flutter_linux.tar.xz && \
    rm flutter_linux.tar.xz
ENV PATH ${PATH}:${FLUTTER_PATH}/bin
ENV CHROME_EXECUTABLE /usr/bin/chromium
RUN flutter config --android-sdk /opt/android-sdk-linux/
RUN flutter doctor

## End with custom build tool
COPY build-flutter.sh /build.sh
RUN chmod +x /build.sh

## Builder command
WORKDIR /build/sources
ENTRYPOINT ["/build.sh"]
