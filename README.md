# AndroidStringResTranslationTool

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
python3 src/dayun/translator.py --root_file ./test_data/app/src/main/res/values/strings.xml --exclude_languages=af,ca --dry_run=True
```
