#!/usr/bin/env python
# -- coding: UTF-8 --
# Path: src/dayun/translator.py
# This is a simple translator using google translation to translate Android string resource files
import argparse
# Copyright (c) 2022-Present HsinYun Chang
# Create by HsinYun Chang<brautifulgirl@hotmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import xml.etree.ElementTree as ET
import time
import json
from textwrap import wrap
from typing import List, Set
from xml.sax.saxutils import escape
import re

try:
    import urllib2 as request
    from urllib import quote
except:
    from urllib import request
    from urllib.parse import quote

USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
               (
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, '
                   'like Gecko) '
                   'Chrome/19.0.1084.46 Safari/536.5'),
               (
                   'Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) '
                   'Chrome/19.0.1084.46'
                   'Safari/536.5'),)

SLEEP_SEC_FOR_EACH_REQUEST = 3
DRY_RUN = True
DEFAULT_LANG = 'en'

OUTPUT_STRING_PATTERN = '    <string name="{}">{}</string>\n'


class LocaleFile:
    """
    A locale data structure having file path, locale, and its language code
    """
    def __init__(self, path):
        self.path = path
        regex = r"values-([a-zA-Z-]*)"
        match = re.search(regex, path)
        self.locale = match.groups()[0]
        self.lang = self.locale.split('-')[0]

    def __str__(self):
        return 'path: {}, lang: {}'.format(self.path, self.lang)


def _random_choice(seq):
    def _random_int(width):
        return int.from_bytes(os.urandom(width), 'little')

    return seq[_random_int(1) % len(seq)]


class StringResource:
    """
    String resource represents id, content, etc
    """
    def __init__(self, id, content, translated=True):
        self.id = id
        self.content = content
        self.translated = translated

    def __repr__(self):
        return '(id: {}, content: {}, translated: {})'.format(self.id, self.content,
                                                              self.translated)


class ResourceFinder:

    def get_locale_files_from_dir(self, path, file_ext='xml'):
        locale_files = []
        for root, dirs, files in os.walk(path):
            if root.endswith('values'):
                continue
            for file in files:
                if file.endswith(f'.{file_ext}'):
                    locale_files.append(LocaleFile(os.path.join(root, file)))
        return locale_files

    def get_string_id_set(self, path):
        resources = self.parse_resource_file(path)
        print('resources: {}'.format(resources))
        return set(r[0] for r in resources)

    def parse_resource_file(self, file):
        if not os.path.exists(file):
            return []
        tree = ET.parse(file)
        root = tree.getroot()
        return self.parse_node(root)

    def parse_node(self, root):
        """
        return a list of tuple(id, string xml entity)
        """

        def escape_xml(s):
            return escape(s).replace('"', '&quot;').replace("'", '&apos;')

        idAttrib = '{http://schemas.android.com/apk/res/android}id'
        str_tag = 'string'
        resources: List[StringResource] = []
        for child in root:
            if str_tag in child.tag:
                translated = True
                for key, value in child.attrib.items():
                    if idAttrib in child.attrib:
                        id = child.attrib[idAttrib]
                        id = id[id.find('/') + 1:]
                    elif key == 'translatable':
                        translated = not value == 'false'
                    elif key == 'name':
                        id = value

                if not id or (' ' in id or '-' in id):
                    raise ValueError('id is invalid: {}'.format(id))

                content = self._get_content(child)
                content = escape_xml(content)
                resources.append(StringResource(id, content, translated))

        return resources

    def _get_content(self, element):
        res = element.text
        for e in element:
            res = res + ET.tostring(e, encoding='unicode')
            if e.tail:
                res = res + e.tail
        return res


class Translator:
    def __init__(self, from_lang=DEFAULT_LANG):
        self.from_lang = from_lang

    def translate_file(self, need_translated_str_resources: List[StringResource],
                       target_str_resources: List[
                           StringResource],
                       target_locale_file: LocaleFile):
        """
        translate the target_locale_file and save the result to the same file
        """
        if not target_str_resources:
            raise ValueError('root resources is empty')

        new_translated_str_resources = self._translate_str_resources(
            need_translated_str_resources, target_locale_file.lang)
        self._save_translated_strings(new_translated_str_resources, target_locale_file)

    def _save_translated_strings(self, new_translated_str_resources, target_locale_file):
        if not new_translated_str_resources:
            return
        end_resource_syntax = '</resources>'
        new_lines = []
        for each in new_translated_str_resources:
            line = OUTPUT_STRING_PATTERN.format(each.id, each.content)
            new_lines.append(line)
            print(line)
        new_lines.append(end_resource_syntax + '\n')

        previous_lines = []
        with open(target_locale_file.path, 'r') as target_xml:
            previous_lines = target_xml.readlines()

        output_path = target_locale_file.path + '.bak' if DRY_RUN else target_locale_file.path
        with open(output_path, 'w') as target_xml:
            target_xml.writelines(
                [item for item in previous_lines if end_resource_syntax not in item])
            target_xml.writelines([str(line) for line in new_lines])
        print(f'Saved to {output_path}')

    def _translate_str_resources(self, need_translated_str_resources, lang):
        """
        translate the string resources
        """
        translated_str_resources = []
        for str_resource in need_translated_str_resources:
            content = str_resource.content
            new_content = self._translate_content(content, lang)
            translated_str_resources.append(StringResource(id=str_resource.id,
                                                           content=new_content))

        return translated_str_resources

    def _translate_content(self, source, to_lang):
        if DRY_RUN:
            return 'This is a dry-run string'
        if self.from_lang == to_lang:
            return source
        source_list = wrap(source, 1000, replace_whitespace=False)
        res = ''
        for s in source_list:
            translate = self._get_translation_from_google(s, to_lang)
            if translate:
                print('Finished translation : ' + s + ' -> ' + translate)
            else:
                print('Finished translation : ' + s + ' use the original str: ' + s)
            res = res + (translate if translate is not None else s)
            time.sleep(SLEEP_SEC_FOR_EACH_REQUEST)
        return res

    def _get_translation_from_google(self, source, to_lang):
        json5 = self._get_json5_from_google(source, to_lang)
        data = json.loads(json5)
        translation = data['responseData']['translatedText']
        if not isinstance(translation, bool):
            return translation
        else:
            matches = data['matches']
            for match in matches:
                if not isinstance(match['translation'], bool):
                    next_best_match = match['translation']
                    break
            return next_best_match

    def _get_json5_from_google(self, source, to_lang):
        escaped_source = quote(source, '')
        headers = {'User-Agent': _random_choice(USER_AGENTS)}
        api_url = "http://mymemory.translated.net/api/get?q=%s&langpair=%s|%s"
        req = request.Request(url=api_url % (escaped_source, self.from_lang, to_lang),
                              headers=headers)
        r = request.urlopen(req)
        return r.read().decode('utf-8')


def run(exclude_lang_set: Set, root_file: str, translator: Translator,
        resource_finder: ResourceFinder):
    if not os.path.exists(root_file) or os.path.basename(root_file) != 'strings.xml':
        raise ValueError(f'{root_file} is not strings.xml')

    root_file_dir: str = os.path.join(os.path.dirname(root_file), '..', '..')
    existing_locale_files: List[LocaleFile] = resource_finder.get_locale_files_from_dir(
        root_file_dir)

    root_str_resources = resource_finder.parse_resource_file(root_file)
    # Exclude Non-translated Strings
    root_str_resources = [res for res in root_str_resources if res.translated != False]
    print('There are {} strings in root file should be translated: {}'.format(len(
        root_str_resources), root_file))
    for locale_file in existing_locale_files:
        print(f'Started lang: {locale_file.lang}')
        if locale_file.lang in exclude_lang_set:
            print('Skipped lang: {}'.format(locale_file.lang))
            continue
        target_str_resources = resource_finder.parse_resource_file(locale_file.path)
        target_id_set = set([res.id for res in target_str_resources])
        # Exclude resources that already existed in target file
        need_translated_str_resources = [res for res in root_str_resources if res.id not in
                                         target_id_set]

        if target_str_resources:
            print('There are {} strings in target file should be translated: {}'.format(len(
                target_str_resources), locale_file.path))
            translator.translate_file(need_translated_str_resources, target_str_resources,
                                      locale_file)


def main():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--exclude_languages', required=False,
                        help='list of languages to skip. For example, --exclude_languages=af,ca',
                        default='')
    parser.add_argument('-i', '--root_file', help='root/base resource path', required=False,
                        default=os.path.join(curr_dir, '..', 'app', 'src', 'main', 'res', 'values',
                                             'strings.xml'))

    args = parser.parse_args()
    run(set(args.exclude_languages.split(',')), args.root_file, Translator(), ResourceFinder())


if __name__ == "__main__":
    main()
