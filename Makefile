
comma:= ,
empty:=
space:= $(empty) $(empty)

all: package-app install-packages
package-app: clean-pycache
	if [[ ! -f .api_key ]]; then echo ${ETSY_API_KEY} > .api_key; fi
	python3 setup.py py2app --arch x86_64 --force-system-tk --includes 'requests,json,collections,threading,queue,webbrowser' --extra-scripts '$(subst $(space),$(comma),$(wildcard src/*))' -r '.api_key'

clean-pycache:
	rm -rf src/__pycache__ || true

install-packages:
	python3 -m pip install requests

clean:
	rm -rf build
	rm -rf dist
	rm .etsy-tool-*
	rm -rf __pycache__