# Get the node image 
FROM node:18

WORKDIR /app

COPY package.json package-lock.json /app/

RUN --mount=type=cache,target=/root/.npm npm install

COPY . .

# RUN chmod +x node_modules/.bin/next

RUN npm run build

# Just metadata in this case because compose.yaml defines the ports again.
EXPOSE 3000 

CMD ["npm", "run", "start"]
# CMD ["npm", "run", "dev"]