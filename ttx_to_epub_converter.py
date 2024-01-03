from bs4 import BeautifulSoup
from pprint import pprint



def remove_t_param_tags(html_content):
    # Parse the HTML content with Beautiful Soup

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all t-param tags
    for t_param_tag in soup.find_all('t-param'):
        # Replace the t-param tag with its contents (children)
        t_param_tag.unwrap()

    # Return the modified HTML
    return str(soup)


tags = ['a', 'body', 'br', 'div', 'h1', 'h2', 'h3', 'head', 'html', 'style',
        't-code', 't-contents', 't-em', 't-font', 't-img', 't-move', 't-param',
        't-pb', 't-rb', 't-time', 't-yoko', 'title']


with open('index2.xhtml', 'r', encoding='utf-8') as file:
    html = file.read()

html = remove_t_param_tags(html)

soup = BeautifulSoup(html, 'html.parser')

with open('index2_t.xhtml', 'w', encoding='utf-8') as file:
    file.write(soup.prettify())
# parent = soup.find('body')


# output_file_path = 'tag_information.txt'
#
# with open(output_file_path, 'w', encoding='utf-8') as output_file:
#     def get_ancestry(tag):
#         ancestry = []
#         parent = tag.parent
#         while parent:
#             ancestry.append(parent.name)
#             parent = parent.parent
#         return ancestry[::-1]
#
#     # Iterate through each tag and write its text to the file (not its children's text)
#     for tag in all_tags:
#         # Check if the tag has any child tags
#         if not tag.find_all(True):
#             # Get tag name
#             tag_name = tag.name
#
#             # Get tag text (if any)
#             tag_text = tag.get_text(strip=True)
#             tag_properties = tag.attrs
#             tag_ancestry = get_ancestry(tag)
#
#             # Write tag information to the file
#             output_file.write(f"Tag Name: {tag_name}\n")
#             if tag.name != 't-pb' and tag.name != 'html' and tag.name != 'body':
#                 output_file.write(f"Tag Text: {tag_text}\n")
#             output_file.write(f"Tag Properties: {tag_properties}\n")
#             output_file.write(f"Tag Ancestry: {' > '.join(tag_ancestry)}\n")
#             output_file.write("=" * 40 + "\n")
#
#
# print(f"Tag information has been written to '{output_file_path}'.")
# unique_property_combinations = set()
#
# # Iterate through all tags and print their properties
# for tag in soup.find_all(True):
#     # Get tag properties (attributes)
#     tag_properties = tag.attrs
#
#     property_names = tuple(sorted(tag_properties.keys()))
#
#     # Add the tuple of property names to the set
#     unique_property_combinations.add(property_names)
#
# # Print the count of unique property combinations
# print(f"\nTotal number of unique property combinations: {len(unique_property_combinations)}")
# pprint(unique_property_combinations)

