# Get the node image 
FROM node:18

WORKDIR /app

COPY package.json /app/

RUN npm install

COPY . .

RUN npm run build

# Just metadata in this case because compose.yaml defines the ports again.
EXPOSE 3000 

CMD ["npm", "run", "dev"]