
comma:= ,
empty:=
space:= $(empty) $(empty)

all: package-app
package-app:
	rm -rf src/__pycache__ || true
	echo ${ETSY_API_KEY} > .api_key
	python3 setup.py py2app --arch x86_64 --force-system-tk --includes 'requests,json,collections,threading,queue,webbrowser' --extra-scripts '$(subst $(space),$(comma),$(wildcard src/*))' -r '.api_key'