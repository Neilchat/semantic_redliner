from tika import parser


class TikaParser:

    def get_text(self, path):

        parsed_pdf = parser.from_file(path)

        data = parsed_pdf['content']

        return data
