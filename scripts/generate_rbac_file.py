import subprocess
import xml.etree.ElementTree as ET
import string
import secrets
import argparse
import bcrypt

from os import environ, path


def create_user_element(parent, username, password, role_id):
    """
    Create a user XML element and append it to the parent element.

    :param parent: The parent XML element to which this user will be appended.
    :param username: The username for the user.
    :param password: The password for the user.
    :param role_id: The role ID for the user.
    """
    user = ET.SubElement(parent, "user")

    name_element = ET.SubElement(user, "name")
    name_element.text = username

    password_element = ET.SubElement(user, "password")
    password_element.text = password

    roles_element = ET.SubElement(user, "roles")
    role_id_element = ET.SubElement(roles_element, "id")
    role_id_element.text = role_id


def create_role_element(parent, topic_prefix:str, role_id):
    """
    Create a role XML element and append it to the parent element.

    :param parent: The parent XML element to which this role will be appended.
    :param role_id: The role ID.
    """
    role = ET.SubElement(parent, "role")

    role_id_element = ET.SubElement(role, "id")
    role_id_element.text = role_id

    permissions = ET.SubElement(role, "permissions")
    permission = ET.SubElement(permissions, "permission")

    topic_element = ET.SubElement(permission, "topic")

    if role_id == "publisher":

        topic_element.text = '/'.join((topic_prefix,"${{clientid}}",'+'))
        activity_element = ET.SubElement(permission, "activity")
        activity_element.text = "PUBLISH"

        retain_element = ET.SubElement(permission, "retain")
        retain_element.text = "ALL"

    elif role_id == "subscriber":
        topic_element.text = '/'.join((topic_prefix,"#"))
        activity_element = ET.SubElement(permission, "activity")
        activity_element.text = "SUBSCRIBE"

    elif role_id == "transformer":
        topic_element.text = '/'.join((topic_prefix, "#"))


def generate_credentials_xml(file_name: str, topic_prefix:str, hash: str, publishers_count: int, subscribers_count: int,
                             pub_id_prefix="publisher", sub_id_prefix="subscriber"):
    # Create the root element
    root = ET.Element("file-rbac")


    # Create the 'users' element
    users = ET.SubElement(root, "users")
    roles_element = ET.SubElement(root, "roles")

    # Loop to create publisher users based on the publishers_count
    for i in range(1, publishers_count + 1):
        username = f"{pub_id_prefix}{i}"
        role_id = "publisher"
        create_user_element(users, username, hash, role_id)

    # Loop to create subscribers users based on the publishers_count
    for i in range(1, subscribers_count + 1):
        username = f"{sub_id_prefix}{i}"
        role_id = "subscriber"
        create_user_element(users, username, hash, role_id)

    create_role_element(roles_element, topic_prefix, role_id="publisher")
    create_role_element(roles_element, topic_prefix, role_id="subscriber")

    # Create the tree and write to the specified file
    tree = ET.ElementTree(root)

    with open(file_name, 'wb') as f:
        tree.write(f, encoding="UTF-8", xml_declaration=True)  #, method="xml"


def generate_pass() -> str:
    alphabet_premium = string.ascii_letters + string.digits + '.%_-<=>?@'
    pwd = ''.join(secrets.choice(alphabet_premium) for i in range(16))

    return pwd


def generate_hash(password: str) -> str:
    userBytes = password.encode('utf-8')
    # generating the salt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(userBytes, salt)
    return hashed


def get_password(password: str) -> str:
    parent = path.dirname(path.dirname(__file__))
    jar_file = path.join(parent,'monitoring/hivemq-file-rbac-extension/hivemq-file-rbac-extension-4.6.2.jar')
    java_command = ['java', '-jar', jar_file, '-p', password]

    try:
        # Run the Java command
        result = subprocess.run(java_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Get the stdout
        output_lines = result.stdout.split('\n')

        # Get the third line if it exists
        if len(output_lines) >= 3:
            third_line = output_lines[2]
            return third_line
        else:
            print("Output does not have a third line.")
            print("STDERR:\n", result.stderr)  # Usually for error messages
            return result

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the Java command: {e}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.output}")
        print(f"Error: {e.stderr}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an XML file with user credentials.")
    parser.add_argument("--publishers", type=int, required=True, help="Number of publisher users to create.")
    parser.add_argument("--subscribers", type=int, required=True, help="Number of subscriber users to create.")
    parser.add_argument("--transformers", type=int, required=True, help="Number of transformers users to create.")
    parser.add_argument("--topic_prefix", type=str, default="site1", help="Topic prefix.")

    args = parser.parse_args()
    publishers_count = args.publishers
    subscribers_count = args.subscribers
    transformers_count = args.transformers
    topic_prefix=args.topic_prefix

    ingestion = "credentials_ingestion.xml"
    core = "credentials_core.xml"

    # Password broker 1
    pwd1=generate_pass()
    #print(pwd1)
    #hashed1 = generate_hash(pwd1).decode()
    hashed1=get_password(pwd1)
    #print(hashed1)

    # Password broker 2
    pwd2 = generate_pass()
    #print(pwd2)
    # hashed2 = generate_hash(pwd2).decode()
    hashed2 = get_password(pwd2)
    #print(hashed2)

    generate_credentials_xml(file_name=ingestion, topic_prefix=topic_prefix, hash=hashed1,
                             publishers_count=publishers_count, subscribers_count=transformers_count,
                             sub_id_prefix="transformer")

    print(f"{ingestion} has been generated successfully.")

    generate_credentials_xml(file_name=core, topic_prefix=topic_prefix, hash=hashed2,
                             publishers_count=transformers_count, subscribers_count=transformers_count,
                             pub_id_prefix="transformer")

    print(f"{core} has been generated successfully.")

    environ['PASSWORD1'] = pwd1
    environ['PASSWORD2'] = pwd2

    print("Generated password saved into environment variables \'PASSWORD1\' and \'PASSWORD2\'.")


