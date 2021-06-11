.PHONY: all test clean function

all : test clean function

test:
	python3 -m unittest

function:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} \;
	docker run --rm -v `pwd`:/var/task --user `id -u`:`id -g` "lambci/lambda:build-python3.8" /bin/sh -c "pip install -r requirements.txt -t package; exit"
	cd package/ && zip -r9 ../function.zip .
	zip -g -r9 function.zip pysecrets/ templates/ lambda.py

clean:
	rm -rf package/
	find . -type d -name "__pycache__" -prune -exec rm -rf {} \;
	rm -f function.zip
