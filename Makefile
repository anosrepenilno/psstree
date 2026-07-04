.PHONY: clean build publish

clean:
	rm -rf build dist *.egg-info

build: clean
	python -m build

publish: build
	python -m twine upload --verbose dist/*

