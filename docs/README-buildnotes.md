# Build Notes
Some random notes on building - this is all in progess and subject to change

## About requirements.txt
We don't really use this anymore - switched to Pipfile. Keeping it here for posterity by running:
`pipenv lock -r > requirements.txt`

## Manually creating a release
2022-02-03: There were a bunch of odd errors using pyinstaller which look like bug with the latest release. For now I have switched to using the dev release, which you can see in the Pipfile (`pyinstaller = {file = "https://github.com/pyinstaller/pyinstaller/archive/develop.zip"}`)

Currently working way to create a release:
`pyinstaller --add-data .clivrt:. --onefile clivrt.py`

Which dumps clivrt into `./dist/clivrt`