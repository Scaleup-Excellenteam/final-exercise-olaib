from flask import json
from pptx import Presentation


#
#
# # ============================== STATIC FUNCS================================
# def extract_text_from_slide(slide):
#     slide_text = ""
#     for shape in slide.shapes:
#         if shape.has_text_frame:
#             for paragraph in shape.text_frame.paragraphs:
#                 for run in paragraph.runs:
#                     slide_text += run.text
#                     slide_text += " ."  # Space between paragraphs
#     return slide_text
#
#
# # ========================== PPTX-PROCESSOR ====================================
# class PptxProcessor:
#     """Processes pptx file and extracts slides"""
#
#     def __init__(self, path: str):
#         """Initializes pptx processor
#         :param path: path to pptx file
#         """
#         self.slides = []
#         self.explanations = []
#         self.file_name = path.split("\\")[-1]
#         self.presentation = Presentation(path)
#
#     def process_presentation(self):
#         for slide_num, slide in enumerate(self.presentation.slides):
#             slide_text = self.extract_text_from_slide(slide)
#             self.slides.append(slide_text)
#
#     def extract_text_from_slide(self, slide):
#         slide_text = ""
#         for shape in slide.shapes:
#             if shape.has_text_frame:
#                 for paragraph in shape.text_frame.paragraphs:
#                     for run in paragraph.runs:
#                         slide_text += run.text
#                         slide_text += " ."  # Space between paragraphs
#         return slide_text
#
#     def get_slide(self, slide_num) -> str:
#         return self.slides[slide_num - 1]
#
#     def get_slides(self) -> list:
#         return self.slides
#
#     def get_slide_text(self, slide_num) -> str:
#         return self.slides[slide_num - 1]
#
#     def save_explanations(self):
#         """Saves explanations to json file"""
#         data = {}
#         for i, explanation in enumerate(self.explanations):
#             slide_number = i + 1
#             data[slide_number] = explanation
# # class Pptx_processor:
# #     """Processes pptx file and extracts slides and save explanations to json file"""
# #
# #     def __init__(self, path: str):
# #         """Initializes pptx processor
# #         :param path: path to pptx file
# #         """
# #         self.slides = []
# #         self.explanations = []
# #         self.file_name = path.split("\\")[-1]
# #         self.presentation = Presentation(path)
# #
# #     def process_presentation(self):
# #         for slide_num, slide in enumerate(self.presentation.slides):
# #             slide_text = extract_text_from_slide(slide)
# #             self.slides.append(slide_text)
# #
# #     def get_slide(self, slide_num) -> str:
# #         return self.slides[slide_num - 1]
# #
# #     def get_slides(self) -> list:
# #         return self.slides
# #
# #     def get_slide_text(self, slide_num) -> str:
# #         return self.slides[slide_num - 1]
# #
# #     def save_explanations(self):
# #         """Saves explanations to json file
# #         :param output_file: path to output file
# #         """
# #         data = {}
# #         for i, explanation in enumerate(self.explanations):
# #             slide_number = i + 1
# #             data[slide_number] = explanation
# #
# #         with open(f"explanations_{self.file_name}.json", "w") as file:
# #             json.dump(data, file, indent=4)
# #         logging.info(f"Explanations saved successfully to explanations_{self.file_name}")
class PptxProcessor:
    """Parser class for extracting text from PowerPoint slides."""

    def __init__(self, path: str):
        """Initialize the PptxParser with the path to the PowerPoint file."""
        self.path = path
        self.file_name = path.split("/")[-1].split(".")[0]
        self.slides = self.extract_text_from_presentation()

    def extract_text_from_presentation(self):
        """Extract text from all slides in the presentation."""
        presentation = Presentation(self.path)
        slides_text = []
        for slide in presentation.slides:
            slide_text = self.extract_text_from_slide(slide)
            slides_text.append(slide_text)
        return slides_text

    def get_slide(self, slide_num) -> str:
        return self.slides[slide_num - 1]

    def get_slides(self) -> list:
        return self.slides

    @staticmethod
    def extract_text_from_slide(slide):
        """Extract text from a single slide."""
        slide_text = ""
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        slide_text += run.text
                        slide_text += " ."  # Space between paragraphs
        return slide_text

    def save_explanations_as_json(self, explanations):
        """Save explanations as a json file."""
        data = {}
        for i, explanation in enumerate(explanations):
            slide_number = i + 1
            data[slide_number] = explanation

        with open(f"explanations_{self.file_name}.json", "w") as file:
            json.dump(data, file, indent=4)

