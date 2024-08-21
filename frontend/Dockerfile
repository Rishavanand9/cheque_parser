# Build stage
FROM node:14 as build

# Set the working directory in the container
WORKDIR /frontend

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Build the app
RUN npm run build

# Serve stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /frontend/build /usr/share/nginx/html

# Add your custom nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]