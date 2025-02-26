# Get the node image 
FROM node:18

WORKDIR /app

COPY package.json /app/

# ONLY TEMP WHILE BUILING IS FAILING?
# RUN npm cache clean --force

RUN npm install

COPY . .

RUN chmod +x node_modules/.bin/next

RUN npm run build

# Just metadata in this case because compose.yaml defines the ports again.
EXPOSE 3000 

CMD ["npm", "run", "start"]