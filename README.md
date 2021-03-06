# Graph-Ryder-api-v2
This is a simple Rest full Api to interact with neo4j database using the tulip-python library.
Big computation are made server side to provide a light weight ui: [Graph-ryder-dashboard-v2](https://github.com/norbertFeron/graph-ryder-dashboard-v2)

####1. change config file
```
cp config.example.ini config.ini
nano config.ini
```
Neo4j database need the following graphAware plugins:
- [graphaware-timetree-3.0.1.38.24.jar](http://products.graphaware.com/download/timetree/graphaware-timetree-3.0.1.38.24.jar)
- [graphaware-server-community-all-3.0.1.38.jar](http://products.graphaware.com/download/framework-server-community/graphaware-server-community-all-3.0.1.38.jar)
If you launch neo4j in a container name it with an alias
```
[neo4j]
url = myNeo4j
user = user
password = pass
```
## Local Installation
####2. install requirements
```
pip install -r requirements.txt
```
####3. launch api server
```
python app.py
```

## Docker Installation
####2. build
```
docker build -t avres-api .
```
####3. run
```
docker run -d -p 5000:5000 --name my-avres-api avres-api
```
If you launch neo4j in a container you have to link it with '--link' option
```
--link neo4jContainerName:myNeo4j
```
## Post install
### Generate the apidoc
- install apidoc
```
npm install apidoc -g
```
- generate the doc
```
apidoc -i ./routes/ -o ./routes/apidoc/
```
