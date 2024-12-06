import os
import glob


def generate_aws_certificate_header(certs):
    """Generates the aws_certificate.h file content.

    Args:
        certs (dict): A dictionary containing the certificate data, 
                      where keys are certificate names ('mqtt_root_ca', 
                      'mqtt_client_cert', 'mqtt_private_key') and 
                      values are the certificate strings.

    Returns:
        str: The content of aws_certificate.h
    """

    header_content = """#ifndef _MQTT_CERTIFICATE_H_
#define _MQTT_CERTIFICATE_H_

"""

    for cert_name, cert_data in certs.items():
        header_content += f"/*\n * {cert_name.replace('_', ' ').title()} \n */\n"  # Add comment for each cert

        c_array = []
        for line in cert_data.splitlines():
            stripped_line = line.strip()
            if stripped_line:
                c_array.append(f"\"{stripped_line}\\n\"")  # Add \r\n for consistency

        c_array_content = "\n\t\t".join(c_array) # added tab for better format
        header_content += f"const char {cert_name}[] =\n\t\t{c_array_content};\n\n"


    header_content += "#endif /* _MQTT_CERTIFICATE_H_ */"
    return header_content

def read_certificate_file(filepath):
    """Reads a certificate file and returns its content as a string."""
    try:
        with open(filepath, "r") as f:
            cert_data = f.read()
        return cert_data
    except FileNotFoundError:
        print(f"Error: Certificate file not found at {filepath}")

def find_client_certificate(directory):
    """Finds the client certificate file in the given directory."""
    cert_pattern = "*-certificate.pem.crt"
    matches = glob.glob(os.path.join(directory, cert_pattern))
    if matches:
        return matches[0]
    else:
        return None
    
def find_private_key(directory):
    """Finds the private key file in the given directory."""
    private_key_pattern = "*-private.pem.key"  # The pattern to search for
    matches = glob.glob(os.path.join(directory, private_key_pattern))
    if matches:
        return matches[0]  # Return the first match
    else:
        return None
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__)) # Get current script's directory
    rootca_filepath = os.path.join(script_dir, "AmazonRootCA1.pem")
    client_cert_filepath = find_client_certificate(script_dir)  # Call the new function
    private_key_filepath = find_private_key(script_dir) # call it here to find
    output_filepath = os.path.join(script_dir, "aws_certificate.h") # output in same folder
    certs = {
        "mqtt_root_ca": read_certificate_file(rootca_filepath),
        "mqtt_client_cert": read_certificate_file(client_cert_filepath),
        "mqtt_private_key": read_certificate_file(private_key_filepath),        # Add other certificates if needed
    }
    # Replace ... with actual certificate content.

    # Check if any of the certificate files were not found
    if any(cert is None for cert in certs.values()):
      print("Error reading one or more certificate files. Exiting.")  # and exit or handle as needed
      return

    aws_certificate_h_content = generate_aws_certificate_header(certs)

    with open("aws_certificate.h", "w") as f:
        f.write(aws_certificate_h_content)

    print("aws_certificate.h generated successfully.")


if __name__ == "__main__":
    main()
