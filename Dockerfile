FROM python:3.9-slim

# 设置时区为中国标准时间
ENV TZ=Asia/Shanghai

# 安装时区数据、Chrome 和驱动
RUN apt-get update && apt-get install -y \
    tzdata \
    chromium \
    chromium-driver \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再拷代码
COPY . .

# 设置环境路径
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 运行脚本
CMD ["python", "acckio.py"]