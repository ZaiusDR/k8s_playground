FROM node:18 AS builder

WORKDIR /app

COPY package.json ./
RUN npm install

ARG ws_url="ws://localhost:3001/"
ENV VITE_WS_URL=$ws_url

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
