.PHONY: test clean

test:
	python3 -m unittest

function:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} \;
	pip3 install --target ./package -Ur requirements.txt
	rm -rf package/Cryptodome/SelfTest
	cd package/ && zip -r9 ../function.zip .
	zip -g -r9 function.zip pysecrets/ lambda.py

clean:
	rm -rf package/
	find . -type d -name "__pycache__" -prune -exec rm -rf {} \;
	rm -f function.zip
