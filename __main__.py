from Presentation import Presentation_processor

PATH = 'sources/Tests.pptx'


def main():
    presentation_processor = Presentation_processor()
    presentation_processor.open_presentation(PATH)
    presentation_processor.process_presentation()
    presentation_processor.presentation.save('sources/Tests.txt')
    print(presentation_processor.explanations)


if __name__ == "__main__":
    main()
