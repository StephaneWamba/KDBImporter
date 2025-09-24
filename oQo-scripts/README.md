# oQo-scripts

This project meant to automate quantum data hardvesting on many websites.

## 📁 Project Structure
```
oQo-scripts/
├── README.md
├── documents
├── requirements.txt
└── src
    ├── arxiv
    │   └── arxiv.py
    └── main.py
```

## 🚀 Getting Started

Follow these steps to set up the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/oQo-scripts.git
cd oQo-scripts
```

### 2. Create your venv
On Unix or macOS
```bash
python3 -m venv script_venv
source venv/bin/activate
```
---
Or, on Windows
```bash
python -m venv script_venv
script_venv\Scripts\activate
```

### 3. Install the necessary packages

Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/
```bash
pip install -r requirements.txt
```

### 4. Run our script !
```bash
python main_[subname].py
```

## Regarding ArXiv API

### How to build your `search_query`

The core of any bulk import is the `search_query` string. You combine one or more qualifiers with `+AND+` / `+OR+`. Here are all the main field tags supported by the Atom API:

| Qualifier   | Description                                        | Example                                |
|-------------|----------------------------------------------------|----------------------------------------|
| `cat:`      | **Category** (subject class), e.g. `cs.AI`          | `cat:physics.optics`                   |
| `au:`       | **Author** name                                    | `au:"Doe, John"`                       |
| `ti:`       | **Title** text                                     | `ti:"quantum+computing"`               |
| `abs:`      | **Abstract** text                                  | `abs:"deep+learning"`                  |
| `co:`       | **Comments** metadata                              | `co:"invited+talk"`                    |
| `jr:`       | **Journal reference** metadata                     | `jr:"Nature"`                          |
| `all:`      | All of the above fields combined (full‐text)       | `all:"graph+neural+networks"`          |
| _(no tag)_  | Shorthand for `all:`                               | `machine+learning`  

### Regarding post-consume scripts
- They require the installation of OpenAI SDK for python. An open ai key is expected in `OPENAI_API_KEY` environment variable 
- They require a list of authorized tags (names should be insterted already in paperless) in a file `tags.txt` and a list of categories in `categories.txt`
- The txt files should be in a folder for which the path has to be specific in the environment variable `INCLUDE_PATH`
- The post-consume script is `run_post_consume.sh` always remember to set to executable (+x). This should call all other post-processing scripts.





# To Ask
-> Document type (Scientifique paper, pdf, article ?)
-> Correspondant -> What should we fill ?
-> Storage path usefull ? GO empty
-> tags how to fill ?
-> Use of pp workflow to fill custom_fields and other pp data ?

# To Do
-> Implementation NIST NEWS
-> Ne pas ajouter une entry sur la db local si pas recup pdf.
-> NE PAS PARSER APRES LA LAST DATE
-> query non send in paperless from arxiv
-> Implement a solution to not re-upload documents twice, OPTIONNAL, pp check before adding twice
    -> Done for arxiv, but just on a run.
