from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

# Initialize the Selenium WebDriver
driver = webdriver.Chrome()

# LinkedIn credentials
username = '' 
password = ''

# LinkedIn login URL
login_url = 'https://www.linkedin.com/login'

# Open LinkedIn login page
driver.get(login_url)
time.sleep(2)

# Enter username
username_input = driver.find_element(By.ID, 'username')
username_input.send_keys(username)

# Enter password
password_input = driver.find_element(By.ID, 'password')
password_input.send_keys(password)

# Click login button
login_button = driver.find_element(By.XPATH, '//*[@type="submit"]')
login_button.click()
time.sleep(5)

# Navigate to a LinkedIn profile
profile_url = 'https://www.linkedin.com/in/arif-ul-islam-716517149/'
driver.get(profile_url)
time.sleep(5)

# Get page source and parse with BeautifulSoup
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

# Extract profile information
main_text = soup.find('main')

# Ensure main_text is not None
if main_text:
    main_text = str(main_text)
else:
    main_text = ""

profile_section = soup.find("section", class_="pv-profile-card")
target_ids = {"licenses_and_certifications", "about", "experience", "projects", "skills", "publications"}  # add more target ids if needed
# Initialize a dictionary to store full sections for each target id
filtered_sections = {tid: [] for tid in target_ids}

# Find all sections that might contain profile information
profile_sections = soup.find_all("section", class_="pv-profile-card")

# Loop through each section and check if any descendant has one of the target ids.
for sec in profile_sections:
    for tid in target_ids:
        if sec.find(id=tid):  # if any element within the section has the target id
            # Extract the full section's text
            filtered_sections[tid].append(sec.get_text(separator="\n", strip=True))
            break  # Stop after the first match in this section

# Combine the extracted sections into one text block for the LLM
combined_entries = []
seen = set()
for tid, sections in filtered_sections.items():
    for idx, text in enumerate(sections):
        entry = f"{tid} (instance {idx+1}):\n{text}"
        if entry not in seen:
            combined_entries.append(entry)
            seen.add(entry)
combined_text = "\n\n".join(combined_entries)

system = SystemMessagePromptTemplate.from_template("""You are an AI Assistant. 
                                                   You will be given extracted content. 
                                                   Your task is to find the insightful information of the user from that extracted content. 
                                                   Write and summerize in broard about the user such as the user's name, headline, current position, education, and any other relevant profile information. 
                                                   Ignore unrelated data such as suggestions, likes, comments, and interests.
""")

human = HumanMessagePromptTemplate.from_template("Here is the extracted content: {html_source}")

template = ChatPromptTemplate([system, human])

model = ChatOllama(base_url="http://localhost:11434", model='llama3.2:latest')

chain = template | model | StrOutputParser()

# Generate a response
response = chain.invoke({"html_source": combined_text})

print(response)

# Close the WebDriver
driver.quit()