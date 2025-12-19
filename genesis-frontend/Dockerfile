FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source
COPY . .

EXPOSE 3000

ENV PORT 3000
ENV NODE_ENV development

# Dev mode - compatible with volume mounts
CMD ["npm", "run", "dev"]
