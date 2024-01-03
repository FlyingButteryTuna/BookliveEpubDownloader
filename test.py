from bs4 import BeautifulSoup

import tag_converter_helpers

tag_handlers = {
    'after': tag_converter_helpers.handle_after,
    'before': tag_converter_helpers.handle_before,
    'start': tag_converter_helpers.handle_start,
    'end': tag_converter_helpers.handle_end,
    'linespace': tag_converter_helpers.handle_linespace,
    'pad-before': tag_converter_helpers.handle_pad_before,
    'pad-after': tag_converter_helpers.handle_pad_after,
    'pad-start': tag_converter_helpers.handle_pad_start,
    'pad-end': tag_converter_helpers.handle_pad_end,
    'xsize': tag_converter_helpers.handle_xsize,
    'align': tag_converter_helpers.handle_align,
    'indent': tag_converter_helpers.handle_indent,
    'border-after-color': tag_converter_helpers.handle_border_after_color,
    'border-before-color': tag_converter_helpers.handle_border_before_color,
    'border-after-style': tag_converter_helpers.handle_border_after_style,
    'border-before-style': tag_converter_helpers.handle_border_before_style,
    'border-after-width': tag_converter_helpers.handle_border_after_width,
    'border-before-width': tag_converter_helpers.handle_border_before_width,
    'border-start-color': tag_converter_helpers.handle_border_start_color,
    'border-end-color': tag_converter_helpers.handle_border_end_color,
    'border-start-style': tag_converter_helpers.handle_border_start_style,
    'border-end-style': tag_converter_helpers.handle_border_end_style,
    'border-start-width': tag_converter_helpers.handle_border_start_width,
    'border-end-width': tag_converter_helpers.handle_border_end_width,
    'face': tag_converter_helpers.handle_face,
    'text-ori': tag_converter_helpers.handle_text_orientation,
    'weight': tag_converter_helpers.handle_weight,
    'charspace': tag_converter_helpers.handle_charspace,
    't-code': tag_converter_helpers.handle_tcode,
    'length': tag_converter_helpers.handle_length
}

styles_to_delete = [
    'honmonface',
    'honmonsize',
    'link',
    'bgcolor'
]

styles_to_skip = [
    'text-decoration',
    'word-break',
    'color',
]


props_to_skip = [
    't-class',
    'href',
    'name',
    'a',
    'height',
    'orgheight',
    'orgwidth',
    'shrink',
    'src',
    'width',
    'bgcolor',
    'stroke',
    'text',
    'valign',
    'cpl',
    'max-width',
    'areasize',
    'h',
    'mheight',
    'mwidth',
    'style',
    'class',
    'alt',  # todo gaiji alt (e.g. overlord vol1)
    'fontclear',  # todo idk what this is lol arifureta vol1
    'height'
]

props_to_keep = [
    'src',
    'class',
    'stroke',
    'height',
]

tags_to_skip = [
    't-pb',
    'a',
    'br'
]


def process_property(prop_name, prop_value):
    if prop_name in styles_to_skip:
        return prop_name, prop_value

    if prop_name in styles_to_delete:
        return None, None

    if prop_name == 'mbottom' or prop_name == 'mtop' or prop_name == 'mleft' or prop_name == 'mright':
        return prop_name[1:], prop_value
    handler = tag_handlers.get(prop_name)

    if handler is None:
        raise ValueError(f"No handler found for attribute '{prop_name}'")
    return handler(None, prop_value)


def extract_modified_style_content(style_content, class_mapping):
    soup = BeautifulSoup(style_content, 'html.parser')
    modified_styles = {}

    for style_element in soup.find_all('style'):
        for style_rule in style_element.text.split('}'):
            if '{' in style_rule:
                selector, properties = map(str.strip, style_rule.split('{', 1))
                class_name = selector.replace('.', '')

                if class_name in class_mapping:
                    selector = '.' + class_mapping[class_name]
                else:
                    continue

                for prop in properties.split(';'):
                    if ':' in prop:
                        prop_name, prop_value = map(str.strip, prop.split(':', 1))

                        new_prop_name, new_prop_value = process_property(prop_name, prop_value)
                        if new_prop_name is None and new_prop_value is None:
                            continue
                        if selector in modified_styles:
                            modified_styles[selector][new_prop_name] = new_prop_value
                        else:
                            modified_styles[selector] = {new_prop_name: new_prop_value}

    return modified_styles


def remove_t_param_tags(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    for t_param_tag in soup.find_all('t-param'):
        t_param_tag.unwrap()

    return str(soup)


def get_parent_t_pb(tag):
    parent = tag.find_parent('t-pb')
    return parent


def replace_tag(parent_t_pb, attr, value):
    if attr in props_to_skip:
        return attr, value

    handler = tag_handlers.get(attr)

    if handler is None:
        raise ValueError(f"No handler found for attribute '{attr}'")
    return handler(parent_t_pb, value)


def replace_tags(soup):
    tag_converter_helpers.handle_img(soup)
    tag_converter_helpers.handle_tmove(soup)
    tag_converter_helpers.handle_trb(soup)
    tag_converter_helpers.handle_tyoko(soup)
    tag_converter_helpers.handle_tfont(soup)
    tag_converter_helpers.handle_tem(soup)


def generate_css_classes(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    class_mapping = tag_converter_helpers.handle_tclass(soup)
    replace_tags(soup)

    body_tag = soup.find('body')
    modified_styles = extract_modified_style_content(html_content, class_mapping)

    if body_tag:
        css_classes = {}

        for tag in body_tag.find_all(True):
            tag_properties_tmp = tag.attrs

            tag_properties = {}
            parent_t_pb = get_parent_t_pb(tag)
            for key, value in tag_properties_tmp.items():
                new_key, new_value = replace_tag(parent_t_pb, key, value)
                tag_properties[new_key] = new_value
            tag.attrs = {}
            tag.attrs = tag_properties

        for tag in body_tag.find_all(True):
            if tag.name == 'a':
                continue
            tag_properties = tag.attrs
            if len(tag_properties) == 0:
                continue

            filtered_properties = {key: value for key, value in tag_properties.items() if key not in props_to_skip}

            properties_tuple = tuple(sorted(filtered_properties.items()))

            css_class = css_classes.get(properties_tuple)

            if not css_class:
                css_class = f"css_class_{len(css_classes) + 1}"
                css_classes[properties_tuple] = css_class

            tag.attrs = {}
            tag['class'] = [css_class]

            for prop in tag_properties:
                if prop in props_to_keep:
                    if tag.attrs.get(prop) is not None:
                        tag[prop] += tag_properties[prop]
                    else:
                        tag[prop] = tag_properties[prop]

            if tag.name == 't-pb':
                tag['valign'] = tag_properties['valign']


        new_html = soup

        css_file_content = ""
        for properties_tuple, css_class in css_classes.items():
            css_properties = "; ".join([f"{key}: {value}" for key, value in properties_tuple])
            css_file_content += f".{css_class} {{{css_properties}}}\n"

        with open('epub/item/style/generated_styles.css', 'w', encoding='utf-8') as css_file:
            css_file.write(css_file_content)
            for selector, properties in modified_styles.items():
                css_file.write(
                    f'{selector} {{ {" ".join([f"{key}: {value};" for key, value in properties.items()])} }}\n')

        return new_html

    else:
        print("No body tag found in the HTML.")
        return None


# with open('index2.xhtml', 'r', encoding='utf-8') as file:
#     html_content = file.read()
#
# html_content = remove_t_param_tags(html_content)
#
# new_html = generate_css_classes(html_content)
#
# if new_html:
#     with open('teeeeeest.html', 'w', encoding='utf-8') as new_file:
#         new_file.write(new_html.prettify())
#
# print(
#     "CSS classes have been generated and written to 'generated_styles.css'. New HTML with classes has been written to 'new_file.html'.")


# def write_unique_tag_names_to_file(html_content, output_file):
#     soup = BeautifulSoup(html_content, 'html.parser')
#     tag_names = {tag.name for tag in soup.find_all()}
#
#     with open(output_file, 'w') as file:
#         file.write("Unique tag names:\n")
#         for name in tag_names:
#             file.write(name + '\n')
#
# write_unique_tag_names_to_file(html_content, 'tags.txt')
