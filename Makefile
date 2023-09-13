.PHONY: all test clean function layer

all : test clean function layer

test:
	python3 -m unittest

function:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} \;
	zip -g -r9 function.zip pysecrets/ lambda.py

layer:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} \;
	docker run --rm -v `pwd`:/var/task --user `id -u`:`id -g` "public.ecr.aws/sam/build-python3.11:latest" /bin/sh -c "pip install --no-cache -r requirements.txt -t python; exit"
	zip -r9 ./layer.zip python/

clean:
	rm -rf python/
	find . -type d -name "__pycache__" -prune -exec rm -rf {} \;
	rm -f function.zip layer.zip
