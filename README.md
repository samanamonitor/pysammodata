docker build --tag odata:latest --progress=plain .
docker run -dit --name odatadev -v $(pwd):/usr/src odata:latest /bin/bash
docker exec -it odatadev /bin/bash

docker builder prune


python3 -m pip install -r requirements.txt