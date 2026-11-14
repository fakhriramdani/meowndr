FROM node:22-alpine AS builder
WORKDIR /app
COPY studio-ui/package.json studio-ui/package-lock.json* ./
RUN npm ci || npm install
COPY studio-ui/ ./
RUN npm run build

FROM nginx:1.27-alpine
COPY studio-ui/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
