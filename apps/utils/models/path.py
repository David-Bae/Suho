import os

#####################################################################################
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)

#! PDF를 만드는데 필요한 파일 (절대주소 사용)
PDF_RESOURCE_DIR = os.path.join(current_directory, 'pdfResources')

#! 생성된 보고서를 저장하는 폴더 (절대주소 사용)
REPORT_DIR = '/usr/src/suho_data/report'
#####################################################################################

print(current_directory)