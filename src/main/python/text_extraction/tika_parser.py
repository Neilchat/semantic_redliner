from tika import parser


class TikaParser:

    def get_text(self, path):
        parsed_pdf = parser.from_file(path)

        # saving content of pdf
        # you can also bring text only, by parsed_pdf['text']
        # parsed_pdf['content'] returns string
        data = parsed_pdf['content']

        # Printing of content
        return data

if __name__ == "__main__":
    p = TikaParser()
    text = p.get_text("/Users/saswata/Documents/semantic_redliner/src/main/python/data/Jan 2015.docx")
    print(len(text.split(" ")))
