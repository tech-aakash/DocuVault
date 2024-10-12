import boto3
from botocore.exceptions import ClientError
from neo4j import GraphDatabase
import random
import requests
from PIL import Image
import pytesseract
import cv2
import numpy as np
from ultralytics import YOLO
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib

# Initialize AWS Cognito client
cognito_client = boto3.client('cognito-idp', region_name='us-east-1')

from dotenv import load_dotenv
import os

# Load environment variables from api.env
load_dotenv('api.env')

# Now you can use the environment variables, for example:
NEO4J_LINK = os.getenv('NEO4J_LINK')
NEO4J_API_KEY = os.getenv('NEO4J_API_KEY')
COGNITO_CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
BREVO_API_KEY = os.getenv('BREVO_API_KEY')

def sign_up_user(email):
    try:
        response = cognito_client.sign_up(
            ClientId=COGNITO_CLIENT_ID,  # Replace with your App Client ID
            Username=email,
            Password='TemporaryPassword123!',  # Use a strong temporary password
            UserAttributes=[
                {'Name': 'email', 'Value': email},
            ],
        )
        return response
    except ClientError as e:
        return str(e)

def confirm_user_sign_up(email, otp):
    try:
        response = cognito_client.confirm_sign_up(
            ClientId=COGNITO_CLIENT_ID,  # Replace with your App Client ID
            Username=email,
            ConfirmationCode=otp
        )
        return response
    except ClientError as e:
        return str(e)

def forgot_password(email):
    try:
        response = cognito_client.forgot_password(
            ClientId=COGNITO_CLIENT_ID,  # Replace with your App Client ID
            Username=email
        )
        return response
    except ClientError as e:
        return str(e)

def confirm_forgot_password(email, otp, new_password):
    try:
        response = cognito_client.confirm_forgot_password(
            ClientId=COGNITO_CLIENT_ID,  # Replace with your App Client ID
            Username=email,
            ConfirmationCode=otp,
            Password=new_password
        )
        return response
    except ClientError as e:
        return str(e)

# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_LINK, auth=("neo4j", NEO4J_API_KEY))

def is_email_registered(email):
    with driver.session() as session:
        result = session.run("MATCH (u:User {email: $email}) RETURN u", email=email)
        return result.single() is not None

def store_user(user_id, email):
    with driver.session() as session:
        session.run("CREATE (u:User {user_id: $user_id, email: $email})", user_id=user_id, email=email)

def generate_user_id():
    return str(random.randint(10000, 99999))

def get_user_id_from_email(email):
    with driver.session() as session:
        result = session.run("MATCH (u:User {email: $email}) RETURN u.user_id AS user_id", email=email)
        record = result.single()
        if record:
            return record["user_id"]
        return None

def send_user_id_email(email, user_id):
    url = "https://api.brevo.com/v3/smtp/email"
    api_key = BREVO_API_KEY  # Replace with your Brevo API key
    sender_email = "tesla.nikola0305@gmail.com"  # Replace with your verified sender email
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    data = {
        "sender": {"name": "Your Name", "email": sender_email},
        "to": [{"email": email}],
        "subject": "Your User ID",
        "textContent": f"Your User ID is: {user_id}"
    }

    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 201:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email: {response.text}")

def perform_ocr(img, box):
    x1, y1, x2, y2 = map(int, box[:4])
    cropped_img = img[y1:y2, x1:x2]
    text = pytesseract.image_to_string(cropped_img, config='--psm 6')
    return text.strip()

def extract_year_of_birth(dob):
    # Check if the DOB is in the format 'YYYY-MM-DD'
    if '-' in dob:
        parts = dob.split('-')
        if len(parts) == 3 and len(parts[0]) == 4 and parts[0].isdigit():
            return parts[0]

    # Check if the DOB is in the format 'YYYY'
    if len(dob) == 4 and dob.isdigit():
        return dob

    # Use regex to find a 4-digit year in other formats
    match = re.search(r'\b(19|20)\d{2}\b', dob)
    if match:
        return match.group(0)

    # If no valid year is found, return an error message or handle accordingly
    return None

def run_model_on_document(file_path, doc_type):
    model = YOLO('best.pt')  # Adjust path if necessary

    image = Image.open(file_path).convert('RGB')
    img_cv2 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    results = model(image)

    boxes = results[0].boxes.xyxy.cpu().numpy()
    labels = results[0].boxes.cls.cpu().numpy()
    class_names = model.names
    labels = [class_names[int(cls)] for cls in labels]

    # Define expected fields for the document
    expected_fields = {
        'Name': '',
        'Identity Number': '',
        'Date of Birth': ''
    }

    # Additional field based on document type
    additional_fields = {
        'Voter ID': 'Election Commission of India',
        'Pan Card': 'Income Tax Department',
        'Aadhar Card': 'Aadhar',
        'Passport': 'Republic of India'
    }

    extracted_info = {}
    for box, label in zip(boxes, labels):
        ocr_text = perform_ocr(img_cv2, box)
        standardized_label = label.replace('-', ' ')
        extracted_info[standardized_label] = ocr_text

        # Extract year of birth if DOB field is detected
        if label.lower() == 'date-of-birth':
            year_of_birth = extract_year_of_birth(ocr_text)
            extracted_info['Year of Birth'] = year_of_birth
            extracted_info['Date of Birth'] = ocr_text  # Ensure Date of Birth is also included

    # Initialize missing fields with empty values
    for field in expected_fields:
        if field not in extracted_info:
            extracted_info[field] = expected_fields[field]

    # Add additional field based on document type
    if doc_type in additional_fields:
        extracted_info['Authority'] = additional_fields[doc_type]

    return extracted_info



def generate_encryption_key(year_of_birth, user_id):
    combined_key = str(year_of_birth) + user_id
    print(combined_key)
    hashed_key = hashlib.sha256(combined_key.encode('utf-8')).digest()  # Produce a 32-byte hash
    return hashed_key

def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv, ct

def decrypt_data(iv, ct, key):
    iv = base64.b64decode(iv)
    ct = base64.b64decode(ct)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8')


import json

def store_encrypted_document(user_id, year_of_birth, document_type, extracted_details):
    key = generate_encryption_key(year_of_birth, user_id)

    encrypted_details = {}
    for field, value in extracted_details.items():
        if field != 'year_of_birth':  # No need to encrypt the year of birth
            iv, ct = encrypt_data(value, key)
            encrypted_details[field] = {'iv': iv, 'ct': ct}

    # Serialize the encrypted details to a JSON string
    encrypted_details_json = json.dumps(encrypted_details)

    # Replace spaces with underscores in the document type for Cypher label
    document_type = document_type.replace(' ', '_')

    with driver.session() as session:
        # Match the existing User node
        user_node = session.run("MATCH (u:User {user_id: $user_id}) RETURN u", user_id=user_id).single()
        
        if user_node:
            # Create the Document node and establish the relationship
            session.run(
                f"""
                CREATE (d:{document_type} {{details: $encrypted_details_json}})
                WITH d
                MATCH (u:User {{user_id: $user_id}})
                CREATE (u)-[:HAS_DOCUMENT]->(d)
                """,
                user_id=user_id,
                encrypted_details_json=encrypted_details_json
            )

def get_issued_documents(user_id):
    issued_documents = {}
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {user_id: $user_id})-[:HAS_DOCUMENT]->(d)
            RETURN labels(d)[0] AS doc_type, d.details AS details
            """, 
            user_id=user_id
        )
        
        for record in result:
            doc_type = record['doc_type']
            details = record['details']
            issued_documents[doc_type] = details
    
    return issued_documents

# Add this function to your helper.py

def check_uploaded_document(user_id, doc_type):
    """
    Checks if the user has already uploaded a document of the specified type.
    
    Parameters:
    - user_id: The user's ID
    - doc_type: The type of the document to check (e.g., "Pan Card")
    
    Returns:
    - True if the document type is already uploaded, False otherwise
    """
    # Replace spaces with underscores in the document type for Cypher label
    doc_type_label = doc_type.replace(' ', '_')
    
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {user_id: $user_id})-[:HAS_DOCUMENT]->(d)
            WHERE labels(d)[0] = $doc_type_label
            RETURN d
            """, 
            user_id=user_id,
            doc_type_label=doc_type_label
        )
        
        # If any record is returned, the document type has already been uploaded
        return result.single() is not None

# Check if the given user ID exists in the Neo4j database
def check_user_id_exists(user_id):
    with driver.session() as session:
        result = session.run("MATCH (u:User {user_id: $user_id}) RETURN u", user_id=user_id)
        return result.single() is not None

# Send OTP to the family member's registered email using AWS Cognito
def send_otp_to_user(user_id):
    with driver.session() as session:
        result = session.run("MATCH (u:User {user_id: $user_id}) RETURN u.email AS email", user_id=user_id)
        email = result.single()["email"]

    try:
        response = cognito_client.forgot_password(
            ClientId=COGNITO_CLIENT_ID,  # Replace with your actual Cognito App Client ID
            Username=email
        )
        return True
    except ClientError as e:
        return False

# Confirm the OTP for the user using AWS Cognito
def confirm_otp(user_id, otp):
    with driver.session() as session:
        result = session.run("MATCH (u:User {user_id: $user_id}) RETURN u.email AS email", user_id=user_id)
        email = result.single()["email"]

    try:
        response = cognito_client.confirm_forgot_password(
            ClientId=COGNITO_CLIENT_ID,
            Username=email,
            ConfirmationCode=otp,
            Password="NewTemporaryPassword123!"  # Temporary reset password
        )
        return True
    except ClientError as e:
        return False

# Add a relationship between the main user and the family member in the Neo4j database
def add_family_member_to_db(main_user_id, family_user_id, relationship):
    """
    Add a relationship between the main user and the family member based on the selected relationship type.
    
    Parameters:
    - main_user_id: The ID of the main user
    - family_user_id: The ID of the family member
    - relationship: The type of relationship (Spouse, Child, Parent, Sibling)
    """
    with driver.session() as session:
        if relationship == "Spouse" or relationship == "Sibling":
            # Bi-directional relationship for Spouse or Sibling
            query = """
            MATCH (main:User {user_id: $main_user_id}), (family:User {user_id: $family_user_id})
            CREATE (main)-[:{relationship}]->(family), (family)-[:{relationship}]->(main)
            """.replace("{relationship}", relationship.upper())  # Safely replace relationship with actual value
            session.run(query, main_user_id=main_user_id, family_user_id=family_user_id)
        
        elif relationship == "Parent":
            # Parent-Child relationship
            session.run("""
            MATCH (main:User {user_id: $main_user_id}), (family:User {user_id: $family_user_id})
            CREATE (main)-[:PARENT]->(family), (family)-[:CHILD]->(main)
            """, main_user_id=main_user_id, family_user_id=family_user_id)
        
        elif relationship == "Child":
            # Child-Parent relationship (same as Parent but reverse direction)
            session.run("""
            MATCH (main:User {user_id: $main_user_id}), (family:User {user_id: $family_user_id})
            CREATE (main)-[:CHILD]->(family), (family)-[:PARENT]->(main)
            """, main_user_id=main_user_id, family_user_id=family_user_id)



# Retrieve the list of family members added by the user
def get_family_members(user_id):
    with driver.session() as session:
        result = session.run("""
        MATCH (u:User {user_id: $user_id})-[:HAS_RELATION]->(f:User)
        RETURN f.user_id AS family_user_id, f.email AS family_email, f.name AS family_name
        """, user_id=user_id)

        family_members = result.data()
    return family_members

def remove_family_member_from_db(main_user_id, family_user_id):
    """
    Removes the relationship between the main user and the family member.
    
    Parameters:
    - main_user_id: The user ID of the main user
    - family_user_id: The user ID of the family member to remove
    """
    with driver.session() as session:
        session.run("""
        MATCH (main:User {user_id: $main_user_id})-[r:HAS_RELATION]->(family:User {user_id: $family_user_id})
        DELETE r
        """, main_user_id=main_user_id, family_user_id=family_user_id)
