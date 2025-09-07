import requests

# =================== Configuration ===================
BASE_URL = "https://api.preview.platform.athenahealth.com"
PRACTICE_ID = "195900"  # replace with your practice ID

CLIENT_ID = "0oaz0ptoc0UIw3xf0297"
CLIENT_SECRET = "vTG6wGiWIjvfPZpLun5RmtnJ0XY8dhioXEoeilLVL65TzMGZpzqkzRzgKTJ5LhMa"
SCOPE = "athena/service/Athenanet.MDP.*"  # your app's scope

# =================== Functions ===================

def get_token():
    url = f"{BASE_URL}/oauth2/v1/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": SCOPE,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(url, data=payload, headers=headers)
    if resp.status_code != 200:
        print("Status:", resp.status_code)
        print("Response:", resp.text)
        resp.raise_for_status()
    token = resp.json()["access_token"]
    print("✅ Got Access Token")
    return token


def get_departments(token):
    url = f"{BASE_URL}/v1/{PRACTICE_ID}/departments"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    departments = data.get("departments", [])
    if not departments:
        raise ValueError("No departments found")
    departmentid = departments[0]["departmentid"]
    print(f"✅ Using Department ID: {departmentid}")
    return departmentid


def get_patients(token, lastname):
    """Search patients by lastname only to avoid DOB issues."""
    url = f"{BASE_URL}/v1/{PRACTICE_ID}/patients"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"lastname": lastname}

    try:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        print("❌ HTTP Error:", e)
        print(resp.text)
        return None


def add_patient(token, firstname, lastname, dob, departmentid, gender="M", mobilephone="1111111111"):
    """Add a new patient with proper JSON payload."""
    url = f"{BASE_URL}/v1/{PRACTICE_ID}/patients"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "firstname": firstname,
        "lastname": lastname,
        "dob": dob,  # string in YYYY-MM-DD format
        "departmentid": departmentid,
        "gender": gender,
        "mobilephone": mobilephone
    }

    try:
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        patient = resp.json()
        print("✅ Added Patient:", patient)
        return patient
    except requests.exceptions.HTTPError as e:
        print("❌ Failed to add patient:", e)
        print(resp.text)
        return None


def process_patients(token, departmentid, patient_list):
    """Process list of patients: check and add if not found."""
    for p in patient_list:
        firstname = p.get("firstname")
        lastname = p.get("lastname")
        dob = p.get("dob")
        gender = p.get("gender", "M")
        mobilephone = p.get("mobilephone", "1111111111")

        patients = get_patients(token, lastname)
        if patients and patients.get("patients"):
            print(f"✅ Patient exists: {firstname} {lastname}")
        else:
            print(f"ℹ️ Adding patient: {firstname} {lastname}")
            add_patient(token, firstname, lastname, dob, departmentid, gender, mobilephone)


# =================== Main ===================
if __name__ == "__main__":
    token = get_token()
    departmentid = get_departments(token)

    # Sample patients
    patient_list = [
        {"firstname": "John", "lastname": "Doe", "dob": "1990-01-01", "gender": "M", "mobilephone": "1111111111"},
        {"firstname": "Jane", "lastname": "Smith", "dob": "1985-05-12", "gender": "F", "mobilephone": "2222222222"},
        {"firstname": "Alice", "lastname": "Brown", "dob": "2000-03-15", "gender": "F", "mobilephone": "3333333333"},
    ]

    process_patients(token, departmentid, patient_list)
