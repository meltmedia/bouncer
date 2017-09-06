ifndef VIRTUAL_ENV
$(warning You should set up a virtualenv.  See the README file.)
endif

all: test run

prep:
	@pip install -r requirements.txt > /dev/null
	@find . -name "*.pyc" -delete

run:
	@python -m bouncer -R

test: unittest lint

unittest:
	@nosetests --with-coverage --cover-html --cover-erase --cover-branches --cover-package=bouncer

lint:
	@flake8 .

verboselint:
	@flake8 --show-pep8 --show-source .

clean:
	@find . -name "*.pyc" -delete
	@rm -r cover

.PHONY: clean all test run prep lint unittest
