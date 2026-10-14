FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

ENV API_INTERNAL_URL=http://api:8000
EXPOSE 3000

CMD ["npm", "start"]
