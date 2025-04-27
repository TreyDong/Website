# 使用 Node.js 18 作为基础镜像
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package.json package-lock.json* ./

RUN npm install
# 安装依赖
RUN npm ci

# 复制所有源代码
COPY . .

# 设置生产环境
ENV NODE_ENV=production
ENV PORT=3005
ENV HOSTNAME=0.0.0.0

# 构建应用
# Use the local next executable
RUN ./node_modules/.bin/next build

# 暴露 3001 端口
EXPOSE 3005

# Copy static assets to the expected locations within the standalone directory
RUN cp -R .next/static /app/.next/standalone/.next/static
RUN cp -R public /app/.next/standalone/public

# 启动应用
CMD ["node", ".next/standalone/server.js"]
