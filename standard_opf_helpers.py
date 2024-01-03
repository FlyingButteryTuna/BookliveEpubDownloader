from datetime import datetime
import os


def convert_date_format(input_date):
    # Convert the input date string to a datetime object
    date_object = datetime.strptime(input_date, '%Y%m%d%H%M%S')

    # Format the datetime object to the desired output format
    output_date = date_object.strftime('%Y-%m-%dT%H:%M:%SZ')

    return output_date


def handle_title(soup, metadata_tag, title, ruby):
    title_tag = soup.new_tag('dc:title')
    title_tag.attrs = {
        'id': 'title'
    }
    title_tag.string = title
    metadata_tag.append(title_tag)

    title_ruby_tag = soup.new_tag('meta')
    title_ruby_tag.attrs = {
        'refines': '#title',
        'property': 'file-as'
    }
    title_ruby_tag.string = ruby
    metadata_tag.append(title_ruby_tag)


def handle_authors(soup, metadata_tag, authors):
    i = 1
    for author in authors:
        author_tag = soup.new_tag('dc:creator')
        author_tag.attrs = {
            'id': 'creator0' + str(i)
        }
        author_tag.string = author['Name']
        metadata_tag.append(author_tag)

        author_ruby_tag = soup.new_tag('meta')
        author_ruby_tag.attrs = {
            'refines': '#creator0' + str(i),
            'property': 'file-as'
        }
        author_ruby_tag.string = author['Ruby']
        metadata_tag.append(author_ruby_tag)

        display_seq_tag = soup.new_tag('meta')
        display_seq_tag.attrs = {
            'refines': '#creator0' + str(i),
            'property': 'display-seq'
        }
        display_seq_tag.string = str(i)
        metadata_tag.append(display_seq_tag)

        if len(author['Role']) != 0:
            role_tag = soup.new_tag('meta')
            role_tag.attrs = {
                'refines': '#creator0' + str(i),
                'property': 'role',
                'scheme': 'marc:relators'
            }
            role_tag.string = author['Role']
            metadata_tag.append(role_tag)


def handle_publisher(soup, metadata_tag, publisher, ruby):
    publisher_tag = soup.new_tag('dc:publisher')
    publisher_tag.attrs = {
        'id': 'publisher'
    }
    publisher_tag.string = publisher
    metadata_tag.append(publisher_tag)

    publisher_ruby_tag = soup.new_tag('meta')
    publisher_ruby_tag.attrs = {
        'refines': '#publisher',
        'property': 'file-as'
    }
    publisher_ruby_tag.string = ruby
    metadata_tag.append(publisher_ruby_tag)


def handle_bl_id(soup, metadata_tag, bl_id):
    identifier_tag = soup.new_tag('dc:identifier')
    identifier_tag.attrs = {
        'id': 'bl-id'
    }
    identifier_tag.string = bl_id
    metadata_tag.append(identifier_tag)


def handle_modified_date(soup, metadata_tag, modified_date):
    modified_date_tag = soup.new_tag('meta')
    modified_date_tag.attrs = {
        'property': 'dcterms:modified'
    }
    modified_date_tag.string = convert_date_format(modified_date)
    metadata_tag.append(modified_date_tag)


def handle_images(soup, manifest_tag, epub_folder):
    image_folder = os.path.join(epub_folder, 'image')

    # Check if the image folder exists
    if not os.path.exists(image_folder) or not os.path.isdir(image_folder):
        print(f"Image folder '{image_folder}' not found.")
        return

    # Iterate over image files in the folder
    for filename in os.listdir(image_folder):
        # Check if the file has a valid image extension
        valid_extensions = ['.jpg', '.png', '.svg']
        if any(filename.lower().endswith(ext) for ext in valid_extensions):
            image_id = os.path.splitext(filename)[0]
            image_path = os.path.join('image', filename)

            # Determine the media type based on the file extension
            if filename.lower().endswith('.jpg'):
                media_type = 'image/jpeg'
            elif filename.lower().endswith('.png'):
                media_type = 'image/png'
            elif filename.lower().endswith('.svg'):
                media_type = 'image/svg+xml'
            else:
                # Handle other image types as needed
                continue

            # Create a new item tag
            item_tag = soup.new_tag('item')
            item_tag['media-type'] = media_type
            item_tag['id'] = image_id
            item_tag['href'] = image_path
            if image_id == 'cover':
                item_tag['properties'] = 'cover-image'

            # Append the item tag to the manifest tag
            manifest_tag.append(item_tag)


def handle_xhtmls(soup, manifest_tag, epub_folder):
    xhtml_folder = os.path.join(epub_folder, 'xhtml')

    # Check if the xhtml folder exists
    if not os.path.exists(xhtml_folder) or not os.path.isdir(xhtml_folder):
        print(f"XHTML folder '{xhtml_folder}' not found.")
        return

    # Iterate over xhtml files in the folder
    for filename in os.listdir(xhtml_folder):
        # Check if the file has a valid xhtml extension
        if filename.lower().endswith('.xhtml'):
            xhtml_id = os.path.splitext(filename)[0]
            xhtml_path = os.path.join('xhtml', filename)

            # Create a new item tag
            item_tag = soup.new_tag('item')
            item_tag['media-type'] = 'application/xhtml+xml'
            item_tag['id'] = xhtml_id
            item_tag['href'] = xhtml_path

            # Append the item tag to the manifest tag
            manifest_tag.append(item_tag)


def handle_spine(soup, spine_tag, xhtml_file_names):
    for xhtml_filename in xhtml_file_names:
        xhtml_id = os.path.splitext(xhtml_filename)[0]

        # Create a new itemref tag
        itemref_tag = soup.new_tag('itemref')
        itemref_tag['linear'] = 'yes'
        itemref_tag['idref'] = xhtml_id

        # Append the itemref tag to the spine tag
        spine_tag.append(itemref_tag)


