import pandas as pd
import os


def create_grade_report(report_folder):
    '''
    Функция принимает значение папки с выгрузками, для выгрузок значение grade_report
    Функция объединяет все выгрузки в папке и оставляет только выбранные столбцы
    '''
    all_data = pd.DataFrame()
    reports_directory = os.path.join(os.getcwd(), report_folder)
    directions = os.walk(reports_directory)
    for address, dirc, files in directions:
        for file in files:
            data = pd.read_csv(os.path.join(address, file))
            if file.split("_")[1] == 'MISIS':
                data["course_name"] = 'MISIS_26'
            elif file.split("_")[1] == 'N':
                data["course_name"] = 'N_CHTHER'
            else:
                data["course_name"] = file.split("_")[1]
            all_data = pd.concat([all_data, data])
    columns_to_drop = []
    for i in range(8, len(all_data.columns)):         # первые 8 столбцов не трогаем
        columns_to_drop.append(i)
    # остальные столбцы которые не трогаем    
    columns_to_drop.remove(all_data.columns.get_loc("course_name"))
    columns_to_drop.remove(all_data.columns.get_loc("Cohort Name"))
    columns_to_drop.remove(all_data.columns.get_loc("Exam Statuses"))
    columns_to_drop.remove(all_data.columns.get_loc("Video Links"))
    columns_to_drop.remove(all_data.columns.get_loc("Review Comments"))
    columns_to_drop.remove(all_data.columns.get_loc("Final Exam (Avg)"))
    columns_to_drop.remove(all_data.columns.get_loc("Completion Percentage"))
    columns_to_drop.remove(all_data.columns.get_loc("Certificate Eligible")) 
    columns_to_drop.remove(all_data.columns.get_loc("Certificate Delivered")) 
    columns_to_drop.remove(all_data.columns.get_loc("Enrollment Track")) 
    all_data = all_data.drop(all_data.columns[columns_to_drop], axis=1)
    all_data.to_csv(os.path.join(os.getcwd(),report_folder + '.csv'), index=False)
