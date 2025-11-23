# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* tsconfig.json tsconfig.node.json vite.config.ts index.html ./
COPY src ./src
RUN npm install && npm run build

# Runtime stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
