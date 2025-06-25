FROM node:18-alpine AS build

WORKDIR /app

COPY package.json ./
COPY package-lock.json ./

RUN npm install

COPY . .

ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:stable-alpine

COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

# docker build -t hahongson/cookie-violation-checker-frontend:latest .
# docker push hahongson/cookie-violation-checker-frontend:latest
# docker run -d -p 8080:80 hahongson/cookie-violation-checker-frontend:latest
