
# Set folder path containing PDFs
$folder = "F:\Qurisk\test"

# Optional fields (set to $null or leave empty if not used)
$documentType = 8
$addedVia = "Script"
$scope = "Regulatory"
$authors = "MOHAMEDBASSIOUNY"
$source = "ANSSI"

# Run the Python script with arguments
python importfolder2ppl.py `
    "$folder" `
    --document_type $documentType `
    --added_via "$addedVia" `
    --scope "$scope" `
    --authors "$authors" `
    --source "$source"