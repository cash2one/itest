import csv
from apiget.models import TestInfos
reader = csv.reader(file('testinfo','rb'))
for line in reader:
    if line[0]=='season':
        continue
    if line[0]:
        TestInfos(quarter=line[0], group=line[1], bugs_found=int(line[2]), bugs_found_p1=int(line[3]),
                  bugs_escape=int(line[4]), bugs_escape_noduty=int(line[5]), bugs_escape_p1=int(line[6]),
                  allow_tests=int(line[7]), allow_tests_pass=int(line[8]), bugs_found_function=int(line[9]),
                  bugs_found_function_p1=int(line[10]), bugs_other=int(line[11]), bugs_other_p1=int(line[12]),
                  bugs_escape_info=line[13], t_id=line[14], bugs_escape_p1_noduty=int(line[15])).save()