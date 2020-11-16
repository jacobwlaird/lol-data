# maybe try alpine
FROM node
WORKDIR /usr/src/app
# does this have to change?
COPY package*.json ./
RUN npm install

COPY . ./

EXPOSE 3000
RUN npm start
