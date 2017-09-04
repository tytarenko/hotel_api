run:
	python ./api.py

mkdb:
	python ./migrate.py
	python ./fixtures.py

clean:
	find . -name "*.pyc" -exec rm -rf {} \;
