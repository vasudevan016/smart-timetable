import os
import re
import json
import fitz  # PyMuPDF

pdf_files = {
    "CP_DLD_OCW": ["cp_sec1.pdf", "cp_sec2.pdf", "cp_sec3.pdf", "cp_sec4.pdf"],
    "DSMA": ["dsma_sec1.pdf", "dsma_sec2.pdf", "dsma_sec3.pdf", "dsma_sec4.pdf", "dsma_sec5.pdf"],
    "EE": ["ee_sec1.pdf", "ee_sec2.pdf"],
    "EDL": ["edl_sec1.pdf", "edl_sec2.pdf"]
}

student_db = {}

for course, files in pdf_files.items():
    for filename in files:
        filepath = os.path.join("data", filename)
        
        if not os.path.exists(filepath):
            continue
            
        section_match = re.search(r'sec(\d)', filename.lower())
        section = f"Sec{section_match.group(1)}" if section_match else "Unknown"

        try:
            doc = fitz.open(filepath)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            words = text.split()
            
            for i, word in enumerate(words):
                if "@iiits.in" in word.lower():
                    email = word.lower().strip()
                    
                    if email not in student_db:
                        student_db[email] = {
                            "Name": None,
                            "Roll": None,
                            "Branch": None,
                            "Sections": {}
                        }
                    
                    # Scan ahead up to 25 words to find the Roll Number
                    for j in range(1, 25):
                        if i + j < len(words):
                            check_word = words[i+j].upper()
                            
                            # Lock onto the Roll Number
                            if re.match(r'^S202\d+', check_word):
                                if not student_db[email]["Roll"]:
                                    student_db[email]["Roll"] = check_word
                                
                                # Extract Name ONLY if we haven't grabbed it successfully yet
                                if not student_db[email]["Name"]:
                                    raw_name_words = words[i+1 : i+j]
                                    
                                    # Clean out the garbage (digits, '|', etc.)
                                    clean_name = [w for w in raw_name_words if not re.match(r'^[\d\|]+$', w) and w != '|']
                                    
                                    if clean_name:
                                        student_db[email]["Name"] = " ".join(clean_name).title()
                            
                            # Lock onto the Branch
                            if check_word in ["ECE", "CSE", "AI&DS", "AIDS"] and not student_db[email]["Branch"]:
                                student_db[email]["Branch"] = check_word
                    
                    student_db[email]["Sections"][course] = section
                    
        except Exception as e:
            pass

# Export the compiled database
with open('students.json', 'w') as f:
    json.dump(student_db, f, indent=4)
