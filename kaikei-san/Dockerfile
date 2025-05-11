FROM alpine:3.21

WORKDIR /workspace
ENV DEBIAN_FRONTEND=noninteractive
RUN apk --no-cache --update add python3 py3-pip
RUN pip3 install --no-cache --upgrade --break-system-packages py-cord

COPY src/ .
ENV TZ=Asia/Tokyo
ENTRYPOINT ["python3","-u","/workspace/main.py"]