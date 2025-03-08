from llmsherpa.readers import LayoutPDFReader

llmsherpa_api_url = "http://localhost:5010/api/parseDocument?renderFormat=all"

def get_structure(path):
    pdf_reader = LayoutPDFReader(llmsherpa_api_url)
    doc = pdf_reader.read_pdf(path)
    return doc

