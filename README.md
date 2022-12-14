# AndroidStringResTranslationTool

## Description
This CLI tool allows Android developers to easily internationalize their applications by translating English strings in their resource files to other languages with a single command. This enables them to deploy their applications to any country.

## Usage

### Basic
```
python3 src/dayun/translator.py --root_file ./test_data/app/src/main/res/values/strings.xml
```

### Exclude certain languages


```
python3 src/dayun/translator.py --root_file ./test_data/app/src/main/res/values/strings.xml --exclude_languages=af,ca
```


## Test

```
python3 src/dayun/translator.py --root_file ./test_data/app/src/main/res/values/strings.xml --exclude_languages=af,ca --dryrun
```
