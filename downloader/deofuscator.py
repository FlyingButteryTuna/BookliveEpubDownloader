import re
from downloader import deofuscator_helpers

pattern = re.compile(r'&\$(.*?);')


def process_text(text, arrays):
    matches = pattern.findall(text)

    replacements = [deofuscation_helpers.deobfuscate_char(match, arrays[0], arrays[1]) for match in matches]

    for match, replacement in zip(matches, replacements):
        text = text.replace(f'&${match};', replacement)

    return text


def process_html(html, content_info_json):
    items = content_info_json['items'][0]
    arrays = [deofuscation_helpers.get_array(items['stbl'], items['seed']),
              deofuscation_helpers.get_array(items['ttbl'], items['seed'])]

    # Split HTML into parts, cuz long books make things dummy slow
    parts = html.split('</div>')

    processed_parts = [process_text(part, arrays) + '</div>' for part in parts]
    processed_html = ''.join(processed_parts)

    return processed_html
