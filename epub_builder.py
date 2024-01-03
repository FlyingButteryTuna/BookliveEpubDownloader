from bs4 import BeautifulSoup

import standard_opf_helpers
import test
import shutil
import re
from downloader import img_descrambler
from bs4 import Tag, NavigableString
import requests
from downloader import deofuscator_helpers
from downloader import api_requests
import cv2
import os


def remove_tag_without_attributes_or_children(soup, tag_name):
    for tag in soup.find_all(tag_name):
        if not tag.attrs and not tag.contents:
            tag.decompose()

def find_tpb_tags(element):
    tpb_tags = []
    for child in element.find_all('t-pb', recursive=False):
        tpb_tags.append(child)
        tpb_tags.extend(find_tpb_tags(child))
    return tpb_tags

def get_stroke(t_pb):
    if t_pb['stroke'] == 'vertical':
        return 'vrtl'
    elif t_pb['stroke'] == 'horizontal':
        return 'hltr'


def get_page_type(name):
    if 'p-caution' in name:
        return 'p-caution'
    elif 'p-colophon' in name:
        return 'p-colophon'
    elif 'p-titlepage' in name:
        return 'p-titlepage'
    else:
        return 'p-text'


def convert_name(input_string):
    parts = input_string.split('_')

    new_name = '_'.join(parts[2:])
    new_name = new_name.replace('_xhtml', '.xhtml')

    return new_name


def get_img_and_a_tag(div):
    img_tag = div.find('img')

    a_tag = div.find('a')
    a_name_attribute = a_tag.get('name') if a_tag else None

    for child in div.children:
        if child.name and child.get_text(strip=True):
            return None, None

    return img_tag, a_name_attribute


def get_base_xhtml(stroke, title, body_class, div_class):
    with open('base_xhtml.xhtml', 'r', encoding='utf-8') as base_file:
        content = base_file.read()

    base_xhtml = BeautifulSoup(content, 'html.parser')
    base_xhtml.find('html')['class'] = stroke
    base_xhtml.find('title').string = title

    base_xhtml.find('body')['class'] = body_class
    base_xhtml.find('div')['class'] = div_class
    base_file.close()

    return base_xhtml


def handle_cover(soup, title, epub_folder):
    img, name = get_img_and_a_tag(soup.find('div'))
    if img is None:
        print('Cover error')
        return False
    return handle_pages_img(soup, img, name, title, epub_folder)


def handle_pages_img(soup, img, name, title, epub_folder):
    base = get_base_xhtml( ['hltr'], title, ['p-image'], ['main align-center'])
    name_converted = convert_name(name)
    main_div = base.find('div')
    new_paragraph = soup.new_tag('p')
    new_paragraph.append(img)
    main_div.append(new_paragraph)
    with open(epub_folder + '/item/xhtml/' + name_converted, 'w', encoding='utf-8') as conver_file:
        conver_file.write(str(base))
    return name, name_converted


def handle_pages_text(soup, name, t_pb, title, epub_folder):
    stroke = get_stroke(t_pb)
    page_type = get_page_type(name)

    base = get_base_xhtml([stroke], title, [page_type], ['main'])
    t_pb.name = 'div'
    main_div = base.find('div')
    if t_pb.attrs.get('stroke') is None:
        print()
    if t_pb['valign'] == 'middle' and t_pb['stroke'] == 'vertical':
        base.find('html')['class'] = ['hltr']
        base.find('body').find('div')['class'] += ['vrtl', 'block-align-center']

    del t_pb['stroke']

    main_div.append(t_pb)
    with open(epub_folder + '/item/xhtml/' + name, 'w', encoding='utf-8') as page_file:
        page_file.write(str(base))


def clone(el):
    if isinstance(el, NavigableString):
        return type(el)(el)

    copy = Tag(None, el.builder, el.name, el.namespace, el.nsprefix)
    copy.attrs = dict(el.attrs)
    for attr in ('can_be_empty_element', 'hidden'):
        setattr(copy, attr, getattr(el, attr))
    for child in el.contents:
        copy.append(clone(child))
    return copy


def set_toc_mapping(soup):
    body = soup.find('body')
    xhtml_files_mapping = {}
    pages = [body.find('div')] + body.find_all('t-pb')

    for t_pb in pages:
        a_file_name = t_pb.find('a')
        converted_name = convert_name(a_file_name['name'])
        xhtml_files_mapping[converted_name] = a_file_name['name']

    for a in body.find_all('a', href=True):
        href = a.get('href')
        file_name = [fn for fn in list(xhtml_files_mapping.keys()) if href[1:].split('_')[0] in xhtml_files_mapping[fn]]
        if len(file_name) == 0:
            continue
        if 'xhtml' not in href:
            a['href'] = file_name[0] + href
        else:
            a['href'] = file_name[0]


def build_pages(soup, title, epub_folder):
    remove_tag_without_attributes_or_children(soup, 't-pb')
    toc = soup.find('t-contents')
    if toc:
        set_toc_mapping(soup)

    xhtml_files = []
    name, name_converted = handle_cover(soup, title, epub_folder)
    xhtml_files.append(name_converted)


    for t_pb_tag in soup.find_all('t-pb'):
        copy_tag = clone(t_pb_tag)
        t_pb_child = copy_tag.find('t-pb')
        if t_pb_child:
            t_pb_child.replace_with('')
        img, name = get_img_and_a_tag(copy_tag)
        if img is not None:
            name, name_converted = handle_pages_img(soup, img, name, title, epub_folder)
            xhtml_files.append(name_converted)
        else:
            a_tag = copy_tag.find('a')
            a_name_attribute = a_tag.get('name') if a_tag else None
            a_name_attribute_converted = convert_name(a_name_attribute)
            xhtml_files.append(a_name_attribute_converted)
            a_tag.replace_with('')
            if toc:
                a_id = copy_tag.find('a')
                if a_id is not None and a_id.attrs.get('href') is None:
                    empty_div = soup.new_tag('div')
                    empty_div['id'] = a_id['name']
                    a_id.replace_with(empty_div)

            handle_pages_text(soup, a_name_attribute_converted, copy_tag, title, epub_folder)
    return xhtml_files


def download_images(soup, content_info_json, session, epub_folder):
    ctbl = deofuscator_helpers.get_array(content_info_json['items'][0]['ctbl'], content_info_json['items'][0]['seed'])
    ptbl = deofuscator_helpers.get_array(content_info_json['items'][0]['ptbl'], content_info_json['items'][0]['seed'])
    items = content_info_json['items'][0]
    for img in soup.find_all('img'):
        file_name = os.path.basename(img['src'])
        path = f'img/{file_name}'

        img = api_requests.get_img(session, items['ContentID'], path, items['p'], items['ContentDate'])

        desc = img_descrambler.DescrabmlerType1(ctbl, ptbl, path, img)
        blank_image = desc.descrabmble_img()
        cv2.imwrite(str(os.path.join(epub_folder + '/item/image', file_name)), blank_image)


def build_opf(content_info_json, epub_folder, xhtml_files):
    with open('base_opf.xhtml') as base_opf:
        content = base_opf.read()

    items = content_info_json['items'][0]

    base_opf = BeautifulSoup(content, 'html.parser')

    # metadata
    metadata_tag = base_opf.find('metadata')
    standard_opf_helpers.handle_title(base_opf, metadata_tag, items['Title'], items['TitleRuby'])
    standard_opf_helpers.handle_authors(base_opf, metadata_tag, items['Authors'])
    standard_opf_helpers.handle_publisher(base_opf, metadata_tag, items['Publisher'], items['PublisherRuby'])
    standard_opf_helpers.handle_bl_id(base_opf, metadata_tag, items['ContentID'])
    standard_opf_helpers.handle_modified_date(base_opf, metadata_tag, items['ContentDate'])

    # manifest
    manifest_tag = base_opf.find('manifest')
    standard_opf_helpers.handle_images(base_opf, manifest_tag, epub_folder + '/item')
    standard_opf_helpers.handle_xhtmls(base_opf, manifest_tag, epub_folder + '/item')

    # spine
    spine_tag = base_opf.find('spine')
    standard_opf_helpers.handle_spine(base_opf, spine_tag, xhtml_files)

    with open(epub_folder + '/item/standard.opf', 'w', encoding='utf-8') as standard_file:
        standard_file.write(str(base_opf))


def construct_epub(session, html_content, content_info_json):
    try:
        shutil.rmtree('epub')
    except Exception as e:
        print(f"An error occurred: {e}")

    shutil.copytree('epub_base', 'epub')

    # with open('index2.xhtml', 'r', encoding='utf-8') as file:
    #     html_content = file.read()
    html_content = test.remove_t_param_tags(html_content)

    new_html = test.generate_css_classes(html_content)

    xhtml_files = build_pages(new_html, 'TITLE', 'epub')
    download_images(new_html, content_info_json, session, 'epub')
    build_opf(content_info_json, 'epub', xhtml_files)



