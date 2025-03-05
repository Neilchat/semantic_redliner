from llmsherpa.readers import LayoutPDFReader

llmsherpa_api_url = "http://localhost:5010/api/parseDocument?renderFormat=all"

def get_structure(path):
    pdf_reader = LayoutPDFReader(llmsherpa_api_url)
    doc = pdf_reader.read_pdf(path)
    return doc

if __name__ == "__main__":
    get_structure("/Users/saswata/Documents/semantic_redliner/src/main/python/data/Jan 2015.pdf")