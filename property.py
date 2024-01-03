from bs4 import BeautifulSoup
import math

def write_unique_property_names(html_content):
    # Parse the HTML content with Beautiful Soup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the body tag
    body_tag = soup.find('body')

    if body_tag:
        # Initialize a set to store unique property names
        unique_property_names = set()

        # Iterate through all tags within the body
        for tag in body_tag.find_all(True):
            # Get tag properties (attributes)
            tag_properties = tag.attrs

            # Add the property names to the set
            unique_property_names.update(tag_properties.keys())

        # Write the unique property names to a file
        with open('unique_property_names.txt', 'w', encoding='utf-8') as prop_names_file:
            for prop_name in sorted(unique_property_names):
                prop_names_file.write(f"{prop_name}\n")

        print("Unique property names have been written to 'unique_property_names.txt'.")

    else:
        print("No body tag found in the HTML.")

# Read the HTML file
# with open('index2_t.xhtml', 'r', encoding='utf-8') as file:
#     html_content = file.read()
#
# # Write unique property names to a file
# write_unique_property_names(html_content)

