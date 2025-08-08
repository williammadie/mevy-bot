FROM node:18

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies first for caching
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of your project
COPY . .

# Expose Hardhat's default port
EXPOSE 8545

# Default command: run the local Hardhat node
CMD ["npx", "hardhat", "node", "--hostname", "0.0.0.0"]
