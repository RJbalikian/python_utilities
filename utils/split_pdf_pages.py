def split_pdf_pages(input_pdf, output_pdf=None, start_page=None, end_page=None):
    """Function to split PDF pages in half down the middle (used for notes sheets with two pages on a single sheet). Uses PyMuPDF library.

    Parameters
    ----------
    input_pdf : pathlike object
        Filepath to document that will be cropped
    output_pdf : pathlike object
        Filepath to output document
    start_page : int
        First page that will be cropped. Defaults to first page of document.
    end_page : int
        Last page that will be cropped. Defaults to end of document
        
    Returns
    -------
    pymupdf.Document
    """
    import pymupdf  # PyMuPDF
    import pathlib
    
    # Open the input PDF
    pdf_document = pymupdf.open(input_pdf)
    output_document = pymupdf.open()


    if start_page is None:
        start_page = 1
        
    if end_page is None:
        end_page = len(output_document)-1
        
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        if start_page - 1 <= page_num <= end_page - 1:
            output_document.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
            output_document.fullcopy_page(len(output_document)-1)
            
            page_rect = page.rect
            
            # Split the page into left and right halves
            left_rect = pymupdf.Rect(page_rect.x0, page_rect.y0, page_rect.x1 / 2, page_rect.y1)
            right_rect = pymupdf.Rect(page_rect.x1 / 2, page_rect.y0, page_rect.x1, page_rect.y1)

            output_document[-2].set_cropbox(left_rect)
            output_document[-1].set_cropbox(right_rect)

        else:
            output_document.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)

    # Save the output PDF
    if output_pdf is None:
        output_pdf = pathlib.Path(input_pdf).with_stem(pathlib.Path(input_pdf).stem + '_cropped')
    output_document.save(output_pdf)
    output_document.close()
    pdf_document.close()
    
    return output_document
