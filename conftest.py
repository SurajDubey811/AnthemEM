# import time
# from datetime import datetime
# import pytest
# from py.xml import html
#
#
# @pytest.hookimpl()
# def pytest_cmdline_preparse(config):
#     timestr = time.strftime("%d-%m-%Y - %H%M%S")
#     config.option.htmlpath = "reports/AnthemEM-Test report "+timestr+".html"
#     config.option.self_contained_html = True
#
#
# def pytest_html_report_title(report):
#     """ modifying the title  of html report"""
#     timestr = time.strftime("%d-%m-%Y - %H:%M:%S")
#     report.title = "AnthemEM: Test report "+timestr+".html"
#
#
# def pytest_html_results_table_header(cells):
#     ''' meta programming to modify header of the result'''
#
#     # removing old table headers
#     # adding new headers
#     cells.pop()
#     del cells[0]
#     cells.insert(0, html.th('Time', class_="sortable Time initial-sort asc active", col='Time'))
#     cells.insert(1, html.th('Test ID'))
#     cells.insert(2, html.th('Test Description'))
#     # del cells[3]
#     cells[3] = html.th("Result", class_="sortable Result active")
#     cells.insert(4, html.th("Test Case path"))
#     cells[5] = html.th("Duration", class_="sortable Duration active")
#     # cells.insert(5, html.th("Duration", class_="sortable Duration active"))
#
#
# def pytest_html_results_table_row(report, cells):
#     """ orienting the data gotten from  pytest_runtest_makereport
#     and sending it as row to the result """
#     cells.insert(0, html.td(datetime.now().strftime('%d-%m-%Y %H:%M:%S'), class_='col-time'))
#     cells.insert(1, html.td(report.id, class_="col-TestID"))
#     cells.insert(2, html.td(report.testcase, class_="col-TestDesc"))
#     cells[4] = html.td(report.nodeid, class_="col-Test Case path")
#     cells[5] = html.td(round(report.duration, 2), class_="col-Duration")
#
#
# @pytest.hookimpl(hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     """data from the output of pytest gets processed here
#      and are passed to pytest_html_results_table_row"""
#     outcome = yield
#     # this is the output that is seen end of test case
#     report = outcome.get_result()
#     # taking doc string of the string
#     testDesc = str(item.function.__doc__)
#     # name of the function
#     # test_case_name = str(item.function.__name__)
#     report.id = testDesc.split()[0]
#     testDesc = " ".join(item for item in testDesc.split()[1:])
#     report.tcpath = str(item.function)
#     report.testcase = f"{testDesc}"
#     report.outcome = report.outcome
#     report.nodeid = report.nodeid
#     report.duration = report.duration
#
