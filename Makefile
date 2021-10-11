build:
	poetry install
	poetry run bin/static-page.py
	poetry run bin/gen-trig.py
	
serve:
	make build
	bundle exec jekyll serve
	